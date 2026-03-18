# Publishing Guide - Hermes Loop Plugin

This guide provides step-by-step instructions for maintainers on how to publish updates of the hermes-loop plugin to PyPI.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Version Bumping Strategy (Semver)](#version-bumping-strategy-semver)
- [Pre-Publishing Checklist](#pre-publishing-checklist)
- [Release Process](#release-process)
  - [Step 1: Update Version Numbers](#step-1-update-version-numbers)
  - Step 2: Build the Package
  - Step 3: Test Locally
  - Step 4: Upload to TestPyPI (Recommended)
  - Step 5: Production PyPI Upload
- [Post-Publishing Steps](#post-publishing-steps)
- [Security Considerations](#security-considerations)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before publishing, ensure you have the following:

1. **Maintainer Access** to the GitHub repository
2. **PyPI Account**: Create one at https://pypi.org/account/register/ if needed
3. **Build Tools Installed**:
   ```bash
   pip install build twine keyring
   ```

4. **PyPI Authentication Credentials**:
   - Generate an API token from PyPI account settings (Account Settings → API tokens)
   - Store credentials securely using `keyring` or environment variables
   - Never commit credentials to version control

---

## Version Bumping Strategy (Semver)

This project follows [Semantic Versioning (semver)](https://semver.org/): **MAJOR.MINOR.PATCH**

### Version Number Format

```
X.Y.Z
│ │ │
│ │ └─ PATCH: Bug fixes only, backward compatible
│ └──── MINOR: New features, backward compatible
└──────── MAJOR: Breaking API changes
```

### When to Bump Each Component

| Scenario | Action | Example |
|----------|--------|---------|
| **Breaking Changes** | Increment MAJOR (reset MINOR and PATCH) | `1.2.3` → `2.0.0` |
| **New Features** | Increment MINOR (reset PATCH) | `1.2.3` → `1.3.0` |
| **Bug Fixes Only** | Increment PATCH | `1.2.3` → `1.2.4` |
| **Documentation Updates** | No version change needed | N/A |

### Breaking Changes Examples (Require MAJOR Bump)

- Removing or renaming public APIs
- Changing tool signatures that users depend on
- Modifying plugin behavior in incompatible ways
- Dropping support for Python versions or Hermes Agent features

### Backward Compatible Examples (MINOR bump OK)

- Adding new tools or commands
- New optional parameters with default values
- Performance improvements without API changes
- Bug fixes that don't alter expected behavior

---

## Pre-Publishing Checklist

Complete all items before proceeding with the release:

### Code Quality
- [ ] All tests pass (`pytest` or `test_ci_cd.py`)
- [ ] Linting passes (`black`, `flake8`, `mypy`)
- [ ] No security vulnerabilities (check with `pip audit` if available)
- [ ] CHANGELOG.md is up to date with all changes

### Documentation
- [ ] README.md reflects current functionality
- [ ] All new features documented in USER_GUIDE.md or CMD_REFERENCE.md
- [ ] Version numbers updated in documentation links
- [ ] Any breaking changes documented with migration notes

### Package Integrity
- [ ] Version number bumped in BOTH `pyproject.toml` and `plugin.yaml`
- [ ] Entry points correctly configured in `pyproject.toml`
- [ ] No hardcoded paths or local development references
- [ ] License file present (LICENSE)
- [ ] All required files included in package manifest

### Testing
- [ ] Package builds successfully: `python -m build`
- [ ] Installed wheel works correctly in test environment
- [ ] Plugin discovers and loads properly with Hermes Agent
- [ ] All tools are accessible via LLM discovery

---

## Release Process

### Step 1: Update Version Numbers

Edit the following files to match your new version:

**pyproject.toml:**
```toml
[project]
name = "hermes-loop-plugin"
version = "1.0.1"  # Bump to next version (e.g., 1.0.1)
```

**plugin.yaml:**
```yaml
name: hermes-loop
version: 1.0.1  # Must match pyproject.toml
```

> **Note**: Both files must have matching version numbers!

---

### Step 2: Build the Package

Build distribution artifacts in the `dist/` directory:

```bash
cd ~/.hermes/plugins/hermes-loop
python -m build
```

This creates:
- `dist/hermes_loop_plugin-X.X.X.tar.gz` (source distribution)
- `dist/hermes_loop_plugin-X.X.X-py3-none-any.whl` (wheel)

Verify the built files:
```bash
ls -la dist/
```

---

### Step 3: Test Locally

Before uploading, test the package installation:

```bash
# Install from local build in a virtual environment or with --force-reinstall
pip install dist/hermes_loop_plugin-X.X.X-py3-none-any.whl --force-reinstall --no-cache-dir

# Verify installation
pip show hermes-loop-plugin

# Test plugin loading (optional, depends on your test setup)
python -c "import hermes_loop_plugin; print('Plugin loaded successfully')"
```

If using the Hermes Agent for integration testing:
```bash
hermes  # Should show hermes-loop plugin in available plugins list
```

---

### Step 4: Upload to TestPyPI (Recommended)

**Always test with TestPyPI before production upload.** This prevents accidental releases and allows verification of the complete process.

1. **Ensure you have a TestPyPI account**: https://test.pypi.org/account/register/

2. **Generate an API token** from TestPyPI settings

3. **Upload to TestPyPI**:
   ```bash
   twine upload --repository testpypi dist/*
   ```

4. **Verify the test upload**:
   ```bash
   pip install --index-url https://test.pypi.org/simple/ hermes-loop-plugin
   ```

5. **Test installation** in a clean environment to ensure it works correctly

If everything passes, proceed to production upload. If not, fix issues and rebuild.

---

### Step 5: Production PyPI Upload

Once TestPyPI testing is successful:

1. **Ensure credentials are secure**:
   ```bash
   # Recommended: Use keyring for credential storage
   keyring set pypi.org https://upload.pypi.org/legacy/

   # Or use environment variables (never commit these!)
   export TWINE_USERNAME=__token__
   export TWINE_PASSWORD=pypi-XXXXXXXXXXXX  # Your PyPI API token
   ```

2. **Upload to production PyPI**:
   ```bash
   twine upload dist/*
   ```

3. **Verify the upload** by visiting: https://pypi.org/project/hermes-loop-plugin/

> **Security Note**: Always use `__token__` as username with your API token as password. Never use your PyPI password directly.

---

## Post-Publishing Steps

After successful PyPI upload, complete these steps:

### 1. Create Git Tag

Tag the release in version control:
```bash
git tag v1.0.1
git push origin --tags
```

This creates a visible release point for users to reference.

---

### 2. Create GitHub Release

On the GitHub repository page (https://github.com/NousResearch/hermes-loop-plugin):

1. Click **Releases** → **Draft a new release**
2. Select the tag you just created (`v1.0.1`)
3. Title: `Version X.X.X - [Brief Description]`
4. Add release notes from CHANGELOG.md
5. Mark as "Latest" (optional)
6. Click **Publish release**

---

### 3. Update Documentation Links

Update any external documentation that references the plugin:
- README.md links to PyPI version
- USER_GUIDE.md installation instructions
- CONTRIBUTING.md if publishing process changed

---

### 4. Announce the Release

Notify users through available channels:

**GitHub**:
- GitHub Discussions or Issues for announcements
- Include link to release notes

**Community Channels**:
- Discord server (if applicable)
- Twitter/X with appropriate hashtags (#Python #OpenSource #PyPI)
- Mailing list or newsletter (if applicable)

**Example Announcement Template**:
```
🚀 New Release: hermes-loop-plugin vX.X.X

We're excited to announce version X.X.X of the Hermes Loop plugin!

✨ What's New:
- Feature 1 description
- Feature 2 description

🐛 Fixes:
- Bug fix description

📦 Install/upgrade: pip install --upgrade hermes-loop-plugin

🔗 Full changelog: https://github.com/NousResearch/hermes-loop-plugin/blob/main/CHANGELOG.md
```

---

## Security Considerations

### Credential Management

**NEVER**:
- Commit `.pypirc` files with credentials to git
- Store API tokens in environment variables that are committed
- Share PyPI passwords directly (use API tokens instead)

**ALWAYS**:
- Use `keyring` for credential storage: `pip install keyring`
- Generate API tokens from PyPI account settings
- Rotate tokens periodically
- Use separate tokens for TestPyPI and production

### Token Generation Steps

1. Go to https://pypi.org/manage/account/token/
2. Click **Add API token**
3. Choose scope:
   - Entire account (for maintainers)
   - Specific project (limited access)
4. Give the token a descriptive name
5. Copy and securely store the generated token
6. Use `__token__` as username with this token

### Package Security Checklist

Before publishing, verify:

- [ ] No hardcoded secrets in source code
- [ ] No sensitive data in documentation or examples
- [ ] Dependencies are up to date (check for vulnerabilities)
- [ ] License file is present and correct
- [ ] Package metadata accurately describes the project

---

## Troubleshooting

### Build Fails with ModuleNotFoundError

**Problem**: `python -m build` fails due to missing imports.

**Solution**: Check that all imports use proper package structure:
```bash
# Verify package structure
find hermes_loop_plugin -name "*.py" | head -20

# Test import before building
python -c "import hermes_loop_plugin; print('OK')"
```

---

### PyPI Upload Fails with 403 Forbidden

**Problem**: Authentication error during upload.

**Solutions**:
1. Verify token is valid and not expired:
   ```bash
   # Check current credentials (if using keyring)
   keyring get pypi.org https://upload.pypi.org/legacy/
   ```

2. Regenerate API token from PyPI account settings

3. Ensure you're uploading to correct repository:
   - TestPyPI: `--repository testpypi`
   - Production: no flag or `--repository pypi`

---

### Package Installs But Plugin Not Loaded

**Problem**: After installation, the plugin doesn't appear in Hermes Agent.

**Solutions**:
1. Verify entry point is correct in `pyproject.toml`:
   ```toml
   [project.entry-points."hermes_agent.plugins"]
   hermes-loop = "hermes_loop_plugin:register"
   ```

2. Confirm module name matches directory name:
   - Directory: `hermes_loop_plugin/`
   - Import path: `import hermes_loop_plugin`

3. Reinstall package completely:
   ```bash
   pip uninstall hermes-loop-plugin
   pip install --force-reinstall dist/hermes_loop_plugin-X.X.X-py3-none-any.whl
   ```

---

### Version Numbers Don't Match Warning

**Problem**: PyPI warns about version mismatch between files.

**Solution**: Ensure BOTH files have identical versions:
```bash
# Check pyproject.toml version
grep "^version" pyproject.toml

# Check plugin.yaml version  
grep "version:" plugin.yaml
```

---

## Quick Reference Commands

```bash
# Install build dependencies
pip install build twine keyring

# Build package
python -m build

# Test upload to PyPI
twine upload --repository testpypi dist/*

# Production upload
twine upload dist/*

# Verify installation
pip show hermes-loop-plugin

# Tag and push release
git tag vX.X.X && git push origin --tags

# Check current version numbers
grep "^version" pyproject.toml plugin.yaml
```

---

## Resources

- [Semantic Versioning Specification](https://semver.org/)
- [PyPI Documentation](https://packaging.python.org/en/latest/)
- [Twine User Guide](https://twine.readthedocs.io/)
- [Setuptools Documentation](https://setuptools.pypa.io/)
- [Hermes Agent Plugin Development](https://github.com/NousResearch/hermes-agent)

---

## Maintenance Notes

### Release Schedule Recommendations

- **Patch releases**: As needed for critical bug fixes
- **Minor releases**: Every 2-4 weeks with new features
- **Major releases**: Quarterly or when significant breaking changes accumulate

### Changelog Best Practices

Update `CHANGELOG.md` before each release:
1. Add new section at top with version number and date
2. Categorize changes: Features, Fixes, Breaking Changes
3. Keep descriptions concise but informative
4. Link to pull requests or issues when applicable

---

*Last updated: March 2026 | For questions, open an issue on GitHub.*
