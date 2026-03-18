"""Tool handlers for hermes-loop plugin.

These provide both direct JSON responses and command-style interfaces."""

import json
from pathlib import Path


def loop_status(args: dict, **kwargs) -> str:
    """Check current loop status (alias for /loop_status).
    
    Returns detailed status including completion progress and promise state.
    """
    from .commands import LoopCommands
    
    cmds = LoopCommands()
    result = cmds.status()
    return json.dumps(result, indent=2)


def set_completion_promise(args: dict, **kwargs) -> str:
    """Set completion promise (alias for /set_promise).
    
    Defines custom termination conditions for the loop.
    """
    from .commands import LoopCommands
    
    cmds = LoopCommands()
    result = cmds.set_promise(
        promise_type=args.get('promise_type'),
        condition=args.get('condition'),
        expected_value=args.get('expected_value')
    )
    return json.dumps(result)


def init_loop(args: dict, **kwargs) -> str:
    """Initialize a new loop state (alias for /init_loop).
    
    Creates the state file and sets up task tracking.
    
    Args:
        total_tasks: Total number of tasks in the loop
        promise_type: Optional completion promise type
        condition: Path/pattern for the promise
        expected_value: Expected value for content_match promises
    """
    from .commands import LoopCommands
    
    cmds = LoopCommands()
    result = cmds.init_loop(
        total_tasks=args.get('total_tasks', 0),
        promise_type=args.get('promise_type'),
        condition=args.get('condition'),
        expected_value=args.get('expected_value')
    )
    return json.dumps(result)


def complete_task(args: dict, **kwargs) -> str:
    """Complete next task (alias for /complete_task).
    
    Increments the completed tasks counter.
    Use this after each subagent or implementation step.
    """
    from .commands import LoopCommands
    
    cmds = LoopCommands()
    result = cmds.complete_task()
    return json.dumps(result)


def add_blocking_issue(args: dict, **kwargs) -> str:
    """Add a blocking issue (alias for /add_blocking_issue).
    
    When issues block progress, the loop will stop automatically.
    Use this when you hit an error that requires manual intervention.
    
    Args:
        issue: Description of the blocking issue
    """
    from .commands import LoopCommands
    
    cmds = LoopCommands()
    result = cmds.add_blocking_issue(args.get('issue', ''))
    return json.dumps(result)


def reset_loop(args: dict, **kwargs) -> str:
    """Reset loop state (alias for /reset_loop).
    
    Clears completed task count but keeps total tasks and promise.
    Use this to restart iteration from the beginning.
    """
    from .commands import LoopCommands
    
    cmds = LoopCommands()
    result = cmds.reset()
    return json.dumps(result)


# Command-style aliases for more intuitive usage

def command_init_loop(args: dict, **kwargs) -> str:
    """Command-style loop initialization."""
    return init_loop(args, **kwargs)


def command_complete_task(args: dict, **kwargs) -> str:
    """Mark next task as completed."""
    return complete_task(args, **kwargs)


def command_set_promise(args: dict, **kwargs) -> str:
    """Set completion promise."""
    return set_completion_promise(args, **kwargs)


def command_add_blocking_issue(args: dict, **kwargs) -> str:
    """Add a blocking issue."""
    return add_blocking_issue(args, **kwargs)


def command_loop_status(args: dict, **kwargs) -> str:
    """Get current loop status."""
    return loop_status(args, **kwargs)
