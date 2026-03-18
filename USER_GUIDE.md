# Hermes Loop Plugin - User Guide

## Overview

This guide provides comprehensive documentation and usage examples for all 6 tools in the Hermes Loop plugin. Whether you're a beginner or experienced user, this guide will help you effectively manage task execution loops.

## Quick Reference Table

| Tool | Purpose | When to Use |
|------|---------|-------------|
| `init_loop` | Initialize loop with parameters | Start of every loop workflow |
| `loop_status` | Check progress and state | Debugging, monitoring during execution |
| `complete_task` | Mark task complete | After each successful task completion |
| `add_blocking_issue` | Flag blocking problems | When issues prevent further progress |
| `reset_loop` | Reset without losing config | Need to restart loop with same settings |
| `set_completion_promise` | Define custom termination | Advanced control over loop exit conditions |

---

## Tool 1: init_loop - Initialize Loop

### Purpose

Initialize a new task execution loop with configurable parameters. This is the first tool you call when starting a new workflow.

### Parameters

- **total_tasks** (required): Total number of tasks in the loop
- **promise_type** (optional): Completion promise type ('task_count', 'file_exists', 'content_match')
- **condition** (optional): Path/pattern for the promise condition
- **expected_value** (optional): Expected value for content_match promises

### Basic Usage

```python
# Initialize a simple loop with 10 tasks
init_loop(total_tasks=10)
```

### Advanced Examples

#### Example 1: Loop with task_count promise

```python
# Loop that completes after all tasks are done
init_loop(
    total_tasks=25,
    promise_type='task_count',
    condition='all_complete'
)
```

#### Example 2: Loop monitoring file existence

```python
# Loop continues until a build artifact is created
init_loop(
    total_tasks=10,
    promise_type='file_exists',
    condition='/path/to/build/output/dist/index.html'
)
```

#### Example 3: Loop with content validation

```python
# Loop validates response contains expected data
init_loop(
    total_tasks=5,
    promise_type='content_match',
    condition='/var/log/app.log',
    expected_value='Initialization complete'
)
```

### Common Patterns

#### Pattern 1: Data Processing Pipeline

```python
# Initialize loop for processing multiple files
files = ['data1.csv', 'data2.csv', 'data3.csv']
init_loop(
    total_tasks=len(files),
    promise_type='task_count'
)
```

#### Pattern 2: API Retry Loop

```python
# Initialize with retry capability
init_loop(
    total_tasks=5,  # Max retries
    promise_type='content_match',
    condition='/tmp/api_status.json',
    expected_value='"status": "success"'
)
```

---

## Tool 2: loop_status - Check Loop Status

### Purpose

Check the current status of task execution loops. Returns whether tasks remain, if completion is reached, and any blocking issues. Use this for debugging or monitoring.

### Parameters

No parameters required. The tool automatically detects active loops.

### Basic Usage

```python
# Get current loop status
loop_status()
```

### Response Format

The tool returns:

```json
{
    "tasks_remaining": 7,
    "total_tasks": 10,
    "completion_reached": false,
    "blocking_issues": [],
    "promise_type": "task_count",
    "condition": null
}
```

### Usage Examples

#### Example 1: Monitoring Progress

```python
# Check progress during loop execution
status = loop_status()
print(f"Progress: {status['tasks_remaining']}/{status['total_tasks']} remaining")

if status['completion_reached']:
    print("Loop completed!")
```

#### Example 2: Debugging Blocking Issues

```python
status = loop_status()
if status['blocking_issues']:
    print("Blocking issues detected:")
    for issue in status['blocking_issues']:
        print(f"  - {issue}")
```

#### Example 3: Verifying Promise State

```python
# Check if completion promise is active
status = loop_status()
print(f"Promise type: {status.get('promise_type', 'none')}")
print(f"Condition: {status.get('condition', 'N/A')}")
```

### Common Patterns

#### Pattern 1: Progress Logging

```python
# Log progress every N tasks
if status['tasks_remaining'] % 5 == 0 and status['tasks_remaining'] > 0:
    print(f"Current progress: {status['total_tasks'] - status['tasks_remaining']}/{status['total_tasks']}")
```

