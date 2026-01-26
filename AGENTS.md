# AGENTS.md

> **Source of truth**: `CLAUDE.md` and `GEMINI.md` are symlinks to this file in this repo.

## Project Context
**Convoviz** converts ChatGPT export data (JSON/ZIP) into Markdown, visualizations (Word Clouds, Graphs), and metadata. It handles complex, non-linear conversation trees (DAGs) and polymorphic content types.

## Operational Commands
Always use `uv` to run commands in the environment.

- **Test**: `uv run pytest` (Comprehensive), `uv run pytest -x` (Stop on first fail)
- **Lint**: `uv run ruff check convoviz tests`
- **Format**: `uv run ruff format`
- **Type Check**: `uv run ty check convoviz`

## 🚀 First Step
**ALWAYS start by reading [`docs/dev/HANDOFF.md`](docs/dev/HANDOFF.md)** to understand the current project state, recent updates, and known issues.

## 📚 Documentation Index
- **[Workflow & Protocols](docs/dev/workflow.md)**: Release steps, git usage, agent behavior rules.
- **[Architecture & Standards](docs/dev/architecture.md)**: Tech stack, core design patterns.
- **[Data Schema](docs/dev/data-schema.md)**: ChatGPT export structure details.
