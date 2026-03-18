# Pre-Release Checklist

**Project:** hermes-loop-plugin  
**Version:** 1.0.0  
**Date:** March 17, 2026  

---

## Quick Checks Before Publishing

### Files Present ✅
- [x] `README.md` - User documentation
- [x] `LICENSE` - MIT License
- [x] `CONTRIBUTING.md` - Contribution guidelines  
- [x] `CHANGELOG.md` - Version history
- [x] `plugin.yaml` - Plugin manifest
- [x] `pyproject.toml` - Python packaging config

### Build Test ✅
```bash
cd ~/.hermes/plugins/hermes-loop/
python -m build
# Should create: dist/*.whl and dist/*.tar.gz
```

### Tools Registered (6 total) ✅
1. `init_loop` - Initialize loop state
2. `loop_status` - Check current status
3. `complete_task` - Mark task complete
4. `set_completion_promise` - Define termination condition
5. `add_blocking_issue` - Add blocker that stops loop
6. `reset_loop` - Reset completed count

### Documentation Quality ✅
- [x] README provides clear overview and installation instructions
- [x] SKILL.md contains comprehensive usage examples  
- [x] CHANGELOG follows Keep a Changelog format
- [x] CONTRIBUTING guidelines are clear

---

## Publishing Steps

1. **Update version** in both `pyproject.toml` and `plugin.yaml`
2. **Commit changes:**
   ```bash
   git add .
   git commit -m "Bump version to X.X.X"
   git tag vX.X.X
   git push origin main --tags
   ```
3. **Create GitHub Release** on https://github.com/AshMartian/hermes-loop-plugin/releases
4. **Watch it auto-publish!** The workflow will upload to PyPI automatically

---

## After Publishing

Verify your plugin appears at:
https://pypi.org/project/hermes-loop-plugin/

Users can install via:
```bash
pip install hermes-loop-plugin
```

---

**Status:** ✅ Ready for release  