#### Pattern 2: Early Exit Detection

```python
# Check if we should exit early due to blocking issue
if not status['completion_reached'] and status['blocking_issues']:
    print("Exiting loop due to blocking issues")
    # Take appropriate action
```

---

## Tool 3: complete_task - Complete Current Task

### Purpose

Mark the next task as completed. This increments the completed tasks counter and updates progress tracking.

### Parameters

No parameters required. The tool automatically tracks which task is next.

### Basic Usage

```python
# Mark current task as complete
complete_task()
```

### Usage Examples

#### Example 1: Simple Task Completion

```python
# After completing a data processing step
process_file('input.csv')
complete_task()
```

#### Example 2: Conditional Completion

```python
if validate_result(result):
    complete_task()
else:
    add_blocking_issue("Invalid result detected")
```

#### Example 3: Batch Completion with Logging

```python
for item in items:
    process(item)
    if should_complete():
        print(f"Completed task for {item}")
        complete_task()
```

### Common Patterns

#### Pattern 1: Error Handling Before Completion

```python
try:
    result = perform_operation()
    validate(result)
    complete_task()
except Exception as e:
    add_blocking_issue(f"Operation failed: {str(e)}")
```

#### Pattern 2: Task Grouping

```python
# Complete a logical group of operations
with task_group("data_sync"):
    sync_database()
    update_cache()
    refresh_index()
    complete_task()  # Marks entire group as done
```

---

## Tool 4: add_blocking_issue - Add Blocking Issue

### Purpose

Add a description of issues that block progress. When blocking issues are added, the loop stops automatically to prevent further execution on problematic state.

### Parameters

- **issue** (required): Description of the blocking issue

### Basic Usage

```python
# Flag an issue that prevents continuation
add_blocking_issue("Database connection failed")
```

### Usage Examples

#### Example 1: Resource Unavailable

```python
if not resource_available():
    add_blocking_issue("Required resource 'database' is unavailable")
```

#### Example 2: Validation Failure

```python
if not validate_output(result):
    add_blocking_issue(f"Output validation failed: {result.error}")
```

#### Example 3: External Dependency Issue

```python
if api_status != 'healthy':
    add_blocking_issue(f"External API unhealthy (status: {api_status})")
```

### Common Patterns

#### Pattern 1: Comprehensive Error Reporting

```python
def check_dependencies():
    issues = []
    
    if not db_connected():
        issues.append("Database connection failed")
    
    if not cache_available():
        issues.append("Cache service unavailable")
    
    if issues:
        add_blocking_issue("\n".join(issues))
```

#### Pattern 2: Context-Rich Issue Reporting

```python
def handle_error(error):
    context = {
        'task_id': current_task_id,
        'timestamp': datetime.now().isoformat(),
        'error_type': type(error).__name__
    }
    add_blocking_issue(f"Error in task {context['task_id']}: {str(error)}\nContext: {json.dumps(context)}")
```

#### Pattern 3: Cascading Failure Detection

```python
def detect_cascading_failures():
    if primary_failing() and secondary_unavailable():
        add_blocking_issue("Cascading failure detected - both primary and secondary systems affected")
```

---

## Tool 5: reset_loop - Reset Loop State

### Purpose

Reset the loop state while keeping total tasks and promise configuration intact. Use this when you need to restart a loop without reinitializing parameters.

### Parameters

No parameters required. The tool automatically preserves configuration.

### Basic Usage

```python
# Reset to beginning of loop with same settings
reset_loop()
```

### Usage Examples

#### Example 1: Manual Restart After Error Recovery

```python
try:
    # Attempt operation that might fail
    risky_operation()
except RecoverableError:
    add_blocking_issue("Recoverable error detected")
    # After fixing the issue...
    reset_loop()
    # Continue from start with same configuration
```

#### Example 2: Iterative Refinement Loop

```python
for iteration in range(3):
    try:
        result = refine_solution(current)
        if validate(result):
            complete_task()
            break
    except Exception as e:
        add_blocking_issue(f"Iteration {iteration} failed")
    
    # Reset to retry with same initial conditions
    reset_loop()
```

#### Example 3: State Cleanup Between Runs

