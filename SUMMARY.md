# 🚀 Hermes Loop Plugin - v1.0.0 Release Announcement

**Continuous task execution for Hermes Agent**  
*Published: March 17, 2026 | License: MIT | PyPI: hermes-loop-plugin*

---

## 📦 What Is This?

The **Hermes Loop Plugin** enables persistent multi-step workflows where tasks span multiple sessions or require iterative refinement. Think of it as a "keep trying until done" engine for your AI agent.

Inspired by Claude Code's ralph-wiggum-loop pattern, but designed specifically for Hermes Agent's tool-based plugin architecture.

---

## ⚡ Quick Start (30 Seconds)

### Installation
```bash
pip install hermes-loop-plugin
```

That's it! The plugin auto-discovers on your next Hermes Agent startup.

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

## 🎯 Key Features

### 1. State File Persistence 📝
Tracks task progress via `.hermes-loop-state.json`, surviving agent restarts and session interruptions.

```json
{
  "total_tasks": 5,
  "completed_tasks": 2,
  "blocking_issues": [],
  "completion_promise": {
    "promise_type": "file_exists",
    "condition": "src/new-feature.tsx"
  }
}
```

### 2. Completion Promises 🎯  
Define custom termination conditions:

| Type | Description | Use Case |
|------|-------------|----------|
| `task_count` | Stop after N tasks | Try at least 3 debugging approaches |
| `file_exists` | Stop when file created | Keep implementing until feature exists |
| `content_match` | Stop when content appears | Continue until bug fix is in code |
| `custom` | Extensible condition | Complex custom logic |

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

### 5. Blocking Detection 🛑  
Loop automatically stops when critical issues prevent further progress, preventing infinite stuck agents.

---

## 💼 Use Cases

### Feature Implementation Loop
```python
# Implement a feature in multiple steps
init_loop(total_tasks=5, promise_type="file_exists", condition="src/feature.tsx")

delegate_task(goal="Step 1: Create component structure")
complete_task()

delegate_task(goal="Step 2: Add styling")  
complete_task()

# Loop continues until file created or max tasks reached
```

### Debugging Through Iteration
```python
# Systematic debugging with content matching
set_completion_promise(
    promise_type="content_match",
    condition="src/app.tsx",
    expected_value="// Bug fixed"
)

# Follow systematic-debugging process, update state after each test
```

### Multi-Session Workflows
```python
# Long-running tasks across sessions
init_loop(total_tasks=10, promise_type="task_count")

delegate_task(goal="Implement Task 1")
complete_task()

# Agent can stop and restart; loop resumes from completed_tasks=1
```

---

## 📚 Documentation

| Document | Purpose | Lines |
|----------|---------|-------|
| [README.md](./README.md) | Quick start & features overview | 434 |
| [SKILL.md](./SKILL.md) | Comprehensive usage guide with examples | 290 |
| [USER_GUIDE.md](./USER_GUIDE.md) | In-depth user documentation | ~18 KB |
| [CMD_REFERENCE.md](./CMD_REFERENCE.md) | All tool commands reference | 7 KB |
| [QUICKSTART.md](./examples/QUICK_START.md) | 30-second getting started guide | 2.2 KB |
| [CHANGELOG.md](./CHANGELOG.md) | Version history | Ongoing |

**Total:** ~1,550 lines of documentation across all files.

---

## 🔍 How It Works (Diagram)

```
┌─────────────────┐     ┌─────────────────┐
│ User gives goal │────►│ Initialize loop │
└─────────────────┘     │ with state file │
                        └────────┬────────┘
                                 ▼
                        ┌─────────────────┐
                        │ Execute task    │
                        │ via subagent    │
                        └────────┬────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
                    ▼                         ▼
            ┌───────────┐             ┌───────────┐
            │ Update    │◄────────────│ Check     │
            │ state     │   continues │ status    │
            └───────────┘             └─────┬─────┘
                                            │
                              ┌─────────────┼─────────────┐
                              ▼             ▼             ▼
                        Has tasks?    Promise met?  Blocking issue?
                          YES           YES              NO
                            │             │               │
                            ▼             ▼               ▼
                       Continue      Exit loop     Stop immediately
```

---

## 📊 Comparison: Hermes Loop vs ralph-wiggum-loop

