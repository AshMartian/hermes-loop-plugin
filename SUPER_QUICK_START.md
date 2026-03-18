# Hermes Loop Plugin — Super Quick Start (30 seconds!)

## The 4 Commands You Need to Know

### 1. Initialize the loop
```python
init_loop(total_tasks=5)
```

### 2. Run your work and mark complete
```python
delegate_task(goal="Implement feature")
complete_task()
```

### 3. Check status anytime
```python
loop_status()
# Returns: tasks_completed, total_tasks, remaining, etc.
```

### 4. Set custom termination (optional)
```python
set_completion_promise(
    promise_type="file_exists", 
    condition="src/feature.tsx"
)
```

---

## Complete Example (Copy & Paste!)

```python
from pathlib import Path

# Step 1: Initialize with file-exists promise
init_loop(
    total_tasks=7,
    promise_type="file_exists",
    condition="src/features/new-feature.tsx"
)

# Step 2: Run tasks via subagents (loop continues automatically!)
for i in range(1, 8):
    delegate_task(goal=f"Implement feature step {i}")
    complete_task()
    
    # Check status every 2 steps
    if i % 2 == 0:
        loop_status()

# Loop stops when file exists OR all 7 tasks complete!
```

---

## Common Patterns

### Pattern A: Debugging until fixed
```python
init_loop(
    total_tasks=10,
    promise_type="content_match",
    condition="src/app.tsx",
    expected_value="// Bug fixed"
)
# Loop continues until comment "// Bug fixed" appears in app.tsx
```

### Pattern B: Stop when blocked
```python
init_loop(total_tasks=5)

# During execution, hit a blocker:
add_blocking_issue(issue="Cannot proceed without API key")
# Loop stops immediately!
```

### Pattern C: Simple task count stop
```python
init_loop(
    total_tasks=10,
    promise_type="task_count",
    expected_value="3"  # Stop after 3 iterations
)
```

---

## What Happens Next?

The loop **automatically continues** until ONE of these conditions is met:
- ✅ All tasks complete (`completed_tasks >= total_tasks`)
- ✅ File exists (for `file_exists` promise)
- ✅ Content appears in file (for `content_match` promise)
- ❌ Blocking issue detected (stops immediately!)

You don't need to manually check or continue — the plugin handles it via hooks!

---

## Need Help?

See full documentation: **CMD_REFERENCE.md** or **SKILL.md**
