# CI/CD Testing Documentation

## Overview

This document describes how to test the hermes-loop plugin build process end-to-end.

## Build Verification

### Building the Package

```bash
cd ~/.hermes/plugins/hermes-loop
python3 -m build
```

This creates two distribution packages in `dist/`:
- `hermes_loop_plugin-1.0.0-py3-none-any.whl` (wheel)
- `hermes_loop_plugin-1.0.0.tar.gz` (source tarball)

### Installing from Wheel

```bash
# Create virtual environment
python3 -m venv test-venv
source test-venv/bin/activate

# Install the wheel
pip install dist/hermes_loop_plugin-1.0.0-py3-none-any.whl

# Verify installation
pip show hermes-loop-plugin
```

### Verifying Tool Registration

The plugin registers 6 tools:
1. `init_loop` - Initialize a new loop state
2. `loop_status` - Check current status of the task execution loop
3. `complete_task` - Mark next task as completed
4. `add_blocking_issue` - Add a blocking issue
5. `reset_loop` - Reset loop state
6. `set_completion_promise` - Set completion promise

## Automated Testing

Run the test script:

```bash
cd ~/.hermes/plugins/hermes-loop
python3 tests/test_ci_cd.py
```

This verifies:
- pyproject.toml exists and is valid
- Build creates wheel and tarball
- pip install works correctly
- All 6 tools are registered
- Entry points configured properly

## GitHub Actions Workflows

### publish.yml
Publishes to PyPI when tags or releases are created.

### test.yml (new)
Runs build verification on every push/pull request:
- Builds package for Python 3.8-3.11
- Installs in virtual environment
- Verifies tool registration

## Verification Checklist

- [x] python -m build creates dist/*.whl and dist/*.tar.gz
- [x] pip install dist/*.whl works without errors
- [x] hermes-loop plugin loads and registers tools
- [x] All 6 tools (init_loop, loop_status, complete_task, add_blocking_issue, reset_loop, set_completion_promise) are available

## Known Issues

The build produces deprecation warnings about license format in pyproject.toml:
```
SetuptoolsDeprecationWarning: `project.license` as a TOML table is deprecated
```

This can be fixed by changing the license field to use an SPDX expression:
```toml
[project]
license = {text = "MIT"}  # Change to: license = "MIT"
```
