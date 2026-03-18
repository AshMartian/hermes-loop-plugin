# Hermes Loop Plugin - Quick Start Guide

## 30-Second Overview

The hermes-loop plugin keeps your agent running continuously until tasks are completed, using state file monitoring and optional completion promises.

## Basic Usage (3 Steps)

### Step 1: Initialize the loop state

Create a `.hermes-loop-state.json` in your working directory:

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

print("Loop initialized!")
```

### Step 2: Set completion promise (optional)

Define custom termination conditions using the tool:

```python
set_completion_promise(
    promise_type="content_match",
    condition="tests/feature.test.ts",
    expected_value="describe('Feature'"
)
```

### Step 3: Execute tasks and update state

Run your tasks via subagents, updating state after each completion:

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

**That's it!** The loop continues automatically until all conditions are met.

## Completion Promise Types

### Task Count
Stop after completing N tasks:

```python
set_completion_promise(
    promise_type="task_count",
    expected_value="3"  # Stop after 3 iterations
)
```

### File Exists
Stop when a file is created:

```python
set_completion_promise(
    promise_type="file_exists",
    condition="src/features/new-feature.tsx"
)
```

### Content Match
Stop when a file contains specific content:

```python
set_completion_promise(
    promise_type="content_match",
    condition="src/utils/validation.ts",
    expected_value="export function validateInput("
)
```

## Checking Loop Status

Use the `loop_status` tool to inspect current state:

```python
status = loop_status()
print(f"Remaining tasks: {status['has_remaining_tasks']}")
print(f"Completed: {status['tasks_completed']}/{status['total_tasks']}")
print(f"Blocking issues: {status['blocking_issues']}")
```

## Real-World Example: Debugging Loop

Debug an issue through multiple iterations until fixed:

```python
from pathlib import Path
import json

# Initialize debugging loop
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
# 4. Update state if test fails (completed_tasks++)
# 5. Loop continues until bug fixed or max iterations

# During execution, if you hit a blocker:
state_file.write_text(json.dumps({
    "total_tasks": 10,
    "completed_tasks": 2,
    "blocking_issues": ["Cannot proceed without API key"],
    "completion_promise": {...}
}))

# Loop will stop and signal user intervention needed
```

## Integration with subagent-driven-development

Keep subagents running across sessions:

```python
from pathlib import Path
import json

state_file = Path.cwd() / '.hermes-loop-state.json'

with open(state_file, 'w') as f:
    json.dump({
        "total_tasks": 5,
        "completed_tasks": 0,
        "blocking_issues": [],
        "completion_promise": None
    }, f)

# Dispatch tasks via subagents (loop continues automatically)
for i in range(1, 6):
    delegate_task(goal=f"Implement Task {i}")
    
    # Update state after each task
    with open(state_file) as f:
        state = json.load(f)
    state['completed_tasks'] += 1
    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)

# Loop will continue until all 5 tasks complete
```

## Common Patterns

### Pattern 1: Feature Implementation Loop

```python
state = {
    "total_tasks": 7,
    "completed_tasks": 0,
    "blocking_issues": [],
    "completion_promise": {
        "promise_type": "file_exists",
        "condition": "src/features/new-feature.tsx"
    }
}

with open('.hermes-loop-state.json', 'w') as f:
    json.dump(state, f)
```

### Pattern 2: Test-Driven Loop

```python
state = {
    "total_tasks": 5,
    "completed_tasks": 0,
    "blocking_issues": [],
    "completion_promise": {
        "promise_type": "content_match",
        "condition": "tests/feature.test.ts",
        "expected_value": "describe('Feature'"
    }
}
```

### Pattern 3: Iterative Refinement Loop

```python
state = {
    "total_tasks": 5,
    "completed_tasks": 0,
    "blocking_issues": [],
    "completion_promise": {
        "promise_type": "content_match",
        "condition": "src/component.tsx",
        "expected_value": "// TODO: Remove this when ready for production"
    }
}

# Loop continues until TODO comment is removed
```

## Troubleshooting

### Loop won't stop

Check completion promise condition:

```python
status = loop_status()
print(f"Promise fulfilled: {status.get('promise_status', {}).get('fulfilled')}")
```

### State file missing

Initialize a new state file (loop will start fresh):

```bash
# Create new state file
touch .hermes-loop-state.json
echo '{"total_tasks": 0, "completed_tasks": 0}' > .hermes-loop-state.json
```

### Force stop the loop

Remove or rename the state file:

```bash
mv .hermes-loop-state.json .hermes-loop-state.json.backup
# Loop will detect missing state and stop
```

## Next Steps

For detailed usage, see the full [SKILL.md](../SKILL.md) documentation.
