# Publishing Guide - Hermes Loop Plugin

**Note**: For a comprehensive maintainer guide with detailed instructions, see [../PUBLISHING.md](../PUBLISHING.md).

This is a condensed version. Please refer to the main PUBLISHING.md for complete documentation.

## Quick Start

### Prerequisites
```bash
pip install build twine keyring
```

### Build and Test
```bash
python -m build
pip install dist/hermes_loop_plugin-*.whl --force-reinstall
```

### Upload to PyPI
```bash
# Test upload first (recommended)
twine upload --repository testpypi dist/*

# Production upload
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-XXXXX  # Your API token from https://pypi.org/manage/account/token/
twine upload dist/*
```

### Tag Release
```bash
git tag vX.X.X && git push origin --tags
```

---

See [../PUBLISHING.md](../PUBLISHING.md) for:
- Detailed version bumping strategy (semver)
- Complete pre-publishing checklist
- Security considerations and credential management
- Troubleshooting guide
- Post-publishing steps (GitHub releases, announcements)
