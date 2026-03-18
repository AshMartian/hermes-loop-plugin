# Hermes Loop Plugin - Quick Start Guide

## ⏱️ Read Time: 3-5 Minutes

Get up and running with the Hermes Loop plugin in under 5 minutes. This guide covers everything you need to start using the loop tools effectively.

---

## Prerequisites (1 minute)

Ensure Python 3.8+ is installed on your system. Verify with:

```bash
python --version
```

---

## Installation (1 minute)

Install the plugin with a single command:

```bash
pip install hermes-loop-plugin
```

Verify installation:

```bash
hermes --list-tools | grep loop
```

You should see 6 tools listed. If not, restart your terminal and try again.

---

## Basic Usage (2 minutes)

### Step 1: Initialize Your Loop

Every workflow starts with `init_loop`. Define how many tasks you'll execute:

```python
# Simple 5-task loop
init_loop(total_tasks=5)
```

That's it! The loop is now active and ready to track progress.

### Step 2: Execute Tasks and Mark Completion

Run your operations, then mark each task complete:

```python
# Example workflow
process_task_1()
complete_task()  # Marks task 1 done

process_task_2()
complete_task()  # Marks task 2 done

# Continue for all tasks...
```

### Step 3: Monitor Progress

Check your loop status anytime during execution:

```python
status = loop_status()
print(f"Progress: {status['tasks_remaining']} tasks remaining")
```

Sample output:
```json
{
    "tasks_remaining": 2,
    "total_tasks": 5,
    "completion_reached": false,
    "blocking_issues": []
}
```

---

## Handling Problems (1 minute)

When something goes wrong, don't force the loop to continue. Flag issues instead:

```python
if database_unavailable():
    add_blocking_issue("Database connection failed - cannot proceed")
```

The loop will automatically stop when a blocking issue is added, preventing further execution on broken state.

---

## Advanced Features (Optional)

### Custom Completion Conditions

Instead of just counting tasks, you can set conditions for automatic completion:

#### Wait for File Creation

```python
init_loop(
    total_tasks=5,
    promise_type='file_exists',
    condition='/path/to/build/output.txt'
)
# Loop completes automatically when file appears
```

#### Validate Content

```python
init_loop(
    total_tasks=3,
    promise_type='content_match',
    condition='/var/log/app.log',
    expected_value='Initialization complete'
)
# Loop completes when log contains expected message
```

### Reset Without Losing Configuration

Need to retry? Reset the loop state while keeping settings:

```python
reset_loop()  # Clears progress, keeps total_tasks and promise settings
```

---

## Complete Example Workflow

Here's a full example you can adapt:

```python
from hermes_loop import init_loop, complete_task, add_blocking_issue, loop_status

# Step 1: Initialize with 3 tasks
init_loop(total_tasks=3)

# Step 2: Process each item
files = ['data1.csv', 'data2.csv', 'data3.csv']

for file in files:
    # Check prerequisites
    if not os.path.exists(file):
        add_blocking_issue(f"File missing: {file}")
        break
    
    try:
        process_file(file)
        
        # Validate result
        if validate_result():
            complete_task()
        else:
            add_blocking_issue("Result validation failed")
    
    except Exception as e:
        add_blocking_issue(f"Error processing {file}: {str(e)}")

# Step 3: Check final status
status = loop_status()
print(f"Completed: {len(files) - status['tasks_remaining']}/{len(files)} files")
```

---

## Quick Reference Cheat Sheet

| Action | Command |
|--------|---------|
| Start a new loop | `init_loop(total_tasks=N)` |
| Mark task done | `complete_task()` |
| Check progress | `loop_status()` |
| Flag blocking issue | `add_blocking_issue("description")` |
| Reset without losing config | `reset_loop()` |
| Custom completion condition | `set_completion_promise(...)` |

---

## Next Steps

- **Deep Dive:** Read [USER_GUIDE.md](./USER_GUIDE.md) for detailed examples of all 6 tools
- **Setup Details:** See [INSTALLATION.md](./INSTALLATION.md) for advanced installation options and troubleshooting

---

## Common Patterns to Remember

1. **Always start with `init_loop`** - No loop state without initialization
2. **Use `add_blocking_issue` for errors** - Don't continue on problems, flag them
3. **Check status regularly** - Monitor progress with `loop_status()`
4. **Choose appropriate promise type** - Match your completion criteria

---

## Troubleshooting Quick Fixes

| Problem | Solution |
|---------|----------|
| Tools not found after install | Restart terminal or run `export PATH="$HOME/.local/bin:$PATH"` |
| Loop won't start | Ensure `init_loop` was called with valid `total_tasks` |
| Tasks not counting up | Call `complete_task()` after each operation |
| Loop never ends | Check your promise condition can actually be met |

---

**You're ready to go!** Start building loop-based workflows with confidence. For more advanced features, explore the full user guide.
