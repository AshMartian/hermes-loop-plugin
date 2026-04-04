"""Tool handlers for hermes-loop plugin.

These provide both direct JSON responses and command-style interfaces."""

import json
import logging
from pathlib import Path

try:
    from . import display as _display
except ImportError:
    import display as _display  # type: ignore[import]

try:
    from .commands import LoopCommands as _LoopCommands
except ImportError:
    from commands import LoopCommands as _LoopCommands  # type: ignore[import]

_log = logging.getLogger(__name__)

# ── Session-resume prefill helpers ────────────────────────────────────────────

# Written to ~/.hermes/ so hermes resolves it as a relative prefill path.
_RESUME_FILE = Path.home() / ".hermes" / "loop-resume.json"

_RESUME_MSG = (
    "Startup auto-resume check: look for .hermes-loop-state.json in the current "
    "directory. If found and the loop is still active (completed_tasks < total_tasks "
    "and blocking_issues is empty), immediately call loop_status to confirm progress "
    "then resume executing tasks automatically — do not wait for user input. Keep "
    "calling complete_task after each step until all tasks are done or a blocking "
    "issue arises. If no active loop exists here, just greet me normally."
)


def _write_resume_prefill() -> None:
    """Write the session-resume prefill so hermes auto-resumes on next TUI startup."""
    try:
        _RESUME_FILE.parent.mkdir(parents=True, exist_ok=True)
        _RESUME_FILE.write_text(
            json.dumps([{"role": "user", "content": _RESUME_MSG}], indent=2)
        )
    except Exception:
        pass


def _clear_resume_prefill() -> None:
    """Delete the session-resume prefill once the loop is complete or reset."""
    try:
        _RESUME_FILE.unlink(missing_ok=True)
    except Exception:
        pass


def _configure_auto_resume() -> None:
    """One-time: add prefill_messages_file to ~/.hermes/config.yaml if absent.

    Idempotent — skips if already configured.  Called from init_loop so it
    runs the first time the user starts a loop, without needing register(ctx).
    """
    config_path = Path.home() / ".hermes" / "config.yaml"
    # Fast-path: if the key is already present, do nothing.
    if config_path.exists() and "prefill_messages_file" in config_path.read_text():
        return
    try:
        import yaml  # hermes ships with PyYAML
    except ImportError:
        _log.debug("hermes-loop: PyYAML unavailable, skipping auto-resume config")
        return
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config: dict = {}
    if config_path.exists():
        with open(config_path) as fh:
            config = yaml.safe_load(fh) or {}
    agent_cfg = config.setdefault("agent", {})
    if "prefill_messages_file" in agent_cfg:
        return  # Another process may have written it between our checks
    agent_cfg["prefill_messages_file"] = "loop-resume.json"
    with open(config_path, "w") as fh:
        yaml.dump(config, fh, default_flow_style=False, allow_unicode=True)
    _log.info("hermes-loop: configured auto-resume prefill in %s", config_path)


def loop_status(args: dict, **kwargs) -> str:
    """Check current loop status (alias for /loop_status).
    
    Returns detailed status including completion progress and promise state.
    """
    cmds = _LoopCommands()
    result = cmds.status()

    # TUI: show compact status line in terminal
    _display.show_loop_status(
        done=result.get("completed_tasks", 0),
        total=result.get("total_tasks", 0),
        blocking_issues=result.get("blocking_issues"),
    )

    return json.dumps(result, indent=2)


def set_completion_promise(args: dict, **kwargs) -> str:
    """Set completion promise (alias for /set_promise).
    
    Defines custom termination conditions for the loop.
    """
    cmds = _LoopCommands()
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
    cmds = _LoopCommands()
    result = cmds.init_loop(
        total_tasks=args.get('total_tasks', 0),
        promise_type=args.get('promise_type'),
        condition=args.get('condition'),
        expected_value=args.get('expected_value')
    )

    # TUI: announce loop start
    _display.show_loop_start(args.get('total_tasks', 0))

    # Persist resume prefill so next TUI session auto-resumes
    if result.get("success"):
        _configure_auto_resume()
        _write_resume_prefill()

    return json.dumps(result)


def complete_task(args: dict, **kwargs) -> str:
    """Complete next task (alias for /complete_task).
    
    Increments the completed tasks counter.
    Use this after each subagent or implementation step.
    """
    cmds = _LoopCommands()
    result = cmds.complete_task()

    # TUI: update progress bar
    if result.get("success"):
        _display.show_task_complete(
            done=result.get("new_count", 0),
            total=result.get("total_tasks", 0),
            remaining=result.get("remaining", 0),
        )
        # Clear resume prefill once the loop is fully done
        if result.get("remaining", 1) == 0:
            _clear_resume_prefill()

    return json.dumps(result)


def add_blocking_issue(args: dict, **kwargs) -> str:
    """Add a blocking issue (alias for /add_blocking_issue).
    
    When issues block progress, the loop will stop automatically.
    Use this when you hit an error that requires manual intervention.
    
    Args:
        issue: Description of the blocking issue
    """
    cmds = _LoopCommands()
    issue_text = args.get('issue', '')
    result = cmds.add_blocking_issue(issue_text)

    # TUI: show blocked banner
    _display.show_loop_blocked(issue_text)

    return json.dumps(result)


def reset_loop(args: dict, **kwargs) -> str:
    """Reset loop state (alias for /reset_loop).
    
    Clears completed task count but keeps total tasks and promise.
    Use this to restart iteration from the beginning.
    """
    cmds = _LoopCommands()
    result = cmds.reset()
    # A reset means no active loop — clear the resume prefill
    _clear_resume_prefill()
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
