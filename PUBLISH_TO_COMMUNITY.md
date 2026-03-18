# Quick Guide: Publishing the Hermes Loop Plugin to the Community

This guide shows you exactly what to do next to share your plugin with the Hermes community.

## 📊 Current Status

✅ **Plugin is complete and ready** - All 6 tools working, documentation created, build verified  
📦 **Distribution packages built**: `dist/hermes_loop_plugin-1.0.0-py3-none-any.whl` (13 KB)

---

## 🎯 Recommended Path: Publish to PyPI

This is the official way to share plugins with the Hermes community. Users can then install via:
```bash
pip install hermes-loop-plugin
```

### Step 1: Create GitHub Repository

**Action Required:** You need a public GitHub repo for your plugin.

**Option A**: Use an existing repository (if you have one)  
**Option B**: Create new repository at https://github.com/YOUR_USERNAME/hermes-loop-plugin

**Repo name suggestions:**
- `hermes-loop-plugin`
- `hermes-agent-loop`
- `hermes-loop`

### Step 2: Prepare Repository Files

Your plugin directory **already has everything needed**:

```bash
cd ~/.hermes/plugins/hermes-loop/

# Verify all required files exist (you already have these!):
ls -la README.md LICENSE CONTRIBUTING.md pyproject.toml plugin.yaml .github/
```

**Files you need:**
- ✅ `README.md` - Project overview and installation instructions
- ✅ `LICENSE` - MIT License for open source
- ✅ `CONTRIBUTING.md` - Guide for community contributors
- ✅ `pyproject.toml` - Python packaging configuration
- ✅ `plugin.yaml` - Plugin manifest with version info
- ✅ `.github/` - GitHub templates and workflows

### Step 3: Commit to Git Repository

```bash
cd ~/.hermes/plugins/hermes-loop/

# Initialize git (if not already done)
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial release v1.0.0 - Hermes Loop Plugin"

# Link to remote repository (replace YOUR_USERNAME and repo name)
git remote add origin https://github.com/YOUR_USERNAME/hermes-loop-plugin.git

# Push to GitHub
git push -u origin main
```

### Step 4: Tag the Release

```bash
# Create version tag
git tag v1.0.0

# Push tag
git push origin --tags
```

This creates a visible release point for users to reference.

### Step 5: Build Distribution Packages

You've already done this, but verify again:

```bash
cd ~/.hermes/plugins/hermes-loop/
python -m build

# Verify packages created:
ls -la dist/
# Should show:
# hermes_loop_plugin-1.0.0-py3-none-any.whl
# hermes_loop_plugin-1.0.0.tar.gz
```

### Step 6: Create PyPI Account (If Not Already Done)

1. Go to https://pypi.org/account/register/
2. Register with your email
3. Verify your account via email

### Step 7: Generate PyPI API Token

**Security Note:** Never use your PyPI password directly! Always use an API token.

```bash
# Install keyring for secure credential storage
pip install keyring

# Generate token from PyPI settings page:
# https://pypi.org/manage/account/token/
# 1. Click "Add API token"
# 2. Choose scope (entire account or specific project)
# 3. Give it a descriptive name (e.g., "hermes-loop-plugin publish")
# 4. Copy the generated token (shown only once!)
```

### Step 8: Test Upload to TestPyPI First (Recommended Safety Step)

**Always test before production upload!**

```bash
# Install twine for secure uploads
pip install twine

# Upload to TestPyPI (separate from production PyPI)
twine upload --repository testpypi dist/*

# Verify the test package installs correctly:
pip3 install --index-url https://test.pypi.org/simple/ hermes-loop-plugin
```

If everything works, proceed to production. If not, fix issues and rebuild.

### Step 9: Production PyPI Upload

```bash
# Store your API token securely (keyring recommended)
keyring set pypi.org https://upload.pypi.org/legacy/
# When prompted, enter the API token you generated earlier

# Upload to production PyPI
twine upload dist/*

# Verify at: https://pypi.org/project/hermes-loop-plugin/
```

### Step 10: Post-Publishing Steps

**a. Create GitHub Release:**
- Go to your repository on GitHub
- Click "Releases" → "Draft a new release"
- Select tag `v1.0.0`
- Title: "Version 1.0.0 - Initial Release"
- Add release notes from CHANGELOG.md
- Publish

**b. Announce to Community:**
- Post in Hermes Agent Discord (if available)
- Share on Twitter/X with #Python #OpenSource #PyPI hashtags
- Update any external documentation links

---

## 🔄 Alternative: Direct GitHub Distribution (No PyPI)

If you don't want to use PyPI, users can still install directly from GitHub:

```bash
# Install directly from GitHub repository
pip install git+https://github.com/YOUR_USERNAME/hermes-loop-plugin.git@v1.0.0

# Or with subdirectory if needed
pip install "git+https://github.com/YOUR_USERNAME/hermes-loop-plugin.git@v1.0.0#subdirectory=hermes_loop_plugin"
```

**Pros:** Simpler setup, no PyPI account needed  
**Cons:** Less discoverable, users need to know exact repo URL

---

## 📚 What Users Will See After Publication

### Installation Instructions (for your README):

```markdown
# Install via pip
pip install hermes-loop-plugin

# Verify installation
hermes  # Should show hermes-loop plugin in available plugins list
```

### Available Tools:
Users can then use these tools during their Hermes sessions:
- `init_loop(total_tasks=5)` - Initialize a loop with task count
- `loop_status()` - Check current progress
- `complete_task()` - Mark tasks as complete
- `set_completion_promise(...)` - Define custom termination conditions
- `add_blocking_issue(issue="...")` - Add blockers that stop the loop
- `reset_loop()` - Reset completed count

---

## 🛡️ Security Checklist Before Publishing

- [ ] No hardcoded secrets or API keys in source code
- [ ] `.pypirc` file (if used) is NOT committed to git
- [ ] License file present and properly formatted (MIT ✅)
- [ ] Version numbers match between `pyproject.toml` and `plugin.yaml`
- [ ] All required documentation files included

---

## 🆘 Troubleshooting Common Issues

### Issue: "403 Forbidden" on upload
**Solution:** Check your API token is valid and not expired

### Issue: "Package already exists"
**Solution:** You've already published this version. Use a higher version number in both `pyproject.toml` and `plugin.yaml`, then rebuild

### Issue: Plugin doesn't load after install
**Solution:** Verify entry point configuration in `pyproject.toml`:
```toml
[project.entry-points."hermes_agent.plugins"]
hermes-loop = "hermes_loop_plugin:register"
```

---

## 📞 Need Help?

If you encounter issues during publishing:
1. Check the error message carefully
2. Review the full PUBLISHING.md guide in your plugin directory
3. Open an issue on your GitHub repository for community help

---

## ✅ Summary of Next Steps

**Your immediate action items:**

1. **Create GitHub repo**: https://github.com/YOUR_USERNAME/hermes-loop-plugin
2. **Push code**: `git push origin main --tags`
3. **Register PyPI account**: https://pypi.org/account/register/
4. **Generate API token**: https://pypi.org/manage/account/token/
5. **Test upload**: `twine upload --repository testpypi dist/*`
6. **Production upload**: `twine upload dist/*`
7. **Create GitHub release** with v1.0.0 tag

Once published, users can install via: `pip install hermes-loop-plugin` 🎉