```python
# Clean up state before starting fresh
cleanup_temp_files()
reset_loop()
init_loop(total_tasks=10)  # Reinitialize if needed
```

### Common Patterns

#### Pattern 1: Safe Reset with Confirmation

```python
def safe_reset():
    status = loop_status()
    print(f"Resetting loop: {status['tasks_remaining']} tasks remaining")
    
    # Confirm before reset (in interactive mode)
    if confirm_reset():
        reset_loop()
        print("Loop state reset successfully")
```

#### Pattern 2: Reset After External Changes

```python
# When external factors change, reset loop
if external_condition_changed():
    print("External conditions changed, resetting loop")
    reset_loop()
    # Loop will re-evaluate with new conditions
```

---

## Tool 6: set_completion_promise - Set Completion Promise

### Purpose

Define custom termination conditions for loops. The loop continues until either all tasks complete OR this promise is fulfilled. Use this for advanced control over loop exit behavior.

### Parameters

- **promise_type** (required): Type of completion condition
  - `'task_count'`: Complete after N tasks
  - `'file_exists'`: Complete when file appears
  - `'content_match'`: Complete when content matches pattern
  - `'custom'`: Custom logic implementation
- **condition** (required): The specific condition to check
- **expected_value** (optional): Expected value for the condition

### Promise Types Explained

#### task_count: Task-Based Completion

```python
# Loop completes after exactly 10 tasks are marked complete
set_completion_promise(
    promise_type='task_count',
    condition='10'
)
```

#### file_exists: File-Based Completion

```python
# Loop continues until build artifact is created
set_completion_promise(
    promise_type='file_exists',
    condition='/var/build/output/final.zip'
)
```

#### content_match: Content Validation

```python
# Loop validates log contains expected message
set_completion_promise(
    promise_type='content_match',
    condition='/var/log/application.log',
    expected_value='Process completed successfully'
)
```

### Usage Examples

#### Example 1: Multi-Condition Completion

```python
# Set up a loop that completes on file creation OR task count
init_loop(total_tasks=5, promise_type='file_exists', condition='/tmp/ready.txt')

# Later in execution, add additional completion criteria
set_completion_promise(
    promise_type='task_count',
    condition='3'  # Also complete after 3 tasks if file doesn't appear
)
```

#### Example 2: Dynamic Condition Updates

```python
def update_completion_condition(new_file):
    set_completion_promise(
        promise_type='file_exists',
        condition=new_file,
        expected_value=None
    )
```

#### Example 3: Content Pattern Matching

```python
# Match specific JSON content in response file
set_completion_promise(
    promise_type='content_match',
    condition='/tmp/response.json',
    expected_value='"status": "ready", "version": "2.0"'
)
```

### Advanced Patterns

#### Pattern 1: Fallback Completion Strategy

```python
# Primary completion via file, fallback to task count
init_loop(
    total_tasks=5,
    promise_type='file_exists',
    condition='/tmp/ready.txt'
)

# If file doesn't appear after checking, switch to task-based
set_completion_promise(
    promise_type='task_count',
    condition='2'  # Timeout fallback
)
```

#### Pattern 2: Content Validation with Multiple Patterns

```python
def validate_complex_content(filepath):
    patterns = [
        '"status": "success"',
        '"version": "[0-9.]+"',
        '"timestamp":'
    ]
    
    for pattern in patterns:
        set_completion_promise(
            promise_type='content_match',
            condition=filepath,
            expected_value=pattern
        )
```

---

## Integration Examples

### Example 1: Complete Data Processing Workflow

```python
# Initialize loop for processing batch of files
files = ['data1.csv', 'data2.csv', 'data3.csv']
init_loop(
    total_tasks=len(files),
    promise_type='task_count'
)

for file in files:
    # Check if input exists
    if not os.path.exists(f'/input/{file}'):
        add_blocking_issue(f"Input file missing: {file}")
        break
    
    try:
        # Process the file
        process_file(f'/input/{file}')
        
        # Validate output
        if validate_output():
            complete_task()
        else:
            add_blocking_issue(f"Output validation failed for {file}")
    
    except Exception as e:
        add_blocking_issue(f"Processing error in {file}: {str(e)}")

# Check final status
status = loop_status()
print(f"Processed {len(files) - status['tasks_remaining']}/{len(files)} files")
```

