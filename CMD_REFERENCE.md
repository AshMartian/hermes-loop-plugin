# Hermes Loop Plugin — Command Reference

Quick reference for all available tools. These work just like slash commands!

## Available Commands

| Command | Description | Usage Example |
|---------|-------------|---------------|
| `/loop_status` | Check current loop state | `loop_status()` |
| `/init_loop` | Initialize a new loop | `init_loop(total_tasks=5)` |
| `/complete_task` | Mark task as done | `complete_task()` |
| `/set_promise` | Set completion condition | `set_completion_promise(promise_type="file_exists", condition="src/feature.tsx")` |
| `/add_blocking_issue` | Add blocker that stops loop | `add_blocking_issue(issue="Cannot proceed without API key")` |
| `/reset_loop` | Reset completed count | `reset_loop()` |

---

## Quick Start Examples

### 1. Initialize a Loop

```python
# Basic initialization with 5 tasks
init_loop(total_tasks=5)

# With file-exists promise (stop when file created)
init_loop(
    total_tasks=7,
    promise_type="file_exists",
    condition="src/features/new-feature.tsx"
)

# With content-match promise (stop when text appears)
init_loop(
    total_tasks=5,
    promise_type="content_match",
    condition="tests/feature.test.ts",
    expected_value="describe('Feature'"
)
```

### 2. Complete Tasks

After each subagent or implementation step:

```python
# Run your work
delegate_task(goal="Implement feature step 1")

# Mark it complete
complete_task()
# Returns: {"success": true, "new_count": 1, "remaining": 4}

# Continue with next task...
delegate_task(goal="Implement feature step 2")
complete_task()
```

### 3. Check Status Anytime

```python
status = loop_status()
print(status)
# Returns: {
#   "active": true,
#   "tasks_completed": 2,
#   "total_tasks": 5,
#   "remaining_tasks": 3,
#   "completion_reached": false,
#   "blocking_issues": [],
#   "promise_status": {"has_promise": true, "fulfilled": false}
# }
```

### 4. Add Blocking Issues

When you hit an error:

```python
add_blocking_issue(issue="Cannot proceed without API key")
# Returns: {"success": true, "total_issues": 1}

# Loop will stop automatically when status shows blocking issues
```

### 5. Set Promise After Initialization

If you want to define the promise separately:

```python
set_completion_promise(
    promise_type="file_exists",
    condition="src/features/new-feature.tsx"
)

# Or update an existing promise
set_completion_promise(
    promise_type="content_match",
    condition="src/app.tsx",
    expected_value="// Bug fixed"
)
```

### 6. Reset Loop State

To restart from the beginning:

```python
reset_loop()
# Returns: {"success": true, "message": "Loop reset - cleared 2 completed tasks"}
```

---

## Real-World Patterns

### Pattern A: Feature Implementation Loop

```python
# Initialize with file-exists promise
init_loop(
    total_tasks=7,
    promise_type="file_exists",
    condition="src/features/new-feature.tsx"
)

# Execute tasks via subagents
for i in range(1, 8):
    delegate_task(goal=f"Implement feature step {i}")
    complete_task()
    
    # Check status periodically
    if i % 2 == 0:
        loop_status()

# Loop continues until file exists OR all tasks complete
```

### Pattern B: Debugging Loop with Blocking Detection

```python
# Initialize debugging session
init_loop(total_tasks=10)

# During execution, if you hit a blocker:
add_blocking_issue(issue="Cannot proceed without API key")

# Loop stops automatically when blocking issues are present
```

### Pattern C: Iterative Refinement Loop

```python
# Continue until code meets quality criteria
init_loop(
    total_tasks=5,
    promise_type="content_match",
    condition="src/component.tsx",
    expected_value="// TODO: Remove this when ready for production"
)

# Each iteration, remove the TODO comment and complete task
delegate_task(goal="Refactor component to remove TODO")
complete_task()

# Loop continues until TODO is removed or max iterations reached
```

### Pattern D: Test-Driven Loop

```python
# Continue until test file has proper structure
init_loop(
    total_tasks=5,
    promise_type="content_match",
    condition="tests/feature.test.ts",
    expected_value="describe('Feature'"
)

delegate_task(goal="Write feature tests")
complete_task()

# Loop continues until describe block appears in test file
```

---

## Promise Types Reference

### task_count
Stop after completing N tasks:

```python
init_loop(
    total_tasks=10,
    promise_type="task_count",
    expected_value="3"  # Stop after 3 iterations
)
```

### file_exists
Stop when a specific file is created:

```python
init_loop(
    total_tasks=5,
    promise_type="file_exists",
    condition="src/features/new-feature.tsx"
)
```

### content_match
Stop when a file contains specific text:

```python
init_loop(
    total_tasks=5,
    promise_type="content_match",
    condition="src/utils/validation.ts",
    expected_value="export function validateInput("
)
```

---

## Troubleshooting Commands

### Check if loop is active

```python
status = loop_status()
if status.get('active'):
    print(f"Loop running: {status['tasks_completed']}/{status['total_tasks']} tasks")
else:
    print("No active loop state found")
```

### Force stop a stuck loop

```python
# Option 1: Add blocking issue to trigger stop
add_blocking_issue(issue="Force stopping due to timeout")

# Option 2: Reset the loop (clears completed count)
reset_loop()
```

### View current state file directly

```bash
cat .hermes-loop-state.json
```

---

## Integration with subagent-driven-development

Complete workflow combining both skills:

```python
from pathlib import Path

# 1. Initialize loop state
init_loop(
    total_tasks=5,
    promise_type="task_count",
    expected_value="3"
)

# 2. Create task plan
plan = """
TASK LIST:
1. Create User model with email field
2. Add password hashing utility  
3. Create login endpoint
4. Add JWT token generation
5. Create registration endpoint
"""

# 3. Execute tasks via subagents (loop continues automatically)
for i in range(1, 6):
    delegate_task(
        goal=f"Implement Task {i}",
        context=plan
    )
    
    # Update state after each task
    complete_task()

# Loop will continue until all tasks complete OR promise stops it at task 3
```

---

## Key Points to Remember

1. **Always call `complete_task()`** after completing each subagent/implement step
2. **Completion promises are optional** but recommended for custom termination conditions  
3. **Blocking issues stop the loop immediately** — use when you hit a blocker
4. **Loop resumes across sessions automatically** if you close and reopen Hermes
5. **Use `loop_status()` anytime** to inspect current state

---

## Tool vs Command

These tools work exactly like slash commands:

```python
# Works just as well as calling a tool directly
init_loop(total_tasks=5)

# Or with full parameters
init_loop(
    total_tasks=7,
    promise_type="file_exists",
    condition="src/feature.tsx"
)
```

The tools are designed to be intuitive and command-like for easy usage!
