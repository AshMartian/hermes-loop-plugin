---
name: hermes-loop
description: Continuous task execution loop — keeps agent running until goals completed via state file monitoring and completion promises. Use for multi-step tasks requiring persistent iteration.
version: 1.0.0
author: Hermes Agent Community
license: MIT
tags: [loop, iteration, persistence, state-management]
metadata:
  hermes:
    tags: [loop, iteration, persistence, state-management]
    related_skills: [subagent-driven-development, writing-plans, systematic-debugging]
---

# Hermes Loop Plugin

Continuous task execution loop that keeps the agent running until goals are completed. Uses state file monitoring and optional completion promises to control when the loop should stop.

## Overview

The hermes-loop plugin enables **persistent multi-step workflows** where tasks span multiple sessions or require iterative refinement. Unlike single-shot tools, this plugin maintains execution state and automatically resumes work until completion conditions are met.

### Key Features

- **State Persistence**: Tracks task progress via `.hermes-loop-state.json`
- **Completion Promises**: Define custom termination conditions beyond simple task counts
- **Automatic Resumption**: Continues from where it left off across sessions
- **Blocking Detection**: Stops loop when critical issues prevent progress
- **Tool Integration**: Provides `loop_status` and `set_completion_promise` tools

## When to Use

Use this skill when:

- Tasks require **multiple iterations** before completion
- Work spans **multiple agent sessions** (need state persistence)
- You need **custom termination conditions** beyond task count
- Tasks may encounter **blocking issues** that should halt the loop
- You want **automatic resumption** across session boundaries

### Examples

✅ **Good use cases:**
- "Implement a feature with 5 subtasks, each requiring review"
- "Debug an issue through multiple iterations until fixed"
- "Build a component that passes all tests before completion"
- "Research and implement until you find a working solution"

❌ **Not needed for:**
- Single-step tasks (use direct implementation)
- Tasks with guaranteed single-pass completion
- Simple tool calls without state requirements

## Core Concepts

### State File: `.hermes-loop-state.json`

The plugin uses a JSON state file to track execution progress. Located in the working directory by default.

```json
{
  "total_tasks": 5,
  "completed_tasks": 2,
  "blocking_issues": [],
  "completion_promise": null,
  "created_at": "2026-03-17T09:38:00Z"
}
```

**Fields:**
- `total_tasks`: Total number of tasks in the loop
- `completed_tasks`: Number of tasks completed so far
- `blocking_issues`: List of issues that should stop the loop
- `completion_promise`: Optional custom termination condition (see below)
- `created_at`: Timestamp when loop started

### Completion Promises

Completion promises define **custom conditions** for when the loop should stop. Beyond simple task count, you can specify:

#### 1. Task Count Promise

Stop after completing a specific number of tasks:

```json
{
  "promise_type": "task_count",
  "condition": null,
  "expected_value": "3",
  "fulfilled": false
}
```

**Use case:** "Continue until I've tried at least 3 debugging approaches"

#### 2. File Exists Promise

Stop when a specific file is created:

```json
{
  "promise_type": "file_exists",
  "condition": "src/features/new-feature.tsx",
  "expected_value": null,
  "fulfilled": false
}
```

**Use case:** "Keep implementing until the feature file exists"

#### 3. Content Match Promise

Stop when a file contains specific content:

```json
{
  "promise_type": "content_match",
  "condition": "src/utils/validation.ts",
  "expected_value": "export function validateInput(",
  "fulfilled": false
}
```

**Use case:** "Continue until validation logic is implemented"

#### 4. Custom Promise

Define your own condition via tool implementation:

```json
{
  "promise_type": "custom",
  "condition": "my_custom_condition",
  "expected_value": null,
  "fulfilled": false
}
```

**Use case:** Complex conditions requiring custom logic (extend the plugin)

## Usage Patterns

### Pattern 1: Basic Task Loop with Completion Promise

