"""Hermes Loop plugin — registration.

Provides continuous task execution loop with state persistence and completion promises.
"""

import json
import logging
from pathlib import Path

from . import commands, schemas, tools

logger = logging.getLogger(__name__)


def _on_post_tool_call(tool_name: str, args: dict, result: str, task_id: str, **kwargs):
    """Hook: runs after every tool call to check loop continuation."""
    
    # Only process if this is a loop-related tool or we're in a loop session
    loop_tools = ['loop_status', 'set_completion_promise', 'init_loop', 
                  'complete_task', 'add_blocking_issue', 'reset_loop']
    
    if not any(t in tool_name for t in loop_tools):
        return
    
    cwd = kwargs.get('cwd', str(Path.cwd()))
    state_file_path = Path(cwd) / '.hermes-loop-state.json'
    
    # Check if we have an active state file
    if not state_file_path.exists():
        return
    
    try:
        with open(state_file_path) as f:
            state = json.load(f)
        
        total_tasks = state.get('total_tasks', 0)
        completed_tasks = state.get('completed_tasks', 0)
        blocking_issues = state.get('blocking_issues', [])
        
        # If all tasks complete, signal loop end
        if completed_tasks >= total_tasks and not blocking_issues:
            logger.info(f"[hermes-loop] All {total_tasks} tasks completed at session {task_id}")
            
            # Add completion marker to transcript for detection by stop hook
            transcript_path = kwargs.get('transcript_path')
            if transcript_path:
                try:
                    with open(transcript_path, 'a') as f:
                        f.write(f"\n# [HERMES-LOOP] ALL_TASKS_COMPLETE at {task_id}\n")
                except Exception as e:
                    logger.error(f"Failed to write completion marker: {e}")
                    
    except Exception as e:
        logger.error(f"[hermes-loop] Error in post_tool_call hook: {e}")


def _on_session_start(session_id: str, platform: str, **kwargs):
    """Hook: runs when a new session starts."""
    
    cwd = kwargs.get('cwd', str(Path.cwd()))
    state_file_path = Path(cwd) / '.hermes-loop-state.json'
    
    if not state_file_path.exists():
        return
    
    try:
        with open(state_file_path) as f:
            state = json.load(f)
        
        total_tasks = state.get('total_tasks', 0)
        completed_tasks = state.get('completed_tasks', 0)
        
        if total_tasks > 0 and completed_tasks < total_tasks:
            logger.info(
                f"[hermes-loop] Resuming loop from session {session_id}: "
                f"{completed_tasks}/{total_tasks} tasks complete"
            )
            
    except Exception as e:
        logger.error(f"[hermes-loop] Error in on_session_start hook: {e}")


