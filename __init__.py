"""Hermes Loop plugin — registration.

Provides continuous task execution loop with state persistence and completion promises."""

import json
import logging
from pathlib import Path

from . import commands, schemas, tools

logger = logging.getLogger(__name__)


def _on_post_tool_call(tool_name: str, args: dict, result: str, task_id: str, **kwargs):
    """Hook: runs after every tool call to log loop-related tool usage."""
    loop_tools = ['loop_status', 'set_completion_promise', 'init_loop',
                  'complete_task', 'add_blocking_issue', 'reset_loop']
    if any(t in tool_name for t in loop_tools):
        logger.debug("[hermes-loop] tool=%s session=%s", tool_name, task_id)


def _on_session_start(session_id: str, model: str, platform: str, **kwargs):
    """Hook: runs once when a new session is created (first turn only)."""
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
                "[hermes-loop] Resuming loop (session %s): %d/%d tasks complete",
                session_id, completed_tasks, total_tasks,
            )
    except Exception as e:
        logger.error("[hermes-loop] Error in on_session_start hook: %s", e)


def _on_pre_llm_call(session_id: str, user_message: str, conversation_history: list,
                     is_first_turn: bool, model: str, platform: str, **kwargs) -> dict:
    """Hook: runs before each LLM turn to inject loop state as system context.

    Returns {"context": ...} to append guidance to the ephemeral system prompt,
    which is the hermes-supported way to influence loop continuation.
    """
    cwd = kwargs.get('cwd', str(Path.cwd()))
    state_file_path = Path(cwd) / '.hermes-loop-state.json'

    if not state_file_path.exists():
        return

    try:
        with open(state_file_path) as f:
            state = json.load(f)

        total_tasks = state.get('total_tasks', 0)
        completed_tasks = state.get('completed_tasks', 0)
        blocking_issues = state.get('blocking_issues', [])
        completion_promise = state.get('completion_promise')

        if blocking_issues:
            return {
                "context": (
                    f"[HERMES-LOOP] The loop is BLOCKED and cannot continue. "
                    f"Blocking issues: {blocking_issues}. "
                    "Stop work, report these issues to the user, and do not attempt further tasks."
                )
            }

        # Check completion promise fulfillment
        promise_status = ""
        if completion_promise and not completion_promise.get('fulfilled', False):
            promise_type = completion_promise.get('promise_type', '')
            condition = completion_promise.get('condition', '')
            promise_fulfilled = False

            if promise_type == 'task_count':
                expected = int(completion_promise.get('expected_value', 0))
                promise_fulfilled = completed_tasks >= expected
            elif promise_type == 'file_exists':
                promise_fulfilled = (Path(cwd) / condition).exists()
            elif promise_type == 'content_match':
                check_path = Path(cwd) / condition
                if check_path.exists():
                    pattern = completion_promise.get('expected_value', '')
                    promise_fulfilled = pattern in check_path.read_text()

            if promise_fulfilled:
                completion_promise['fulfilled'] = True
                with open(state_file_path, 'w') as f:
                    json.dump(state, f, indent=2)
                promise_status = (
                    f" Completion promise ({promise_type}: {condition}) is NOW FULFILLED."
                    " Wrap up and summarize results."
                )
            else:
                promise_status = (
                    f" Completion promise ({promise_type}: {condition}) not yet met — keep working."
                )

        if completed_tasks >= total_tasks:
            return {
                "context": (
                    f"[HERMES-LOOP] All {total_tasks} tasks are complete.{promise_status} "
                    "Summarize what was accomplished and wrap up."
                )
            }

        remaining = total_tasks - completed_tasks
        return {
            "context": (
                f"[HERMES-LOOP] Loop active: {completed_tasks}/{total_tasks} tasks complete "
                f"({remaining} remaining).{promise_status} Continue with the next task."
            )
        }

    except Exception as e:
        logger.error("[hermes-loop] Error in pre_llm_call hook: %s", e)


def _on_session_end(session_id: str, completed: bool, interrupted: bool,
                    model: str, platform: str, **kwargs):
    """Hook: runs at the end of every run_conversation call."""
    cwd = kwargs.get('cwd', str(Path.cwd()))
    state_file_path = Path(cwd) / '.hermes-loop-state.json'

    if not state_file_path.exists():
        return

    try:
        with open(state_file_path) as f:
            state = json.load(f)

        completed_tasks = state.get('completed_tasks', 0)
        total_tasks = state.get('total_tasks', 0)
        logger.info(
            "[hermes-loop] Session %s ended (completed=%s interrupted=%s): %d/%d tasks",
            session_id, completed, interrupted, completed_tasks, total_tasks,
        )
    except Exception as e:
        logger.error("[hermes-loop] Error in on_session_end hook: %s", e)


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
    
    # Register lifecycle hooks
    ctx.register_hook("post_tool_call", _on_post_tool_call)
    ctx.register_hook("on_session_start", _on_session_start)
    ctx.register_hook("pre_llm_call", _on_pre_llm_call)
    ctx.register_hook("on_session_end", _on_session_end)

    logger.info("[hermes-loop] Plugin registered with 6 tools and 4 hooks")
