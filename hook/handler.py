"""Gateway hook handler for hermes-loop.

Fires on agent:step and agent:end events. When loop tools are detected in the
step's tool_names list, reads the loop state file and logs progress.

This hook only runs in gateway mode (Telegram, Discord, Slack, etc.).
For CLI TUI flair, see display.py which prints to stderr from tool handlers.
"""

import json
import logging
import os
from pathlib import Path

logger = logging.getLogger("hermes.hook.hermes-loop")

_LOOP_TOOLS = frozenset({
    "init_loop",
    "complete_task",
    "add_blocking_issue",
    "loop_status",
    "set_completion_promise",
    "reset_loop",
})


def _read_state(cwd: str) -> dict | None:
    state_file = Path(cwd) / ".hermes-loop-state.json"
    if not state_file.exists():
        return None
    try:
        return json.loads(state_file.read_text())
    except Exception:
        return None


def _bar(done: int, total: int, width: int = 8) -> str:
    if total <= 0:
        return "░" * width
    filled = min(width, round(done / total * width))
    return "█" * filled + "░" * (width - filled)


def handle(event_type: str, context: dict) -> None:
    """Handle agent:step and agent:end hook events."""
    tool_names: list = context.get("tool_names", [])
    session_id: str = context.get("session_id", "")
    cwd: str = context.get("cwd", os.getcwd())

    # Only act when loop tools were involved this step
    if event_type == "agent:step" and not any(t in _LOOP_TOOLS for t in tool_names):
        return

    state = _read_state(cwd)
    if state is None:
        return

    done = state.get("completed_tasks", 0)
    total = state.get("total_tasks", 0)
    issues = state.get("blocking_issues", [])

    if issues:
        logger.info(
            "[hermes-loop] session=%s  ⛔ BLOCKED  %s",
            session_id,
            issues[0][:80] if issues else "",
        )
        return

    bar = _bar(done, total)
    remaining = max(0, total - done)

    if event_type == "agent:end" or done >= total:
        if total > 0 and done >= total:
            logger.info(
                "[hermes-loop] session=%s  ✓ COMPLETE  %s  %d/%d",
                session_id, bar, done, total,
            )
        return

    logger.info(
        "[hermes-loop] session=%s  ↻ LOOP  %s  %d/%d  (%d remaining)",
        session_id, bar, done, total, remaining,
    )
