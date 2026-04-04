"""Terminal display helpers for hermes-loop.

Writes compact ASCII art loop-status banners to sys.stderr so they appear
in the terminal regardless of prompt_toolkit's stdout patching.

Respects the NO_COLOR env var and HERMES_LOOP_NO_TUI env var to suppress
all output when running non-interactively or in tests.
"""

import os
import sys
from typing import Optional


# ── colour palette ──────────────────────────────────────────────────────────
_ANSI = not (os.getenv("NO_COLOR") or os.getenv("HERMES_LOOP_NO_TUI") or not sys.stderr.isatty())

def _c(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m" if _ANSI else text

def _cyan(t):   return _c("96", t)
def _green(t):  return _c("92", t)
def _yellow(t): return _c("93", t)
def _red(t):    return _c("91", t)
def _bold(t):   return _c("1", t)
def _dim(t):    return _c("2", t)


# ── progress bar ─────────────────────────────────────────────────────────────
def _bar(done: int, total: int, width: int = 10) -> str:
    if total <= 0:
        return "░" * width
    filled = min(width, round(done / total * width))
    return "█" * filled + "░" * (width - filled)


# ── public display functions ─────────────────────────────────────────────────

def show_loop_start(total_tasks: int) -> None:
    """Print a loop-start banner when init_loop is called."""
    line = (
        _cyan("↻") + " " + _bold("LOOP START") +
        "  " + _dim(f"0 / {total_tasks} tasks")
    )
    _emit(line)


def show_task_complete(done: int, total: int, remaining: Optional[int] = None) -> None:
    """Print a progress bar after complete_task is called."""
    if remaining is None:
        remaining = max(0, total - done)

    bar = _bar(done, total)

    if done >= total:
        line = (
            _green("✓") + " " + _bold("LOOP COMPLETE") +
            "  " + _green(_bar(total, total)) +
            "  " + _green(f"{done} / {total}")
        )
    else:
        line = (
            _cyan("↻") + " " + _bold("LOOP") +
            "  " + _cyan(bar) +
            "  " + _bold(f"{done} / {total}") +
            "  " + _dim(f"· {remaining} remaining")
        )
    _emit(line)


def show_loop_blocked(issue: str) -> None:
    """Print a blocked banner when add_blocking_issue is called."""
    short = issue[:60] + "…" if len(issue) > 60 else issue
    line = (
        _red("⛔") + " " + _bold(_red("LOOP BLOCKED")) +
        "  " + _dim(short)
    )
    _emit(line)


def show_loop_status(done: int, total: int, blocked: bool = False,
                     blocking_issues: Optional[list] = None) -> None:
    """Print a compact status line for loop_status queries."""
    if blocking_issues:
        show_loop_blocked(blocking_issues[0] if blocking_issues else "unknown")
        return

    bar = _bar(done, total)
    pct = f"{round(done / total * 100) if total else 0}%"

    line = (
        _cyan("↻") + " " + _bold("LOOP STATUS") +
        "  " + _cyan(bar) +
        "  " + _bold(f"{done} / {total}") +
        "  " + _dim(pct)
    )
    _emit(line)


# ── internal ─────────────────────────────────────────────────────────────────

def _emit(line: str) -> None:
    """Write one status line to stderr, safely."""
    try:
        sys.stderr.write(f"\n  {line}\n")
        sys.stderr.flush()
    except Exception:
        pass