def _on_stop_hook(input_data: dict, **kwargs) -> int:
    """Hook: determines if loop should continue or stop.
    
    Returns 0 to continue, non-zero to stop.
    This is the main loop controller."""
    
    cwd = input_data.get('cwd', str(Path.cwd()))
    transcript_path = input_data.get('transcript_path')
    
    state_file_path = Path(cwd) / '.hermes-loop-state.json'
    
    # If no state file, nothing to continue
    if not state_file_path.exists():
        return 0
    
    try:
        with open(state_file_path) as f:
            state = json.load(f)
        
        total_tasks = state.get('total_tasks', 0)
        completed_tasks = state.get('completed_tasks', 0)
        blocking_issues = state.get('blocking_issues', [])
        completion_promise = state.get('completion_promise')
        
        # Check for explicit ALL_TASKS_COMPLETE in transcript (backup detection)
        if transcript_path and Path(transcript_path).exists():
            with open(transcript_path) as f:
                content = f.read()
                if 'ALL_TASKS_COMPLETE' in content:
                    logger.info("[hermes-loop] Detected ALL_TASKS_COMPLETE marker")
                    return 1  # Stop
        
        # Check blocking issues first
        if blocking_issues:
            logger.warning(
                f"[hermes-loop] Blocking issues detected, stopping loop: {blocking_issues}"
            )
            return 1
        
        # Check completion promise
        if completion_promise and not completion_promise.get('fulfilled', False):
            promise_type = completion_promise.get('promise_type', '')
            condition = completion_promise.get('condition', '')
            
            # Evaluate the promise condition
            promise_fulfilled = False
            
            if promise_type == 'task_count':
                expected = int(completion_promise.get('expected_value', 0))
                promise_fulfilled = completed_tasks >= expected
                
            elif promise_type == 'file_exists':
                check_path = Path(cwd) / condition
                promise_fulfilled = check_path.exists()
                
            elif promise_type == 'content_match':
                check_path = Path(cwd) / condition
                if check_path.exists():
                    content = check_path.read_text()
                    pattern = completion_promise.get('expected_value', '')
                    promise_fulfilled = pattern in content
            
            # Update fulfilled status
            if promise_fulfilled:
                completion_promise['fulfilled'] = True
                with open(state_file_path, 'w') as f:
                    json.dump(state, f, indent=2)
            
            if not promise_fulfilled:
                logger.info(
                    f"[hermes-loop] Completion promise not yet fulfilled "
                    f"({promise_type}: {condition}), continuing loop"
                )
                return 0
        
        # Check if all tasks complete
        if completed_tasks >= total_tasks:
            logger.info(f"[hermes-loop] All {total_tasks} tasks completed, stopping loop")
            return 1
        
        # Continue the loop
        logger.debug(
            f"[hermes-loop] Continuing loop: {completed_tasks}/{total_tasks} tasks complete"
        )
        
    except Exception as e:
        logger.error(f"[hermes-loop] Error in stop hook: {e}")
    
    return 0  # Default to continue on error


def register(ctx):
    """Register tools and hooks with Hermes Agent."""
    
    # Core loop status tool
    ctx.register_tool(
        name="loop_status",
        toolset="hermes-loop",
        schema=schemas.LOOP_STATUS,
        handler=tools.loop_status
    )
    
    # Completion promise tool
    ctx.register_tool(
        name="set_completion_promise",
        toolset="hermes-loop",
        schema=schemas.COMPLETE_PROMISE,
        handler=tools.set_completion_promise
    )
    
    # Command-style tools for easier usage
    ctx.register_tool(
        name="init_loop",
        toolset="hermes-loop",
        schema={
            "name": "init_loop",
            "description": (
                "Initialize a new loop state. Creates the state file and sets up task tracking."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "total_tasks": {
                        "type": "integer",
                        "description": "Total number of tasks in the loop"
                    },
                    "promise_type": {
                        "type": "string", 
                        "description": "Optional completion promise type (task_count, file_exists, content_match)"
                    },
                    "condition": {
                        "type": "string",
                        "description": "Path/pattern for the promise"
                    },
                    "expected_value": {
                        "type": "string",
                        "description": "Expected value for content_match promises"
                    }
                },
                "required": ["total_tasks"]
            }
        },
        handler=tools.init_loop
    )
    
    # Command-style tools (aliases for easier usage)
    ctx.register_tool(
        name="complete_task",
        toolset="hermes-loop", 
        schema={
            "name": "complete_task",
            "description": (
                "Mark next task as completed. Increments the completed tasks counter."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        handler=tools.complete_task
    )
    
    ctx.register_tool(
        name="add_blocking_issue",
        toolset="hermes-loop",
        schema={
            "name": "add_blocking_issue", 
            "description": (
                "Add a blocking issue. When issues block progress, the loop will stop automatically."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "issue": {
                        "type": "string",
                        "description": "Description of the blocking issue"
                    }
                },
                "required": ["issue"]
            }
        },
        handler=tools.add_blocking_issue
    )
    
    ctx.register_tool(
        name="reset_loop",
        toolset="hermes-loop",
        schema={
            "name": "reset_loop",
            "description": (
                "Reset loop state. Clears completed task count but keeps total tasks and promise."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        handler=tools.reset_loop
    )
    
    # Register hooks for loop continuation control
    ctx.register_hook("post_tool_call", _on_post_tool_call)
    ctx.register_hook("on_session_start", _on_session_start)
    ctx.register_hook("stop_hook", _on_stop_hook)
    
    logger.info("[hermes-loop] Plugin registered with 6 tools and 3 hooks")