### Example 2: API Health Check Loop

```python
# Initialize with content match promise
init_loop(
    total_tasks=5,
    promise_type='content_match',
    condition='/var/log/api_health.log',
    expected_value='"status": "healthy"'
)

for attempt in range(5):
    status = loop_status()
    
    if status['completion_reached']:
        print("API health check passed!")
        break
    
    try:
        response = call_api_endpoint('/health')
        
        if '"status": "healthy"' in response.content:
            complete_task()
            # Loop will detect completion via promise
        else:
            add_blocking_issue(f"API returned unhealthy status on attempt {attempt + 1}")
    
    except Exception as e:
        add_blocking_issue(f"API call failed: {str(e)}")

# Reset if needed for retry
if not status['completion_reached'] and should_retry():
    reset_loop()
```

### Example 3: Iterative Refinement with Custom Promise

```python
def refine_until_quality(current_state, quality_threshold=0.9):
    init_loop(
        total_tasks=10,
        promise_type='task_count'
    )
    
    for iteration in range(10):
        status = loop_status()
        
        if status['completion_reached']:
            print(f"Quality threshold met after {iteration} iterations")
            break
        
        # Perform refinement step
        new_state, quality_score = refine(current_state)
        
        if quality_score >= quality_threshold:
            set_completion_promise(
                promise_type='custom',
                condition=f'quality_met_at_iteration_{iteration}'
            )
            complete_task()
            break
        
        current_state = new_state
    
    return current_state
```

---

## Best Practices

### 1. Always Initialize Before Use

Never call other loop tools without first calling `init_loop`. This ensures proper state setup.

### 2. Check Status Regularly

Use `loop_status()` during execution to monitor progress and detect issues early:

```python
# Good practice
status = loop_status()
if status['tasks_remaining'] == total_tasks // 2:
    print(f"Halfway point: {status}")
```

### 3. Be Specific with Blocking Issues

When adding blocking issues, include enough context for debugging:

```python
# Better
add_blocking_issue("Database connection failed on host 'db.example.com' after 3 retries")

# Less helpful
add_blocking_issue("Database error")
```

### 4. Use Appropriate Promise Types

Choose the right completion condition for your use case:

- **task_count**: When you know exact number of operations
- **file_exists**: When waiting for external artifacts
- **content_match**: When validating output content
- **custom**: For complex conditional logic

### 5. Handle Edge Cases

Always check for blocking issues before completing tasks:

```python
if any_blocking_issues():
    add_blocking_issue("Cannot proceed - unresolved dependencies")
else:
    complete_task()
```

---

## Troubleshooting Common Issues

### Issue: Loop doesn't start

**Symptoms:** Other tools fail or return errors about uninitialized state.

**Solution:** Ensure `init_loop` is called first with valid parameters:

```python
# Always call this before other loop operations
init_loop(total_tasks=5)
```

### Issue: Loop never completes

**Symptoms:** Tasks remaining stays constant, promise not fulfilled.

**Solution:** Check completion conditions and verify they can be met:

1. Verify `file_exists` path is correct
2. Check `content_match` expected value matches actual output
3. Ensure tasks are being marked complete with `complete_task()`

### Issue: Blocking issues prevent progress

**Symptoms:** Loop stops immediately after adding issue.

**Solution:** Review and resolve the blocking issue before continuing:

```python
# Resolve the underlying problem first
fix_database_connection()
# Then continue loop execution
```

### Issue: State not persisting between sessions

**Symptoms:** Reset or new session loses progress.

**Solution:** Ensure state file is properly located at `~/.hermes/plugins/hermes-loop/state.json`. The plugin automatically manages this file.

---

## Additional Resources

- [INSTALLATION.md](./INSTALLATION.md) - Installation and setup guide
- [QUICKSTART.md](./QUICKSTART.md) - Rapid onboarding tutorial
- Project repository for source code and issues

---

**Note:** This documentation covers all 6 tools in the Hermes Loop plugin. For specific use cases not covered here, refer to the tool function signatures or contact the project maintainers.