| Feature | Hermes Loop | Ralph Wiggum Loop (Claude Code) |
|---------|-------------|----------------------------------|
| Platform | Hermes Agent | Claude Code |
| State file | `.hermes-loop-state.json` | `.ralph-state.json` |
| Promise types | 4 built-in (task_count, file_exists, content_match, custom) | Similar patterns |
| Tool interface | Explicit tools (`loop_status`, `set_completion_promise`) | Implicit via commands |
| Hook integration | post_tool_call, on_session_start, stop_hook | Similar pattern |
| Installation | `~/.hermes/plugins/hermes-loop/` or pip install | `.claude-plugin/` |

---

## 🛠️ Installation & Distribution

### From PyPI (Recommended)
```bash
pip install hermes-loop-plugin
```

**After installation:** Plugin auto-discovers on next Hermes Agent startup. No configuration needed!

### Local Development
```bash
cd ~/.hermes/plugins/hermes-loop
pip install -e .
```

### Build & Publish (Maintainers)
```bash
python -m build
twine upload dist/*
```

---

## 🔐 Security Considerations

### State File Permissions
Ensure state files are not world-readable if they contain sensitive data:
```bash
chmod 600 .hermes-loop-state.json
```

### Input Validation
Path traversal attacks prevented via promise condition validation.

---

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

**Ways to contribute:**
- Report bugs on GitHub Issues
- Submit pull requests with improvements
- Update documentation
- Share feedback and use cases

See [.github/PUBLISHING.md](./.github/PUBLISHING.md) for contributor publishing guide.

---

## 📋 Version History

### v1.0.0 (2026-03-17) - Initial Release ✨
- Core loop functionality with state persistence
- Four promise types: task_count, file_exists, content_match, custom  
- Automatic session resumption from interrupted loops
- Stop hook integration for loop continuation control
- Six command-style tools
- Comprehensive documentation (~1,550 lines)

### Planned Future Versions 🚧

**v1.1.0 (Q2 2026):**
- Webhook support for external notifications
- Progress visualization features

**v1.2.0 (Q3 2026):**
- Time-based promises (stop after N minutes)
- Quality metrics integration

**v2.0.0 (Future):**
- Multi-loop support (run multiple loops simultaneously)
- Advanced state management
- Plugin ecosystem expansion

---

## 🎓 Integration Patterns

### With subagent-driven-development
```python
# Keep subagents running across sessions
init_loop(total_tasks=5, promise_type="task_count", expected_value="3")

delegate_task(goal="Implement Task 1")
complete_task()

# Loop continues automatically via stop_hook
```

### With systematic-debugging  
```python
set_completion_promise(
    promise_type="content_match",
    condition="src/app.tsx",
    expected_value="// Bug fixed"
)

# Follow debugging process, loop stops when bug is fixed or max iterations reached
```

---

## 🆘 Getting Help

### Check Loop Status
```python
status = loop_status()
print(f"Remaining: {status['has_remaining_tasks']}")
print(f"Completed: {status['tasks_completed']}/{status['total_tasks']}")
```

### Inspect State File
```bash
cat .hermes-loop-state.json
```

### Force Stop (if stuck)
```bash
mv .hermes-loop-state.json .hermes-loop-state.json.backup
# Loop detects missing state and stops automatically
```

---

## 📄 License

MIT License - see [LICENSE](./LICENSE) file for full text.

Permission is granted to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of this software.

---

## 🙏 Credits & Inspiration

- **Inspired by:** Claude Code's ralph-wiggum-loop plugin (tzachbon/smart-ralph)
- **Based on:** Hermes Agent plugin architecture documentation  
- **Built for:** The Hermes Agent community at Nous Research

---

## ✅ Final Checklist

**Ready for public launch?**

- [x] All required files present and documented
- [x] Package builds successfully (`python -m build`)
- [x] Plugin loads in Hermes Agent with all 6 tools visible
- [x] Documentation complete (~1,550 lines)
- [x] Security considerations addressed
- [x] MIT license included

---

## 🎉 Download Now!

**PyPI:** https://pypi.org/project/hermes-loop-plugin/  
**GitHub:** https://github.com/NousResearch/hermes-loop-plugin  

```bash
pip install hermes-loop-plugin
```

**Status:** ✅ Complete and ready to use! The plugin is fully functional, well-documented, and publishable.

---

*Hermes Loop Plugin v1.0.0 - March 17, 2026*  
*"Keep going until it's done."*
