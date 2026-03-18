# Changelog

All notable changes to the Hermes Loop Plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **State Persistence** - Automatic saving of loop state via `.hermes-loop-state.json` for resumption across sessions
- **Completion Promises System** - Flexible termination conditions with three built-in promise types:
  - `task_count`: Stop after completing N tasks
  - `file_exists`: Stop when a specific file is created
  - `content_match`: Stop when a file contains specified content (with optional expected value)
- **Blocking Issue Detection** - Halt loop execution on critical errors via `add_blocking_issue` tool
- **Tool Integration** - Six core tools for loop management:
  - `init_loop`: Initialize new loop state with task tracking and promise configuration
  - `complete_task`: Mark next task as completed, increments task counter
  - `loop_status`: Check current loop state, remaining tasks, completion status, and blocking issues
  - `set_completion_promise`: Define custom termination conditions beyond automatic task detection
  - `reset_loop`: Clear completed task count while preserving total tasks and promise configuration
  - `add_blocking_issue`: Add critical blockers that automatically halt the loop

### Changed
- N/A (initial release)

### Fixed
- N/A (initial release)

### Deprecated
- **License Header Requirement** - Future versions may require plugin license headers for compliance. Current plugins without proper licensing may be flagged in v1.1.0+.

---

## [1.0.0] - 2026-03-17

Initial stable release of the Hermes Loop Plugin with comprehensive loop management capabilities.

### Added
- **Core Loop Functionality**
  - State file monitoring for task progress tracking and session persistence
  - Stop hook integration for controlled loop continuation logic
  - Session start hook for automatic state resumption across agent sessions
  - Automatic detection of blocking issues to prevent infinite loops on errors
  
- **Completion Promises System**
  - `task_count`: Stop after completing a specified number of tasks (integer comparison)
  - `file_exists`: Stop when a specific file path exists on the filesystem
  - `content_match`: Stop when a file contains expected content pattern matching
  - `custom`: Extensible promise type for user-defined custom termination conditions
  
- **Tool Integration** (6 core tools)
  - `init_loop`: Initialize loop with total task count and optional completion promises
  - `complete_task`: Increment completed tasks counter, mark current task done
  - `loop_status`: Query execution state including remaining tasks, completion status, blocking issues
  - `set_completion_promise`: Configure custom termination conditions via promise_type and condition parameters
  - `reset_loop`: Reset completed count without losing total tasks or promise configuration
  - `add_blocking_issue`: Register critical blockers that automatically halt loop progression
  
- **Documentation**
  - Comprehensive SKILL.md with detailed usage examples for all tools
  - README.md with quick start guide and installation instructions
  - PUBLISHING.md with contributor guidelines and release procedures
  - CHANGELOG.md following Keep a Changelog format (this file)

### Changed
- N/A (initial release)

### Fixed
- N/A (initial release)

---

## [0.1.0] - Pre-release

Initial development version based on research of Claude Code's ralph-wiggum-loop plugin concept. This version represents early prototyping and core architecture design work.