**Goal:** Implement a feature through multiple iterations until tests pass.

```python
# Step 1: Initialize the loop state
from pathlib import Path

state_file = Path.cwd() / '.hermes-loop-state.json'
with open(state_file, 'w') as f:
    json.dump({
        "total_tasks": 5,
        "completed_tasks": 0,
        "blocking_issues": [],
        "completion_promise": {
            "promise_type": "content_match",
            "condition": "tests/feature.test.ts",
            "expected_value": "describe('Feature'",
            "fulfilled": False
        }
    }, f)

# Step 2: Set completion promise via tool
set_completion_promise(
    promise_type="content_match",
    condition="tests/feature.test.ts",
    expected_value="describe('Feature'"
)

# Step 3: Execute tasks (via delegate_task or direct implementation)
delegate_task(goal="Implement feature step 1")
delegate_task(goal="Implement feature step 2")

# Step 4: Update state after each task
state_file.write_text(json.dumps({
    "total_tasks": 5,
    "completed_tasks": 2,
    "blocking_issues": [],
    "completion_promise": {...}
}))

# Loop continues automatically via stop_hook until promise fulfilled or all tasks complete
```

### Pattern 2: Debugging Loop with Blocking Detection

**Goal:** Debug an issue through multiple attempts, stopping if blocked.

```python
# Initialize loop for debugging session
state_file = Path.cwd() / '.hermes-loop-state.json'

with open(state_file, 'w') as f:
    json.dump({
        "total_tasks": 10,
        "completed_tasks": 0,
        "blocking_issues": [],
        "completion_promise": {
            "promise_type": "task_count",
            "condition": null,
            "expected_value": "5",
            "fulfilled": False
        }
    }, f)

# During execution, if you hit a blocker:
state_file.write_text(json.dumps({
    "total_tasks": 10,
    "completed_tasks": 2,
    "blocking_issues": ["Cannot proceed without API key"],
    "completion_promise": {...}
}))

# Loop will stop and signal user intervention needed
```

### Pattern 3: Iterative Refinement Loop

**Goal:** Refine code until it meets quality criteria.

```python
# Set up refinement loop
state_file = Path.cwd() / '.hermes-loop-state.json'

with open(state_file, 'w') as f:
    json.dump({
        "total_tasks": 5,
        "completed_tasks": 0,
        "blocking_issues": [],
        "completion_promise": {
            "promise_type": "content_match",
            "condition": "src/component.tsx",
            "expected_value": "// TODO: Remove this when ready for production"
        }
    }, f)

# Each iteration:
# 1. Make changes to src/component.tsx
# 2. Update completed_tasks counter
# 3. Continue until promise fulfilled (TODO removed) or max iterations reached
```

## Tool Reference

### `loop_status`

Check current loop state and whether continuation is needed.

**Parameters:** None

**Returns:** JSON with:
- `has_remaining_tasks`: true if tasks remain
- `tasks_completed`: number completed so far
- `total_tasks`: total tasks in loop
- `completion_reached`: true if all conditions met
- `blocking_issues`: list of blocking issues (if any)
- `state_file_path`: path to state file

**Example:**
```python
status = loop_status()
print(status)
# Output: {"has_remaining_tasks": true, "tasks_completed": 2, ...}
```

### `set_completion_promise`

Set custom termination condition for the loop.

**Parameters:**
- `promise_type`: Type of condition (`task_count`, `file_exists`, `content_match`, `custom`)
- `condition`: Specific condition to check (e.g., file path, content pattern)
- `expected_value`: Expected value for condition (optional)

**Example:**
```python
set_completion_promise(
    promise_type="file_exists",
    condition="src/features/new-feature.tsx"
)
```

## State Management Best Practices

### Updating Task Progress

Always update the state file after completing a task:

