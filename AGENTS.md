# AGENTS.md

> `CLAUDE.md` and `GEMINI.md` are symlinks to this file.

## Project Context
**Convoviz** converts ChatGPT export data (JSON/ZIP) into Markdown, visualizations (Word Clouds, Graphs), and metadata. It handles complex, non-linear conversation trees (DAGs) and polymorphic content types.

## Operational Commands
Always use `uv` to run commands in the environment. Favor native CLI tools over manual file modifications whenever possible (e.g., `uv add` instead of editing `pyproject.toml`, or `uv run ruff check --fix` for linting).

- **Test**: `uv run pytest` (Comprehensive), `uv run pytest -x` (Stop on first fail)
- **Lint**: `uv run ruff check convoviz tests`
- **Format**: `uv run ruff format`
- **Type Check**: `uv run ty check convoviz`

## 🚀 First Step
**CRITICAL: YOU MUST ALWAYS START BY READING [`docs/dev/HANDOFF.md`](docs/dev/HANDOFF.md) AND CONDUCTING A THOROUGH CODEBASE EXPLORATION.**

This is **MANDATORY AND NON-NEGOTIABLE**, regardless of how simple, small, or straightforward the task may seem. You **MUST** understand the current project state, recent updates, and local context **BEFORE** making any assumptions, changes, or plans. **DO NOT SKIP THIS STEP.** Only after this initial mandatory orientation should you proceed with task-specific exploration and implementation.

**IMPORTANT: YOU MUST ALWAYS KEEP ALL RELEVANT .MD FILES UPDATED WITH YOUR CHANGES. THIS INCLUDES `AGENTS.md`, `README.md`, AND `docs/dev/HANDOFF.md`. THIS IS A CRITICAL REQUIREMENT.**

**CRITICAL: ALWAYS RUN THE FULL QUALITY GATE (tests, type checking, linting, formatting) AND FIX ALL ISSUES BEFORE SUBMITTING CHANGES.**

## 📚 Documentation Index
- **[Workflow & Protocols](docs/dev/workflow.md)**: Release steps, git usage, agent behavior rules.
- **[Architecture & Standards](docs/dev/architecture.md)**: Tech stack, core design patterns.
- **[Data Schema](docs/dev/data-schema.md)**: ChatGPT export structure details.
