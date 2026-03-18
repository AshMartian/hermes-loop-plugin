# Hermes Loop Plugin - Installation Guide

## Overview

The Hermes Loop plugin provides a set of tools for managing task execution loops in the Hermes Agent environment. This guide covers installation, configuration, and basic setup.

## Prerequisites

Before installing the plugin, ensure you have:

- Python 3.8 or higher installed
- pip package manager available
- Access to a terminal with appropriate permissions

## Installation Methods

### Method 1: pip Install (Recommended)

Install the plugin directly from PyPI:

```bash
pip install hermes-loop-plugin
```

This is the recommended method for most users as it handles dependencies automatically.

### Method 2: Local Development Installation

If you're working with a local copy of the plugin:

```bash
cd ~/.hermes/plugins/hermes-loop
pip install -e .
```

The `-e` flag installs in editable mode, allowing you to modify the source code and see changes immediately.

### Method 3: Manual Installation

For manual installation or when pip is unavailable:

1. Download the plugin package from the repository
2. Extract to `~/.hermes/plugins/hermes-loop/`
3. Ensure all tool scripts are executable:

```bash
chmod +x ~/.hermes/plugins/hermes-loop/tools/*.py
```

## Post-Installation Verification

After installation, verify the plugin is working correctly:

```bash
# Check if tools are available
hermes --list-tools | grep loop

# Run a quick test
python -c "from hermes_loop import init_loop; print('Plugin loaded successfully')"
```

You should see output indicating all 6 tools are registered.

## Tool List

The plugin provides the following tools:

1. **init_loop** - Initialize a new task execution loop with configurable parameters
2. **loop_status** - Check current status of running loops, view progress and blocking issues
3. **complete_task** - Mark the next task as completed and increment counters
4. **add_blocking_issue** - Flag issues that block progress (stops the loop automatically)
5. **reset_loop** - Reset loop state while keeping configuration intact
6. **set_completion_promise** - Define custom termination conditions for loops

## Configuration Files

The plugin creates/uses the following configuration:

- `~/.hermes/plugins/hermes-loop/state.json` - Stores current loop state (auto-generated)
- `~/.hermes/plugins/hermes-loop/config.yaml` - Optional user configuration file

### Custom Configuration (Optional)

Create a config file at `~/.hermes/plugins/hermes-loop/config.yaml`:

```yaml
loop:
  default_timeout: 300
  auto_save_interval: 5
  log_level: INFO
  
prompts:
  enabled: true
  custom_prompts_dir: ~/.hermes/prompts/
```

## Dependencies

The plugin requires the following Python packages:

- `json` (built-in) - State management
- `yaml` - Configuration parsing (optional, for config.yaml support)
- `logging` (built-in) - Logging functionality

Install dependencies if needed:

```bash
pip install pyyaml
```

## Troubleshooting Installation

### Issue: Command not found after installation

**Solution:** Ensure your PATH includes the pip bin directory:

```bash
export PATH="$HOME/.local/bin:$PATH"
# Add to ~/.bashrc or ~/.zshrc for persistence
```

### Issue: Permission denied errors

**Solution:** Use sudo for system-wide installation or adjust permissions:

```bash
sudo pip install hermes-loop-plugin
# OR
pip install --user hermes-loop-plugin
```

### Issue: Module not found error

**Solution:** Verify the plugin path is correct:

```bash
ls -la ~/.hermes/plugins/hermes-loop/
```

Ensure all required files are present. If missing, reinstall the plugin.

### Issue: Tools not appearing in list

**Solution:** Restart your Hermes Agent session after installation to reload plugins.

## Updating the Plugin

To update to the latest version:

```bash
pip install --upgrade hermes-loop-plugin
```

For local development updates:

```bash
cd ~/.hermes/plugins/hermes-loop
git pull origin main
pip install -e .
```

## Getting Help

If you encounter issues during installation:

1. Check the troubleshooting section above
2. Review logs at `~/.hermes/logs/loop.log` (if logging is enabled)
3. File an issue on the project repository with error details

---

**Next Steps:** After successful installation, proceed to [QUICKSTART.md](./QUICKSTART.md) for a rapid onboarding experience, or [USER_GUIDE.md](./USER_GUIDE.md) for comprehensive usage examples.
