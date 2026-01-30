# Contributing to Convoviz

Thanks for your interest in contributing! This guide covers the essentials.

---

## Reporting Bugs

Before reporting, search existing issues and update to the latest version.

Include:
- **Convoviz version**: `convoviz --version`
- **Python version**: `python --version`  
- **OS**: Windows, macOS, or Linux
- **Steps to reproduce**
- **Error messages** (full traceback if available)

👉 **[Open a Bug Report](https://github.com/mohamed-chs/convoviz/issues/new?template=bug_report.md)**

---

## Suggesting Features

Check existing issues first. Describe the problem you're solving and your proposed solution.

👉 **[Open a Feature Request](https://github.com/mohamed-chs/convoviz/issues/new?template=feature_request.md)**

---

## Development Setup

**Prerequisites**: Python 3.12+, [uv](https://github.com/astral-sh/uv)

```bash
# Fork and clone
git clone https://github.com/YOUR_USERNAME/convoviz.git
cd convoviz

# Install dependencies
uv sync

# Verify
uv run convoviz --help
uv run pytest
```

---

## Code Quality

Run the full quality gate before submitting:

```bash
uv run ruff check convoviz tests   # Lint
uv run ty check convoviz            # Type check
uv run pytest                       # Tests
```

Auto-fix lint issues: `uv run ruff check --fix convoviz tests`

---

## Testing

```bash
uv run pytest          # All tests
uv run pytest -x       # Stop on first failure
uv run pytest -v       # Verbose
```

When adding features, include tests for happy path, error cases, and edge cases.

---

## Submitting Changes

1. Create a branch: `git checkout -b feature/your-feature`
2. Make focused commits
3. Run the quality gate (must pass)
4. Push and open a PR

---

## Architecture Quick Reference

```
convoviz/
├── cli.py          # CLI entrypoint
├── config.py       # Configuration models
├── pipeline.py     # Main processing flow
├── models/         # Pydantic data models (no I/O)
├── renderers/      # Markdown/YAML output (no disk writes)
├── io/             # All file operations
└── analysis/       # Graphs and word clouds
```

Key files to understand first:
- `convoviz/pipeline.py` — main processing flow
- `convoviz/config.py` — configuration options
- `docs/dev/HANDOFF.md` — full project context