```python
def mark_task_complete(state_file: Path):
    """Increment completed_tasks counter."""
    with open(state_file) as f:
        state = json.load(f)
    
    state['completed_tasks'] += 1
    
    # Optional: add timestamp for each completion
    if 'completion_history' not in state:
        state['completion_history'] = []
    state['completion_history'].append({
        "task_index": state['completed_tasks'],
        "timestamp": datetime.now().isoformat()
    })
    
    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)
```

### Adding Blocking Issues

Mark tasks as blocked when critical issues prevent progress:

```python
def add_blocking_issue(state_file: Path, issue: str):
    """Add a blocking issue that stops the loop."""
    with open(state_file) as f:
        state = json.load(f)
    
    if issue not in state['blocking_issues']:
        state['blocking_issues'].append(issue)
        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2)
    
    logger.warning(f"[loop] Blocking issue added: {issue}")
```

### Reading State Safely

Always handle missing or corrupted state files:

```python
def read_state_safe(state_file: Path) -> dict:
    """Read state file with error handling."""
    if not state_file.exists():
        return {"total_tasks": 0, "completed_tasks": 0}
    
    try:
        with open(state_file) as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Failed to read state file: {e}")
        return {"total_tasks": 0, "completed_tasks": 0}
```

## Integration with Other Skills

### With `subagent-driven-development`

The loop plugin **complements** subagent workflows by keeping them running across sessions:

```python
# Use subagent for each task within the loop
delegate_task(
    goal="Implement Task 1",
    context="""
    TASK FROM LOOP STATE:
    - Total tasks in loop: 5
    - Currently at: task 1 of 5
    
    FOLLOW TDD:
    1. Write test
    2. Implement minimal code
    3. Verify tests pass
    """
)

# After completion, update state
mark_task_complete(Path.cwd() / '.hermes-loop-state.json')
```

### With `writing-plans`

Use loop for plans that require iteration:

```python
plan = read_file("docs/plans/feature-plan.md")

# Extract tasks from plan
tasks = parse_plan_tasks(plan)  # Your parsing logic

state_file = Path.cwd() / '.hermes-loop-state.json'
with open(state_file, 'w') as f:
    json.dump({
        "total_tasks": len(tasks),
        "completed_tasks": 0,
        "blocking_issues": [],
        "completion_promise": None
    }, f)

# Execute tasks via subagents (loop continues automatically)
```

### With `systematic-debugging`

Loop works seamlessly with debugging workflows:

```python
# Initialize loop for debugging session
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
# 4. Update state (completed_tasks++) if test fails
# 5. Loop continues until bug fixed or max iterations
```

## Common Pitfalls

### ❌ Forgetting to update state file

**Problem:** Agent completes tasks but doesn't increment counter, loop never ends.

**Solution:** Always call `mark_task_complete()` after each task:

```python
# Correct pattern
delegate_task(goal="Implement feature")
state_file = Path.cwd() / '.hermes-loop-state.json'
mark_task_complete(state_file)  # ← Don't forget this!
```

### ❌ Setting impossible completion promises

**Problem:** Promise condition can never be met, loop runs forever.

**Solution:** Ensure promise conditions are achievable:

```python
# Bad: expects content that will never exist
completion_promise = {
    "promise_type": "content_match",
    "condition": "src/never-created.tsx",  # This file won't be created
    "expected_value": "hello"
}

# Good: realistic condition
completion_promise = {
    "promise_type": "file_exists",
    "condition": "src/features/new-feature.tsx"
}
```

### ❌ Not handling missing state files

**Problem:** Agent crashes when state file doesn't exist.

**Solution:** Always check for existence before reading:

```python
state_file = Path.cwd() / '.hermes-loop-state.json'
if not state_file.exists():
    # Either initialize new loop or exit gracefully
    logger.warning("No active loop state, initializing fresh")
    initialize_loop_state(state_file)
```

### ❌ Mixing multiple loop plugins

**Problem:** Running two different loop plugins simultaneously causes conflicts.

