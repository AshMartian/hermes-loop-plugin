# 🚀 Hermes Loop Plugin - v1.0.0

**Continuous task execution for Hermes Agent**  
*Published: March 17, 2026 | License: MIT*

---

## What Is This?

The **Hermes Loop Plugin** enables persistent multi-step workflows where tasks span multiple sessions or require iterative refinement. Think of it as a "keep trying until done" engine for your AI agent.

Inspired by Claude Code's ralph-wiggum-loop pattern, but designed specifically for Hermes Agent's tool-based plugin architecture.

---

## Quick Start (30 Seconds)

### Installation

#### Current: Install from GitHub 🚀

```bash
pip install git+https://github.com/AshMartian/hermes-loop-plugin.git@v1.0.0
```

That's it! The plugin auto-discovers on your next Hermes Agent startup.

#### Coming Soon: PyPI Installation 📦

The plugin will be available on [PyPI](https://pypi.org/) for easier installation:

```bash
# Coming soon!
pip install hermes-loop-plugin
```

Track progress in our [GitHub Releases](https://github.com/AshMartian/hermes-loop-plugin/releases).

### First Loop

```python
from pathlib import Path
import json

# Define a 5-task loop that stops when file exists
state_file = Path.cwd() / '.hermes-loop-state.json'
with open(state_file, 'w') as f:
    json.dump({
        "total_tasks": 5,
        "completed_tasks": 0,
        "blocking_issues": [],
        "completion_promise": {
            "promise_type": "file_exists",
            "condition": "src/new-feature.tsx"
        }
    }, f)

# Loop continues until file exists or max iterations reached!
```

---

## Key Features

### 1. State File Persistence 📝
Tracks task progress via `.hermes-loop-state.json`, surviving agent restarts and session interruptions.

### 2. Completion Promises 🎯  
Define custom termination conditions:

| Type | Description | Use Case |
|------|-------------|----------|
| `task_count` | Stop after N tasks | Try at least 3 debugging approaches |
| `file_exists` | Stop when file created | Keep implementing until feature exists |
| `content_match` | Stop when content appears | Continue until bug fix is in code |

### 3. Six Powerful Tools 🔧

| Command | Description |
|---------|-------------|
| `init_loop` | Initialize a new loop state |
| `loop_status` | Check current loop status |
| `complete_task` | Mark next task as completed |
| `set_completion_promise` | Define custom termination condition |
| `add_blocking_issue` | Add blocker that stops loop |
| `reset_loop` | Reset completed count |

### 4. Automatic Resumption 🔁  
Interrupted loops resume from saved state when session restarts. No lost progress!

---

## Use Cases

### Feature Implementation Loop

```python
# Implement a feature in multiple steps
init_loop(
    total_tasks=5, 
    promise_type="file_exists", 
    condition="src/feature.tsx"
)

delegate_task(goal="Create component structure")
complete_task()

# Continue with remaining tasks...
```

### Debugging Until Fixed

```python
init_loop(
    total_tasks=10,
    promise_type="content_match",
    condition="src/app.tsx",
    expected_value="// Bug fixed"
)

# Loop continues until comment appears in code
```

---

## Installation & Usage

### From GitHub (Current)

```bash
pip install git+https://github.com/AshMartian/hermes-loop-plugin.git@v1.0.0
```

### Local Development

```bash
git clone https://github.com/AshMartian/hermes-loop-plugin.git
cd hermes-loop-plugin
pip install -e .
```

---

## Documentation

- **[README.md](README.md)** - Full documentation and examples
- **[SKILL.md](SKILL.md)** - Comprehensive usage guide with advanced patterns
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - How to contribute

---

## Download Now!

**Repository:** [https://github.com/AshMartian/hermes-loop-plugin](https://github.com/AshMartian/hermes-loop-plugin)  
**PyPI (Coming Soon):** https://pypi.org/project/hermes-loop-plugin/

```bash
# Install from GitHub now
pip install git+https://github.com/AshMartian/hermes-loop-plugin.git@v1.0.0

# Or wait for PyPI release: pip install hermes-loop-plugin
```

---

**License:** MIT | **Version:** 1.0.0 | **Status:** Ready to use! 🎉