---
name: loop
description: Continuous task execution loop — keeps agent running until goals completed via state file monitoring and completion promises. Use for multi-step tasks requiring persistent iteration.
license: MIT
version: 1.0.1
tags: [loop, iteration, persistence, state-management]
metadata:
  author: Ash Martian
  hermes:
    tags: [loop, iteration, persistence, state-management]
    related_skills: [subagent-driven-development, writing-plans, systematic-debugging]
---

# Hermes Loop Skill

Use this skill when a task requires **multiple sequential steps** that should continue across turns until a goal is reached.

The plugin injects loop state into every turn via `pre_llm_call`. You drive the loop by calling the provided tools and updating the state file — the agent receives context each turn telling it how many tasks remain and what to do next.

## When to use

- Tasks with 3+ discrete steps where each step needs verification before continuing
- Work that may span multiple sessions (state persists on disk)
- Debugging or refinement cycles that should stop when a condition is met, not just after N iterations

## Workflow

### 1. Start the loop

Call `init_loop` with the total number of tasks and an optional completion promise:

```
init_loop(total_tasks=5)
```

Or with a promise — the loop also stops when the condition is met regardless of task count:

```
init_loop(total_tasks=10, promise_type="file_exists", condition="src/feature.tsx")
```

### 2. Do each task, then mark it complete

After finishing a unit of work, call:

```
complete_task()
```

This increments the counter. The plugin will tell you each turn how many tasks remain.

### 3. Handle blockers

If you hit something that prevents further progress, call:

```
add_blocking_issue(issue="Cannot continue: missing API credentials")
```

The loop will signal the user to intervene. Do not keep iterating when blocked.

### 4. Check status anytime

```
loop_status()
```

Returns `{ has_remaining_tasks, tasks_completed, total_tasks, blocking_issues, completion_reached }`.

### 5. Loop ends automatically when:
- `completed_tasks >= total_tasks`, **or**
- a completion promise is fulfilled, **or**
- `blocking_issues` is non-empty

---

## Completion promises

Set a richer stopping condition beyond task count:

| `promise_type` | `condition` | `expected_value` | Stops when |
|---|---|---|---|
| `task_count` | — | `"3"` | completed ≥ N |
| `file_exists` | `"src/foo.tsx"` | — | file exists |
| `content_match` | `"src/foo.tsx"` | `"export function"` | file contains string |

Call `set_completion_promise` at any point to set or update the promise:

```
set_completion_promise(promise_type="content_match", condition="tests/app.test.ts", expected_value="all tests pass")
```

---

## Example: 5-step feature implementation

```
init_loop(total_tasks=5, promise_type="file_exists", condition="src/feature/index.ts")

# Turn 1 — scaffold the feature
... implement step 1 ...
complete_task()

# Turn 2 — add tests
... implement step 2 ...
complete_task()

# … continue until all 5 tasks done or file exists
```

## Example: debugging until fixed

```
init_loop(total_tasks=8, promise_type="content_match", condition="src/app.ts", expected_value="// fix verified")

# Each turn: try an approach, update code, call complete_task()
# Loop stops when the comment is present or 8 attempts exhausted
```

---

## Rules for agents

- **Always call `complete_task()` after finishing a unit of work.** Skipping this causes the loop to never terminate.
- **Call `add_blocking_issue()` instead of retrying forever.** If you cannot proceed, stop and explain why.
- **Do not create a second state file.** There is one `.hermes-loop-state.json` per working directory.
- **Use `loop_status()` to orient yourself** at the start of a resumed session before taking action.
- **Promise conditions must be achievable.** Don't set `file_exists` on a file that won't be created.

## Force stop (emergency)

```bash
mv .hermes-loop-state.json .hermes-loop-state.json.bak
```

The plugin detects the missing file and stops injecting loop context.