**Solution:** Use only one loop plugin per session:

```python
# Good: single source of truth for loop state
state_file = Path.cwd() / '.hermes-loop-state.json'

# Bad: don't mix hermes-loop with other loop systems
other_loop_state = Path.cwd() / '.ralph-state.json'  # Avoid this!
```

## Debugging Loop Issues

### Check if loop is running

Use `loop_status` tool to inspect current state:

```python
status = loop_status()
print(f"Remaining tasks: {status['has_remaining_tasks']}")
print(f"Completed: {status['tasks_completed']}/{status['total_tasks']}")
print(f"Blocking issues: {status['blocking_issues']}")
```

### Inspect state file directly

```bash
cat ~/.hermes-loop-state.json
# or in current directory
cat .hermes-loop-state.json
```

### Test promise evaluation manually

```python
from pathlib import Path

state_file = Path.cwd() / '.hermes-loop-state.json'
with open(state_file) as f:
    state = json.load(f)

promise = state.get('completion_promise')
if promise:
    print(f"Promise type: {promise['promise_type']}")
    print(f"Condition: {promise['condition']}")
    
    # Manually evaluate based on type
    if promise['promise_type'] == 'file_exists':
        check_path = Path.cwd() / promise['condition']
        print(f"File exists: {check_path.exists()}")
```

### Force stop the loop

If loop is stuck, remove or rename the state file:

```bash
mv .hermes-loop-state.json .hermes-loop-state.json.backup
# Loop will detect missing state and stop
```

## Extending the Plugin

### Adding new promise types

To add a custom completion condition type:

1. Update `schemas.py` to include new enum value
2. Modify `tools.py` handler to accept new parameters
3. Update `_on_stop_hook()` in `__init__.py` to evaluate new type

Example: Add `http_status` promise type that stops when API returns 200:

```python
# In __init__.py, add to _on_stop_hook:
elif promise_type == 'http_status':
    import requests
    url = completion_promise.get('condition', '')
    response = requests.get(url)
    expected_status = int(completion_promise.get('expected_value', 200))
    promise_fulfilled = (response.status_code == expected_status)
```

### Custom state fields

Add custom tracking fields to the state file:

```python
state_file = Path.cwd() / '.hermes-loop-state.json'

with open(state_file, 'w') as f:
    json.dump({
        "total_tasks": 5,
        "completed_tasks": 0,
        "blocking_issues": [],
        "custom_metrics": {
            "iterations": 0,
            "last_review_time": None,
            "effort_score": 0.85
        },
        "completion_promise": {...}
    }, f)
```

## Platform-Specific Notes

### macOS/Linux

State file paths use standard POSIX path resolution:

```python
from pathlib import Path
state_file = Path.cwd() / '.hermes-loop-state.json'  # Works on all Unix systems
```

### Windows

Path resolution works via `pathlib`, no special handling needed:

```python
# This works identically on Windows
state_file = Path.cwd() / '.hermes-loop-state.json'
```

## Security Considerations

### State file permissions

Ensure state files are not world-readable if they contain sensitive data:

```bash
chmod 600 .hermes-loop-state.json
```

### Promise condition injection

Validate promise conditions to prevent path traversal:

```python
def validate_promise_condition(condition: str) -> bool:
    """Prevent path traversal attacks."""
    if '..' in condition or condition.startswith('/'):
        return False  # Reject absolute paths and path traversal
    return True
```

## Related Skills

- **subagent-driven-development**: For dispatching tasks within the loop
- **writing-plans**: For creating structured task lists to iterate over
- **systematic-debugging**: For debugging workflows that require iteration
- **test-driven-development**: For implementing TDD within loop iterations

## Changelog

### v1.0.0 (2026-03-17)

- Initial release with core loop functionality
- Support for task_count, file_exists, content_match promise types
- Automatic state persistence and resumption
- Stop hook integration for loop continuation control
