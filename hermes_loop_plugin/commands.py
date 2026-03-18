"""Command-style wrappers for hermes-loop tools.

These provide more intuitive, slash-command-like interfaces to the loop functionality."""

import json
from pathlib import Path


class LoopCommands:
    """Convenience class providing command-style access to loop operations."""
    
    def __init__(self):
        self.state_file = Path.cwd() / '.hermes-loop-state.json'
    
    def init_loop(self, total_tasks: int, promise_type: str = None, 
                  condition: str = None, expected_value: str = None) -> dict:
        """Initialize a new loop state.
        
        Args:
            total_tasks: Total number of tasks in the loop
            promise_type: Optional completion promise type (task_count, file_exists, content_match)
            condition: Path/pattern for the promise
            expected_value: Expected value for content_match promises
            
        Returns:
            dict with initialization status
        """
        state = {
            "total_tasks": total_tasks,
            "completed_tasks": 0,
            "blocking_issues": [],
            "created_at": None
        }
        
        if promise_type:
            state["completion_promise"] = {
                "promise_type": promise_type,
                "condition": condition,
                "expected_value": expected_value,
                "fulfilled": False
            }
        else:
            state["completion_promise"] = None
        
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)
        
        return {
            "success": True,
            "message": f"Loop initialized with {total_tasks} tasks",
            "state_file": str(self.state_file),
            "promise_set": bool(promise_type)
        }
    
    def complete_task(self) -> dict:
        """Mark one task as completed.
        
        Returns:
            dict with updated state
        """
        if not self.state_file.exists():
            return {
                "success": False,
                "error": "No active loop state found"
            }
        
        try:
            with open(self.state_file) as f:
                state = json.load(f)
            
            old_count = state['completed_tasks']
            state['completed_tasks'] += 1
            
            # Track completion history if this is the first task
            if state['completed_tasks'] == 1 and 'completion_history' not in state:
                state['completion_history'] = []
            
            if 'completion_history' in state:
                from datetime import datetime
                state['completion_history'].append({
                    "task_index": state['completed_tasks'],
                    "timestamp": datetime.now().isoformat()
                })
            
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
            
            return {
                "success": True,
                "previous_count": old_count,
                "new_count": state['completed_tasks'],
                "total_tasks": state['total_tasks'],
                "remaining": state['total_tasks'] - state['completed_tasks']
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def set_promise(self, promise_type: str, condition: str = None, 
                    expected_value: str = None) -> dict:
        """Set or update the completion promise.
        
        Args:
            promise_type: Type of promise (task_count, file_exists, content_match)
            condition: Path/pattern for the promise
            expected_value: Expected value for content_match promises
            
        Returns:
            dict with promise status
        """
        if not self.state_file.exists():
            return {
                "success": False,
                "error": "No active loop state found"
            }
        
        try:
            with open(self.state_file) as f:
                state = json.load(f)
            
            promise = {
                "promise_type": promise_type,
                "condition": condition,
                "expected_value": expected_value,
                "fulfilled": False
            }
            
            state['completion_promise'] = promise
            
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
            
            return {
                "success": True,
                "promise_type": promise_type,
                "message": f"Promise set via {promise_type}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def add_blocking_issue(self, issue: str) -> dict:
        """Add a blocking issue that will stop the loop.
        
        Args:
            issue: Description of the blocking issue
            
        Returns:
            dict with update status
        """
        if not self.state_file.exists():
            return {
                "success": False,
                "error": "No active loop state found"
            }
        
        try:
            with open(self.state_file) as f:
                state = json.load(f)
            
            if issue not in state['blocking_issues']:
                state['blocking_issues'].append(issue)
                
                # Add timestamp for tracking
                if 'issues' not in state:
                    from datetime import datetime
                    state['issues'] = []
                state['issues'].append({
                    "issue": issue,
                    "timestamp": datetime.now().isoformat()
                })
            
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
            
            return {
                "success": True,
                "message": f"Blocking issue added: '{issue}'",
                "total_issues": len(state['blocking_issues'])
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def status(self) -> dict:
        """Get current loop status.
        
        Returns:
            dict with full status information
        """
        if not self.state_file.exists():
            return {
                "active": False,
                "message": "No active loop state found"
            }
        
        try:
            with open(self.state_file) as f:
                state = json.load(f)
            
            total = state.get('total_tasks', 0)
            completed = state.get('completed_tasks', 0)
            blocking = state.get('blocking_issues', [])
            promise = state.get('completion_promise')
            
            # Check if promise is fulfilled
            promise_fulfilled = False
            if promise:
                promise_type = promise.get('promise_type', '')
                
                if promise_type == 'task_count':
                    expected = int(promise.get('expected_value', 0))
                    promise_fulfilled = completed >= expected
                    
                elif promise_type == 'file_exists':
                    check_path = Path.cwd() / promise.get('condition', '')
                    promise_fulfilled = check_path.exists()
                    
                elif promise_type == 'content_match':
                    check_path = Path.cwd() / promise.get('condition', '')
                    if check_path.exists():
                        content = check_path.read_text()
                        pattern = promise.get('expected_value', '')
                        promise_fulfilled = pattern in content
            
            has_remaining = completed < total and not promise_fulfilled
            
            return {
                "active": True,
                "has_remaining_tasks": has_remaining,
                "tasks_completed": completed,
                "total_tasks": total,
                "remaining_tasks": total - completed,
                "completion_reached": (not has_remaining) or promise_fulfilled,
                "blocking_issues": blocking,
                "promise_status": {
                    "has_promise": bool(promise),
                    "type": promise.get('promise_type') if promise else None,
                    "fulfilled": promise_fulfilled and promise  # Only mark fulfilled if not already done
                } if promise else None
            }
        except Exception as e:
            return {
                "active": False,
                "error": str(e)
            }
    
    def reset(self) -> dict:
        """Reset the loop state (clears completed tasks but keeps total).
        
        Returns:
            dict with reset status
        """
        if not self.state_file.exists():
            return {
                "success": False,
                "error": "No active loop state found"
            }
        
        try:
            with open(self.state_file) as f:
                state = json.load(f)
            
            old_completed = state['completed_tasks']
            state['completed_tasks'] = 0
            
            # Clear completion history on reset
            if 'completion_history' in state:
                del state['completion_history']
            
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
            
            return {
                "success": True,
                "message": f"Loop reset - cleared {old_completed} completed tasks",
                "total_tasks": state['total_tasks']
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


# Convenience functions for tool handlers to use

def init_loop_command(total_tasks: int, promise_type: str = None, 
                      condition: str = None, expected_value: str = None) -> str:
    """Command-style loop initialization."""
    cmds = LoopCommands()
    result = cmds.init_loop(total_tasks, promise_type, condition, expected_value)
    return json.dumps(result)


def complete_task_command() -> str:
    """Mark next task as completed."""
    cmds = LoopCommands()
    result = cmds.complete_task()
    return json.dumps(result)


def set_promise_command(promise_type: str, condition: str = None, 
                        expected_value: str = None) -> str:
    """Set completion promise."""
    cmds = LoopCommands()
    result = cmds.set_promise(promise_type, condition, expected_value)
    return json.dumps(result)


def add_blocking_issue_command(issue: str) -> str:
    """Add a blocking issue."""
    cmds = LoopCommands()
    result = cmds.add_blocking_issue(issue)
    return json.dumps(result)


def loop_status_command() -> str:
    """Get current loop status."""
    cmds = LoopCommands()
    result = cmds.status()
    return json.dumps(result, indent=2)
