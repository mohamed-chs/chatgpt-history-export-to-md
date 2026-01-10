# AGENTS.md

## Project Context
**Convoviz** converts ChatGPT export data (JSON/ZIP) into Markdown, visualizations (Word Clouds, Graphs), and metadata. It handles complex, non-linear conversation trees (DAGs) and polymorphic content types.

## Tech Stack & Standards
- **Runtime**: Python 3.12+ (Managed by `uv`)
- **Core Libraries**: `pydantic` (Data Models), `typer` (CLI), `matplotlib` (Graphs), `wordcloud`.
- **Style**: strict typing (`mypy`), `ruff` for linting/formatting.

## Operational Commands
Always use `uv` to run commands in the environment.

- **Test**: `uv run pytest` (Comprehensive), `uv run pytest -x` (Stop on first fail)
- **Lint**: `uv run ruff check convoviz tests`
- **Format**: `uv run ruff format`
- **Type Check**: `uv run mypy convoviz`

## Architectural Directives
1.  **Pure Data Models**: Classes in `convoviz/models/` must be pure Pydantic models. NO I/O, NO heavy logic, NO visualization code.
2.  **Functional Rendering**: Renderers (`convoviz/renderers/`) accept a Model + Config and return artifacts (strings, bytes). They do not write to disk.
3.  **IO Isolation**: File reading/writing is strictly limited to `convoviz/io/`.
4.  **Configuration**: All user settings must be typed in `convoviz/config.py`.

## Data Schema Notes
- **ChatGPT Exports**: 
    - Structure is a **DAG** (Tree), not a list.
    - `mapping` contains nodes; `current_node` points to the active leaf.
    - `content.parts` is polymorphic (strings mixed with dicts).
    - Top-level can be a list OR `{ conversations: [...] }`.
- **References**: See `docs/chatgpt-spec-unofficial.md` for a deep research on ChatGPT export schema.

## Agent Protocol
- **Startup**: ALWAYS start by reading `dev/HANDOFF.md`, then conduct a deep codebase analysis to understand the current state and conventions.
- **Critical Mindset**: Do not assume the codebase is perfectly implemented. Be alert for missing or buggy logic, including features that may appear complete but still require refinement or further work.
- **Verification**: ALWAYS run `uv run pytest` and `uv run ruff check` before submitting changes.
- **Persistence**: If you leave incomplete work, update `dev/HANDOFF.md` (do not store tasks here).
- **Files**: Do not modify `LICENSE` or `uv.lock` unless explicitly instructed.

## Communication & UX Protocol
- **Directness**: If you need the user to run a test, inspect a file, or provide context, ASK directly. Do not implement complex workarounds to avoid user interaction.
- **User Experience**: Prioritize the end-user experience (UX) of the application. Do not compromise the application's design or usability to fit temporary development environment constraints.
- **Transparency**: Be transparent about missing context or difficulties.

## Meta-Notes
- This is a working document for brainstorming and info-sharing; it is not a directive.
- It's the entry point for working/continuing work on the project.
- Try to keep it updated; complete rewrites are within the realm of possibility.
- **A good habit to take (I'm talking to you, AI coding agent) is to write other such .md files to persist plans/context in this session and the next.** Write them in the root project directory, or in other places if you prefer (like ./dev/), depending on the context. Take the liberty to do it anytime, it's very much encouraged and recommended; you don't even have to ask before you do it, or notify the user at all for that matter.
