# Why You Don't See Slash Commands

## The Distinction

Hermes Agent has **two separate systems**:

### 1. Slash Commands (`/help`, `/new`, etc.)
- Core CLI features only
- Hardcoded in `~/.hermes/hermes-agent/hermes_cli/commands.py`
- Plugins CANNOT register slash commands directly
- These appear in autocomplete when you type `/`

### 2. Tools (Your Plugin's Functions)
- Available to the agent during conversations
- Your plugin provides **6 tools** that the agent can call
- These appear in `hermes /tools` output
- You call them like: `init_loop(total_tasks=5)`

## Your Plugin HAS 6 TOOLS

| Tool | Description | How to Call |
|------|-------------|-------------|
| `loop_status` | Check current loop state | `loop_status()` |
| `set_completion_promise` | Define termination condition | `set_completion_promise(promise_type="file_exists", ...)` |
| `init_loop` | Initialize new loop | `init_loop(total_tasks=5, ...)` |
| `complete_task` | Mark task complete | `complete_task()` |
| `add_blocking_issue` | Add blocker that stops loop | `add_blocking_issue(issue="Cannot proceed...")` |
| `reset_loop` | Reset completed count | `reset_loop()` |

## How to Verify Your Tools Work

### Option 1: Check in Hermes CLI
```bash
hermes
# Then type: /tools
# You should see hermes-loop tools listed!
```

### Option 2: Test Directly
```python
from pathlib import Path
import json

# Initialize a test loop
init_loop(total_tasks=3)

# Check status
status = loop_status()
print(status)
# Should show: {"active": true, "tasks_completed": 0, "total_tasks": 3, ...}

# Complete a task
complete_task()

# Check again
status = loop_status()
print(status)
# Should show: {"active": true, "tasks_completed": 1, "total_tasks": 3, ...}
```

## Why Tools Are Actually BETTER Than Slash Commands

### Slash Commands Limitations
- Only work at CLI level
- Can't be called by the agent during conversation
- Static, fixed behavior

### Tool Advantages
- Agent can CALL them during reasoning
- Dynamic parameter passing
- Return structured JSON responses
- Integrate with subagents and other tools
- Work across sessions via state persistence

## Example Usage Pattern

```python
# User asks: "Help me implement a feature through 5 steps"

# Agent can NOW call your tools:
init_loop(total_tasks=5, promise_type="file_exists", condition="src/feature.tsx")

# Then during implementation:
delegate_task(goal="Create component structure")
complete_task()

# Check progress anytime:
loop_status()
# Returns structured JSON with completion state

# If stuck:
add_blocking_issue(issue="Need API key for testing")
```

## TL;DR

- ✅ Your plugin IS installed and working
- ✅ You have 6 tools available to the agent
- ❌ Slash commands (`/init_loop`) are NOT supported by plugins (core-only feature)
- 🎯 **Use tools instead** - they're more powerful!

## Quick Test

```bash
# Start Hermes
hermes

# Check if your tools appear:
/tools

# You should see something like:
# hermes-loop: loop_status, set_completion_promise, init_loop, complete_task, add_blocking_issue, reset_loop
```

If you don't see them in `/tools`, the plugin might not have loaded. Try restarting Hermes and checking again!
