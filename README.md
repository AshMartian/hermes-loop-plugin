# Hermes Loop Plugin

Continuous task execution loop that keeps the agent running until goals are completed via state file monitoring and optional completion promises.

## Overview

This plugin enables **persistent multi-step workflows** where tasks span multiple sessions or require iterative refinement. It works similarly to Claude Code's ralph-wiggum-loop but is designed specifically for Hermes Agent's plugin architecture.

## Features

- **State Persistence**: Tracks task progress via `.hermes-loop-state.json`
- **Completion Promises**: Define custom termination conditions (file exists, content match, task count)
- **Automatic Resumption**: Continues from where it left off across sessions
- **Blocking Detection**: Stops loop when critical issues prevent progress
- **Command-style Tools**: Intuitive tool names that work like slash commands!

### Available Commands

| Command | Description |
|---------|-------------|
| `init_loop` | Initialize a new loop state |
| `loop_status` | Check current loop status |
| `complete_task` | Mark next task as completed |
| `set_completion_promise` | Define custom termination condition |
| `add_blocking_issue` | Add blocker that stops loop |
| `reset_loop` | Reset completed count |

## Installation

### 📦 Hermes Installation

The plugin is available on [PyPI](https://pypi.org/project/hermes-loop-plugin/) and can be installed with hermes cli directly:

```bash
hermes plugins install AshMartian/hermes-loop-plugin
```
### From GitHub

The plugin is available for direct installation from our GitHub repository:

```bash
pip install git+https://github.com/AshMartian/hermes-loop-plugin.git@v1.0.0
```

After installation, the plugin will be automatically discovered when you start Hermes Agent. No additional configuration required!

## Updating

```bash
hermes plugins update hermes-loop
```

### Verify Installation

Check that the plugin is installed correctly:

```bash
# Check if package is installed
pip show hermes-loop-plugin

# Or verify plugin location (if using local development)
ls ~/.hermes/plugins/hermes-loop/
```

You should see:
- `plugin.yaml` - Plugin manifest
- `__init__.py` - Registration and hooks
- `schemas.py` - Tool schemas (what LLM sees)
- `tools.py` - Tool handlers (actual implementation)
- `SKILL.md` - Comprehensive usage documentation

### Local Development Installation

For development or custom builds, install from source:

```bash
# Clone the repository
git clone https://github.com/AshMartian/hermes-loop-plugin.git
cd hermes-loop-plugin

# Install in editable mode for development
pip install -e .

# Or build and install manually
python -m build
pip install dist/hermes_loop_plugin-*.whl
```

### Manual Installation (for advanced users)

If you need to install the plugin manually:

1. Download the package from [GitHub Releases](https://github.com/AshMartian/hermes-loop-plugin/releases) or clone the repository
2. Install using pip: `pip install dist/hermes_loop_plugin-X.X.X.tar.gz`
3. Restart Hermes Agent to load the plugin

**Track progress:** Check our [GitHub Releases](https://github.com/AshMartian/hermes-loop-plugin/releases) for updates when we publish to PyPI.

## Quick Start

### 1. Initialize a loop state

Create a `.hermes-loop-state.json` file in your working directory:

```python
from pathlib import Path
import json

state_file = Path.cwd() / '.hermes-loop-state.json'

with open(state_file, 'w') as f:
    json.dump({
        "total_tasks": 5,
        "completed_tasks": 0,
        "blocking_issues": [],
        "completion_promise": {
            "promise_type": "file_exists",
            "condition": "src/features/new-feature.tsx"
        }
    }, f)
```

### 2. Set completion promise (optional)

Use the tool to define custom termination conditions:

```python
set_completion_promise(
    promise_type="content_match",
    condition="tests/feature.test.ts",
    expected_value="describe('Feature'"
)
```

### 3. Execute tasks

Run your tasks via subagents or direct implementation, updating the state after each completion:

```python
from pathlib import Path

# Task 1
delegate_task(goal="Implement feature step 1")

# Update state
state_file = Path.cwd() / '.hermes-loop-state.json'
with open(state_file) as f:
    state = json.load(f)
state['completed_tasks'] += 1
with open(state_file, 'w') as f:
    json.dump(state, f, indent=2)

# Repeat for remaining tasks...
```

### 4. Loop continues automatically

The plugin's stop hook monitors the state file and determines whether to continue or stop execution based on:
- Task completion count vs total
- Completion promise fulfillment status  
- Blocking issues present

## State File Format

```json
{
  "total_tasks": 5,
  "completed_tasks": 2,
  "blocking_issues": [],
  "completion_promise": {
    "promise_type": "file_exists",
    "condition": "src/features/new-feature.tsx",
    "expected_value": null,
    "fulfilled": false
  },
  "created_at": "2026-03-17T09:38:00Z"
}
```

**Fields:**
- `total_tasks`: Total number of tasks in the loop
- `completed_tasks`: Number completed so far  
- `blocking_issues`: List of issues that should stop the loop
- `completion_promise`: Optional custom termination condition
- `created_at`: Timestamp when loop started

## Completion Promise Types

### 1. Task Count

Stop after completing a specific number of tasks:

```json
{
  "promise_type": "task_count",
  "condition": null,
  "expected_value": "3"
}
```

**Use case:** Continue until I've tried at least 3 debugging approaches

### 2. File Exists

Stop when a specific file is created:

```json
{
  "promise_type": "file_exists",
  "condition": "src/features/new-feature.tsx"
}
```

**Use case:** Keep implementing until the feature file exists

### 3. Content Match

Stop when a file contains specific content:

```json
{
  "promise_type": "content_match",
  "condition": "src/utils/validation.ts",
  "expected_value": "export function validateInput("
}
```

**Use case:** Continue until validation logic is implemented

### 4. Custom

Define your own condition via tool implementation:

```json
{
  "promise_type": "custom",
  "condition": "my_custom_condition"
}
```

**Use case:** Complex conditions requiring custom logic (extend the plugin)

## Tools Provided

### `loop_status`

Check current loop state and whether continuation is needed.

**Parameters:** None

**Returns:** JSON with:
- `has_remaining_tasks`: true if tasks remain
- `tasks_completed`: number completed so far
- `total_tasks`: total tasks in loop
- `completion_reached`: true if all conditions met
- `blocking_issues`: list of blocking issues (if any)

### `set_completion_promise`

Set custom termination condition for the loop.

**Parameters:**
- `promise_type`: Type of condition (`task_count`, `file_exists`, `content_match`, `custom`)
- `condition`: Specific condition to check (e.g., file path, content pattern)
- `expected_value`: Expected value for condition (optional)

## Integration Patterns

### With subagent-driven-development

Use the loop to keep subagents running across sessions:

```python
# Initialize state
state_file = Path.cwd() / '.hermes-loop-state.json'
with open(state_file, 'w') as f:
    json.dump({"total_tasks": 5, "completed_tasks": 0}, f)

# Dispatch tasks via subagents (loop continues automatically)
delegate_task(goal="Implement Task 1")
mark_task_complete(state_file)

delegate_task(goal="Implement Task 2")
mark_task_complete(state_file)

# Loop will continue until all 5 tasks complete
```

### With writing-plans

Use loop for plans requiring iteration:

```python
plan = read_file("docs/plans/feature-plan.md")
tasks = parse_plan_tasks(plan)

state_file = Path.cwd() / '.hermes-loop-state.json'
with open(state_file, 'w') as f:
    json.dump({"total_tasks": len(tasks), "completed_tasks": 0}, f)

# Execute tasks (loop continues automatically across sessions)
```

### With systematic-debugging

Loop works seamlessly with debugging workflows:

```python
state_file = Path.cwd() / '.hermes-loop-state.json'
with open(state_file, 'w') as f:
    json.dump({
        "total_tasks": 10,
        "completed_tasks": 0,
        "blocking_issues": [],
        "completion_promise": {
            "promise_type": "content_match",
            "condition": "src/app.tsx",
            "expected_value": "// Bug fixed"
        }
    }, f)

# Follow systematic-debugging process:
# 1. Identify symptoms
# 2. Form hypothesis  
# 3. Test hypothesis
# 4. Update state if test fails
# 5. Loop continues until bug fixed or max iterations
```

## Debugging

### Check loop status

```python
status = loop_status()
print(f"Remaining: {status['has_remaining_tasks']}")
print(f"Completed: {status['tasks_completed']}/{status['total_tasks']}")
```

### Inspect state file directly

```bash
cat .hermes-loop-state.json
```

### Force stop the loop

If loop is stuck, remove or rename the state file:

```bash
mv .hermes-loop-state.json .hermes-loop-state.json.backup
# Loop will detect missing state and stop
```

## Extending the Plugin

To add new promise types or customize behavior:

1. **Update `schemas.py`** - Add new enum values to tool parameters
2. **Modify `tools.py`** - Implement handler logic for new features  
3. **Edit `__init__.py`** - Update `_on_stop_hook()` to evaluate new conditions

Example: Add HTTP status promise type:

```python
# In __init__.py, add to _on_stop_hook:
elif promise_type == 'http_status':
    import requests
    url = completion_promise.get('condition', '')
    response = requests.get(url)
    expected_status = int(completion_promise.get('expected_value', 200))
    promise_fulfilled = (response.status_code == expected_status)
```

## Security Considerations

### State file permissions

Ensure state files are not world-readable if they contain sensitive data:

```bash
chmod 600 .hermes-loop-state.json
```

### Validate promise conditions

Prevent path traversal attacks by validating promise conditions:

```python
def validate_promise_condition(condition: str) -> bool:
    """Prevent path traversal attacks."""
    if '..' in condition or condition.startswith('/'):
        return False  # Reject absolute paths and path traversal
    return True
```

## Comparison with Claude Code's ralph-wiggum-loop

| Feature | Hermes Loop | Ralph Wiggum Loop |
|---------|-------------|-------------------|
| Platform | Hermes Agent | Claude Code |
| State file format | JSON | JSON (similar) |
| Promise types | 4 built-in (task_count, file_exists, content_match, custom) | Similar |
| Hook integration | post_tool_call, on_session_start, stop_hook | Similar pattern |
| Tool interface | Explicit tools (loop_status, set_completion_promise) | Implicit via commands |
| Installation | ~/.hermes/plugins/ | .claude-plugin/ |

The Hermes Loop plugin follows the same conceptual model as ralph-wiggum but is adapted for Hermes Agent's tool-based architecture.

## License

MIT License - see LICENSE file in repository root

**Repository:** [https://github.com/AshMartian/hermes-loop-plugin](https://github.com/AshMartian/hermes-loop-plugin)

## Contributing

Contributions welcome! To contribute:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Update documentation
5. Submit a pull request

### Plugin structure for contributors

```
hermes-loop/
├── plugin.yaml         # Plugin manifest
├── __init__.py         # Registration and hooks
├── schemas.py          # Tool schemas (LLM-facing)
├── tools.py            # Tool handlers (implementation)
├── SKILL.md            # Usage documentation
└── README.md           # This file
```

## Resources

- [Hermes Agent Plugin Documentation](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/guides/build-a-hermes-plugin.md)
- [Subagent-Driven Development Skill](~/.hermes/skills/software-development/subagent-driven-development/SKILL.md)
- [Writing Plans Skill](~/.hermes/skills/software-development/writing-plans/SKILL.md)

## Version History

### v1.0.1 (2026-04-04)

- Cleanup and bug fixes

### v1.0.0 (2026-03-17)

- Initial release with core loop functionality
- Support for task_count, file_exists, content_match promise types
- Automatic state persistence and resumption
- Stop hook integration for loop continuation control
