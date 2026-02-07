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

## 🚀 Agent Protocol

### 1. The Mandatory First Step
**CRITICAL: YOU MUST ALWAYS START BY READING [`docs/dev/HANDOFF.md`](docs/dev/HANDOFF.md) AND CONDUCTING A THOROUGH CODEBASE EXPLORATION.**

This is **MANDATORY AND NON-NEGOTIABLE**, regardless of how simple, small, or straightforward the task may seem. You **MUST** understand the current project state, recent updates, and local context **BEFORE** making any assumptions, changes, or plans. **DO NOT SKIP THIS STEP.** Only after this initial mandatory orientation should you proceed with task-specific exploration and implementation.

### 2. Operational Rigor
- **Critical Mindset**: **DO NOT ASSUME** the codebase is perfectly implemented. Be alert for missing or buggy logic, including features that may appear complete but still require refinement or further work.
- **Verification**: **ALWAYS** run the full quality gate (tests, type checking, linting, formatting) and **FIX ALL ISSUES** before submitting changes.
- **Cohesion Pass**: **MANDATORY.** After changes, perform a targeted sanity/consistency sweep to ensure the new behavior is **fully wired** across configs, prompts/CLI, defaults, tests, and docs. **Do not stop** until the change is coherent end-to-end.
- **Documentation**: **REFLEXIVELY** keep all relevant `.md` files updated. Record all functional and behavioral changes in `docs/dev/CHANGELOG.md`. This is a **CRITICAL REQUIREMENT**.
- **Persistence**: If you leave incomplete work or change the system state, **UPDATE `docs/dev/HANDOFF.md`** with the *current* status and architecture (do not store a history of changes here).
- **Commits**: **PREFER SMALL, LOGICALLY-SCOPED COMMITS** with tests for behavioral changes.

## 🗣️ Communication & UX Protocol

### 1. Directness & Pushing Back
Once you have conducted your initial codebase exploration, be **ASSERTIVE** and **DIRECT**.
- **Ask Directly**: If you need the user to run a test, inspect a file, or provide context, **ASK**. **DO NOT IMPLEMENT** complex workarounds to avoid user interaction.
- **Push Back**: The maintainer values expertise over compliance. If a request is ambiguous, technically flawed, or contradicts established project patterns, **PUSH BACK**. **PROPOSE REFINEMENTS**, better ideas, or even **REJECT AN IDEA** if it’s harmful. A "No, because..." or "Why don't we do X instead?" is much better than a silent, subpar implementation.
- **Transparency**: **BE TRANSPARENT** about missing context, technical debt, or difficulties encountered.

### 2. User Experience (UX) First
**PRIORITIZE** the end-user experience of **Convoviz**. **DO NOT COMPROMISE** the application's design, usability, or performance to fit temporary development environment constraints.

## 📚 Documentation Index
- **[Architecture & Standards](docs/dev/architecture.md)**: Tech stack, core design patterns.
- **[Data Schema](docs/dev/data-schema.md)**: ChatGPT export structure details.
- **[Handoff & Roadmap](docs/dev/HANDOFF.md)**: Current state and pending tasks.
- **[Changelog (Informal)](docs/dev/CHANGELOG.md)**: Historical project updates and changes.
