"""Baseline tests for hermes-loop plugin logic.

Covers the four main layers:
1. LoopCommands (commands.py) — state file read/write
2. _on_pre_llm_call hook (__init__.py) — context injection logic
3. display.py — progress bar math and output safety
4. hook/handler.py — gateway hook filtering
"""

import importlib
import importlib.util
import json
import os
import sys
from pathlib import Path

import pytest

# ── helpers ──────────────────────────────────────────────────────────────────

def _write_state(path: Path, **kwargs) -> Path:
    """Write a loop state JSON file and return its path."""
    state = {
        "total_tasks": 5,
        "completed_tasks": 0,
        "blocking_issues": [],
        "completion_promise": None,
    }
    state.update(kwargs)
    state_file = path / ".hermes-loop-state.json"
    state_file.write_text(json.dumps(state))
    return state_file


# ═══════════════════════════════════════════════════════════════════════════════
# 1. LoopCommands — commands.py
# ═══════════════════════════════════════════════════════════════════════════════

class TestLoopInit:
    def test_creates_state_file(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        from commands import LoopCommands
        result = LoopCommands().init_loop(total_tasks=3)
        assert result["success"] is True
        assert (tmp_path / ".hermes-loop-state.json").exists()

    def test_state_file_has_correct_fields(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        from commands import LoopCommands
        LoopCommands().init_loop(total_tasks=7)
        state = json.loads((tmp_path / ".hermes-loop-state.json").read_text())
        assert state["total_tasks"] == 7
        assert state["completed_tasks"] == 0
        assert state["blocking_issues"] == []
        assert state["completion_promise"] is None

    def test_promise_is_stored(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        from commands import LoopCommands
        LoopCommands().init_loop(total_tasks=4, promise_type="task_count",
                                 condition="", expected_value="4")
        state = json.loads((tmp_path / ".hermes-loop-state.json").read_text())
        assert state["completion_promise"]["promise_type"] == "task_count"
        assert state["completion_promise"]["fulfilled"] is False

    def test_overwrites_existing_state(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        from commands import LoopCommands
        cmds = LoopCommands()
        cmds.init_loop(total_tasks=2)
        cmds.complete_task()
        cmds.init_loop(total_tasks=10)
        state = json.loads((tmp_path / ".hermes-loop-state.json").read_text())
        assert state["completed_tasks"] == 0
        assert state["total_tasks"] == 10


class TestCompleteTask:
    def test_increments_counter(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _write_state(tmp_path, total_tasks=5, completed_tasks=0)
        from commands import LoopCommands
        result = LoopCommands().complete_task()
        assert result["success"] is True
        assert result["new_count"] == 1
        assert result["remaining"] == 4

    def test_persists_across_calls(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _write_state(tmp_path, total_tasks=5, completed_tasks=0)
        from commands import LoopCommands
        cmds = LoopCommands()
        cmds.complete_task()
        cmds.complete_task()
        state = json.loads((tmp_path / ".hermes-loop-state.json").read_text())
        assert state["completed_tasks"] == 2

    def test_remaining_reaches_zero(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _write_state(tmp_path, total_tasks=2, completed_tasks=0)
        from commands import LoopCommands
        cmds = LoopCommands()
        cmds.complete_task()
        result = cmds.complete_task()
        assert result["remaining"] == 0

    def test_no_state_file_returns_error(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        from commands import LoopCommands
        result = LoopCommands().complete_task()
        assert result["success"] is False
        assert "error" in result

    def test_tracks_previous_count(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _write_state(tmp_path, total_tasks=5, completed_tasks=3)
        from commands import LoopCommands
        result = LoopCommands().complete_task()
        assert result["previous_count"] == 3
        assert result["new_count"] == 4


class TestBlockingIssues:
    def test_adds_issue(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _write_state(tmp_path)
        from commands import LoopCommands
        result = LoopCommands().add_blocking_issue("DB connection failed")
        assert result["success"] is True
        state = json.loads((tmp_path / ".hermes-loop-state.json").read_text())
        assert "DB connection failed" in state["blocking_issues"]

    def test_no_duplicate_issues(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _write_state(tmp_path)
        from commands import LoopCommands
        cmds = LoopCommands()
        cmds.add_blocking_issue("same issue")
        cmds.add_blocking_issue("same issue")
        state = json.loads((tmp_path / ".hermes-loop-state.json").read_text())
        assert state["blocking_issues"].count("same issue") == 1

    def test_no_state_file_returns_error(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        from commands import LoopCommands
        result = LoopCommands().add_blocking_issue("some issue")
        assert result["success"] is False

    def test_multiple_distinct_issues(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _write_state(tmp_path)
        from commands import LoopCommands
        cmds = LoopCommands()
        cmds.add_blocking_issue("issue A")
        cmds.add_blocking_issue("issue B")
        state = json.loads((tmp_path / ".hermes-loop-state.json").read_text())
        assert len(state["blocking_issues"]) == 2


class TestLoopStatus:
    def test_no_state_file(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        from commands import LoopCommands
        result = LoopCommands().status()
        assert result["active"] is False

    def test_active_loop(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _write_state(tmp_path, total_tasks=5, completed_tasks=2)
        from commands import LoopCommands
        result = LoopCommands().status()
        assert result["active"] is True
        assert result["tasks_completed"] == 2
        assert result["total_tasks"] == 5
        assert result["remaining_tasks"] == 3
        assert result["has_remaining_tasks"] is True

    def test_completed_loop(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _write_state(tmp_path, total_tasks=3, completed_tasks=3)
        from commands import LoopCommands
        result = LoopCommands().status()
        assert result["has_remaining_tasks"] is False

    def test_blocked_loop(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _write_state(tmp_path, blocking_issues=["disk full"])
        from commands import LoopCommands
        result = LoopCommands().status()
        assert result["blocking_issues"] == ["disk full"]

    def test_task_count_promise_fulfilled(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _write_state(tmp_path, total_tasks=5, completed_tasks=4,
                     completion_promise={
                         "promise_type": "task_count",
                         "condition": "",
                         "expected_value": "4",
                         "fulfilled": False,
                     })
        from commands import LoopCommands
        result = LoopCommands().status()
        assert result["promise_status"]["fulfilled"] is not False  # truthy = fulfilled

    def test_task_count_promise_not_yet_met(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _write_state(tmp_path, total_tasks=5, completed_tasks=2,
                     completion_promise={
                         "promise_type": "task_count",
                         "condition": "",
                         "expected_value": "5",
                         "fulfilled": False,
                     })
        from commands import LoopCommands
        result = LoopCommands().status()
        assert result["promise_status"]["fulfilled"] is False


class TestLoopReset:
    def test_resets_completed_count(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _write_state(tmp_path, total_tasks=5, completed_tasks=3)
        from commands import LoopCommands
        result = LoopCommands().reset()
        assert result["success"] is True
        state = json.loads((tmp_path / ".hermes-loop-state.json").read_text())
        assert state["completed_tasks"] == 0
        assert state["total_tasks"] == 5  # unchanged

    def test_no_state_file_returns_error(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        from commands import LoopCommands
        result = LoopCommands().reset()
        assert result["success"] is False


# ═══════════════════════════════════════════════════════════════════════════════
# 2. _on_pre_llm_call hook logic
# ═══════════════════════════════════════════════════════════════════════════════

# conftest.py bootstraps hermes_loop_plugin into sys.modules before tests run.
import hermes_loop_plugin as _pkg  # noqa: E402

def _get_hook():
    return _pkg._on_pre_llm_call

_COMMON_KWARGS = dict(session_id="s1", user_message="go", conversation_history=[],
                      is_first_turn=False, model="test", platform="cli")


class TestPreLlmCallHook:
    def test_no_state_file_returns_none(self, tmp_path):
        hook = _get_hook()
        result = hook(**_COMMON_KWARGS, cwd=str(tmp_path))
        assert result is None

    def test_active_loop_injects_context(self, tmp_path):
        _write_state(tmp_path, total_tasks=5, completed_tasks=2)
        hook = _get_hook()
        result = hook(**_COMMON_KWARGS, cwd=str(tmp_path))
        assert isinstance(result, dict)
        assert "context" in result
        assert "2/5" in result["context"]
        assert "3 remaining" in result["context"]

    def test_blocked_loop_returns_blocked_context(self, tmp_path):
        _write_state(tmp_path, total_tasks=5, completed_tasks=1,
                     blocking_issues=["permission denied"])
        hook = _get_hook()
        result = hook(**_COMMON_KWARGS, cwd=str(tmp_path))
        assert "BLOCKED" in result["context"]
        assert "permission denied" in result["context"]

    def test_all_tasks_complete_returns_wrap_up(self, tmp_path):
        _write_state(tmp_path, total_tasks=3, completed_tasks=3)
        hook = _get_hook()
        result = hook(**_COMMON_KWARGS, cwd=str(tmp_path))
        assert "All 3 tasks are complete" in result["context"]
        assert "Summarize" in result["context"]

    def test_promise_fulfilled_marks_fulfilled_in_file(self, tmp_path):
        _write_state(tmp_path, total_tasks=5, completed_tasks=4,
                     completion_promise={
                         "promise_type": "task_count",
                         "condition": "",
                         "expected_value": "4",
                         "fulfilled": False,
                     })
        hook = _get_hook()
        hook(**_COMMON_KWARGS, cwd=str(tmp_path))
        state = json.loads((tmp_path / ".hermes-loop-state.json").read_text())
        assert state["completion_promise"]["fulfilled"] is True

    def test_promise_not_met_says_keep_working(self, tmp_path):
        _write_state(tmp_path, total_tasks=5, completed_tasks=2,
                     completion_promise={
                         "promise_type": "task_count",
                         "condition": "",
                         "expected_value": "5",
                         "fulfilled": False,
                     })
        hook = _get_hook()
        result = hook(**_COMMON_KWARGS, cwd=str(tmp_path))
        assert "keep working" in result["context"]

    def test_file_exists_promise_detected(self, tmp_path):
        sentinel = tmp_path / "done.txt"
        sentinel.write_text("done")
        _write_state(tmp_path, total_tasks=3, completed_tasks=1,
                     completion_promise={
                         "promise_type": "file_exists",
                         "condition": "done.txt",
                         "expected_value": "",
                         "fulfilled": False,
                     })
        hook = _get_hook()
        result = hook(**_COMMON_KWARGS, cwd=str(tmp_path))
        assert "FULFILLED" in result["context"]

    def test_content_match_promise_detected(self, tmp_path):
        check_file = tmp_path / "output.txt"
        check_file.write_text("BUILD SUCCESS\n")
        _write_state(tmp_path, total_tasks=3, completed_tasks=1,
                     completion_promise={
                         "promise_type": "content_match",
                         "condition": "output.txt",
                         "expected_value": "BUILD SUCCESS",
                         "fulfilled": False,
                     })
        hook = _get_hook()
        result = hook(**_COMMON_KWARGS, cwd=str(tmp_path))
        assert "FULFILLED" in result["context"]


# ═══════════════════════════════════════════════════════════════════════════════
# 3. display.py — progress bar math and output safety
# ═══════════════════════════════════════════════════════════════════════════════

class TestProgressBar:
    """Tests for display._bar() — the core progress calculation."""

    def setup_method(self):
        # Suppress ANSI and emit for all display tests
        os.environ["HERMES_LOOP_NO_TUI"] = "1"
        import importlib
        import display
        importlib.reload(display)
        self.display = display

    def teardown_method(self):
        os.environ.pop("HERMES_LOOP_NO_TUI", None)

    def test_empty_bar(self):
        bar = self.display._bar(0, 10)
        assert bar == "░" * 10

    def test_full_bar(self):
        bar = self.display._bar(10, 10)
        assert bar == "█" * 10

    def test_half_bar(self):
        bar = self.display._bar(5, 10)
        assert bar.count("█") == 5
        assert bar.count("░") == 5

    def test_zero_total_returns_empty(self):
        bar = self.display._bar(0, 0)
        assert "█" not in bar

    def test_custom_width(self):
        bar = self.display._bar(4, 8, width=8)
        assert len(bar) == 8
        assert bar.count("█") == 4


class TestDisplayOutput:
    """Ensure display functions don't crash regardless of terminal state."""

    def setup_method(self):
        os.environ["HERMES_LOOP_NO_TUI"] = "1"
        import importlib
        import display
        importlib.reload(display)
        self.display = display

    def teardown_method(self):
        os.environ.pop("HERMES_LOOP_NO_TUI", None)

    def test_show_loop_start(self):
        self.display.show_loop_start(5)  # must not raise

    def test_show_task_complete_mid(self):
        self.display.show_task_complete(2, 5)

    def test_show_task_complete_done(self):
        self.display.show_task_complete(5, 5)

    def test_show_loop_blocked(self):
        self.display.show_loop_blocked("some error")

    def test_show_loop_blocked_truncates_long_issue(self):
        long = "x" * 200
        self.display.show_loop_blocked(long)  # must not raise or blow up

    def test_show_loop_status(self):
        self.display.show_loop_status(3, 5)

    def test_show_loop_status_with_blocking_issues(self):
        self.display.show_loop_status(1, 5, blocking_issues=["disk full"])

    def test_show_loop_status_zero_total(self):
        self.display.show_loop_status(0, 0)


# ═══════════════════════════════════════════════════════════════════════════════
# 4. hook/handler.py — gateway hook intent
# ═══════════════════════════════════════════════════════════════════════════════

def _load_handler():
    """Load hook/handler.py as a standalone module."""
    spec = importlib.util.spec_from_file_location(
        "hermes_loop_hook_handler",
        Path(__file__).parent.parent / "hook" / "handler.py",
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestGatewayHandler:
    def test_no_op_when_no_loop_tools(self, tmp_path, caplog):
        handler = _load_handler()
        _write_state(tmp_path, total_tasks=5, completed_tasks=2)
        import logging
        with caplog.at_level(logging.INFO, logger="hermes.hook.hermes-loop"):
            handler.handle("agent:step", {
                "tool_names": ["terminal", "read_file"],
                "session_id": "s1",
                "cwd": str(tmp_path),
            })
        assert not caplog.records  # nothing logged — loop tools not involved

    def test_logs_progress_when_loop_tool_used(self, tmp_path, caplog):
        handler = _load_handler()
        _write_state(tmp_path, total_tasks=5, completed_tasks=2)
        import logging
        with caplog.at_level(logging.INFO, logger="hermes.hook.hermes-loop"):
            handler.handle("agent:step", {
                "tool_names": ["complete_task"],
                "session_id": "s1",
                "cwd": str(tmp_path),
            })
        assert any("2/5" in r.message for r in caplog.records)

    def test_logs_blocked_when_issues_present(self, tmp_path, caplog):
        handler = _load_handler()
        _write_state(tmp_path, total_tasks=5, completed_tasks=1,
                     blocking_issues=["network unreachable"])
        import logging
        with caplog.at_level(logging.INFO, logger="hermes.hook.hermes-loop"):
            handler.handle("agent:step", {
                "tool_names": ["loop_status"],
                "session_id": "s1",
                "cwd": str(tmp_path),
            })
        assert any("BLOCKED" in r.message for r in caplog.records)

    def test_logs_complete_on_agent_end(self, tmp_path, caplog):
        handler = _load_handler()
        _write_state(tmp_path, total_tasks=3, completed_tasks=3)
        import logging
        with caplog.at_level(logging.INFO, logger="hermes.hook.hermes-loop"):
            handler.handle("agent:end", {
                "tool_names": [],
                "session_id": "s1",
                "cwd": str(tmp_path),
            })
        assert any("COMPLETE" in r.message for r in caplog.records)

    def test_no_op_when_no_state_file(self, tmp_path, caplog):
        handler = _load_handler()
        import logging
        with caplog.at_level(logging.INFO, logger="hermes.hook.hermes-loop"):
            handler.handle("agent:step", {
                "tool_names": ["complete_task"],
                "session_id": "s1",
                "cwd": str(tmp_path),
            })
        assert not caplog.records  # no state file → silent no-op
