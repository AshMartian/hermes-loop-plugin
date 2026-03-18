# Contributing to Hermes Loop Plugin

Thank you for your interest in contributing to the Hermes Loop plugin! This document provides guidelines and instructions for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Submitting Pull Requests](#submitting-pull-requests)
- [Documentation Guidelines](#documentation-guidelines)
- [Code Style](#code-style)

## Code of Conduct

We are committed to providing a welcoming and inclusive environment. All contributors are expected to be respectful and professional in their interactions.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork**: `git clone https://github.com/YOUR_USERNAME/hermes-loop-plugin.git`
3. **Install dependencies**: See Development Setup below
4. **Create a branch**: `git checkout -b feature/your-feature-name`

## Development Setup

### Prerequisites

- Python 3.8 or higher
- pip and virtualenv
- Git

### Setting Up the Environment

```bash
# Clone your forked repository
cd hermes-loop-plugin

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install development dependencies
pip install build pytest black flake8 mypy

# Install in editable mode for local testing
pip install -e .
```

### Testing Locally

Before committing, ensure your changes pass all tests:

```bash
# Run linting
black hermes_loop_plugin/
flake8 hermes_loop_plugin/
mypy hermes_loop_plugin/

# Run tests (if you add any)
pytest tests/
```

## Making Changes

### Branch Naming Convention

Use descriptive branch names following this pattern:

- `feature/description` - New features
- `bugfix/description` - Bug fixes
- `docs/description` - Documentation changes
- `refactor/description` - Code refactoring without changing behavior
- `chore/description` - Maintenance tasks (build, config, etc.)

### Commit Message Format

Use conventional commits for clear commit history:

```
<type>(<scope>): <description>

[optional body]

[optional footer linking issues]
```

Types include:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Example:
```
feat(loop): add support for custom promise types

Add new promise_type option that allows users to define 
custom termination conditions via tool implementation.

Closes #42
```

### File Organization

The plugin structure is as follows:

```
hermes-loop-plugin/
├── hermes_loop_plugin/           # Main package directory
│   ├── __init__.py              # Entry point, register() function
│   ├── schemas.py               # Tool schemas (what LLM sees)
│   ├── tools.py                 # Tool handlers (implementation)
│   └── local_imports.py         # Wrapper for local plugin access
├── .github/                      # GitHub-specific files
│   ├── workflows/
│   │   └── publish.yml          # CI/CD workflow
├── examples/                     # Example usage code
├── tests/                        # Test suite (optional)
├── pyproject.toml               # Build configuration
├── README.md                    # User documentation
├── PUBLISHING.md                # Maintainer publishing guide
├── LICENSE                      # MIT License
└── CONTRIBUTING.md              # This file
```

## Submitting Pull Requests

### Before Submitting

1. Ensure all tests pass locally
2. Run linting tools (black, flake8, mypy)
3. Update documentation if you changed functionality
4. Add tests for new features or bug fixes
5. Ensure your code follows the project's style guidelines

### PR Process

1. Push your branch to your fork: `git push origin feature/your-feature`
2. Open a Pull Request on GitHub
3. Fill out the PR template with details about your changes
4. Link any related issues (e.g., "Closes #123")
5. Wait for review and address feedback

### Review Process

- All PRs require at least one reviewer approval
- Maintainers will review for:
  - Code quality and style
  - Functionality correctness
  - Documentation completeness
  - Test coverage (for new features)

## Documentation Guidelines

### README.md

The main README should include:
- Clear description of what the plugin does
- Installation instructions
- Quick start guide
- Feature overview with examples
- Usage documentation
- Contribution links

### Tool Documentation

When adding or modifying tools:

1. **Update `schemas.py`**: Add/modify tool definitions for LLM discovery
2. **Document in README.md**: Update the commands table and descriptions
3. **Add usage examples**: Show how to use the new feature

### Inline Code Comments

- Use docstrings for all public functions and classes
- Keep comments focused on "why" not "what" (code shows what)
- Document complex algorithms or non-obvious implementation details

## Code Style

### Python Style Guide

We follow PEP 8 with some modifications:

- **Line length**: Maximum 100 characters
- **Indentation**: 4 spaces per level
- **Imports**: Grouped and sorted (standard library, third-party, local)
- **Naming conventions**:
  - Modules and packages: `snake_case`
  - Classes: `CamelCase`
  - Functions and variables: `snake_case`
  - Constants: `UPPER_SNAKE_CASE`

### Formatting Tools

We use the following tools to maintain code style:

- **Black**: Code formatting (auto-formatting)
- **Flake8**: Linting and style checking
- **Mypy**: Static type checking (recommended)

Run these before submitting:

```bash
black hermes_loop_plugin/
flake8 hermes_loop_plugin/
mypy hermes_loop_plugin/
```

## Adding New Features

### Step-by-Step Guide

1. Create a new issue describing the feature
2. Discuss the implementation approach in comments (optional but recommended)
3. Fork and clone the repository
4. Create a feature branch: `git checkout -b feature/new-feature`
5. Implement the feature following the guidelines above
6. Add tests for your changes
7. Update documentation
8. Run all linting tools
9. Submit a pull request

### Feature Implementation Checklist

- [ ] Code follows style guidelines (black, flake8)
- [ ] Type hints added where appropriate
- [ ] Docstrings for all public functions/classes
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] CHANGELOG.md updated if applicable
- [ ] No breaking changes without clear migration path

## Questions and Support

If you have questions about contributing:

1. Check existing issues and documentation first
2. Open a new issue for discussion
3. Reach out in the Hermes Agent community channels (Discord, etc.)

## Thank You!

Your contributions make the Hermes Loop plugin better for everyone. We appreciate your time and effort in helping improve this tool!

---

**Note**: For publishing instructions, see [PUBLISHING.md](../PUBLISHING.md).
