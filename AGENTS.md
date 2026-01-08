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

## Agent Protocol
- **Verification**: ALWAYS run `uv run pytest` and `uv run ruff check` before submitting changes.
- **Persistence**: If you leave incomplete work, update `HANDOFF.md` (do not store tasks here).
- **Files**: Do not modify `LICENSE` or `uv.lock` unless explicitly instructed.

## Meta-Notes
- This is a working document for brainstorming and info-sharing; it is not a directive.
- It's the entry point for working/continuing work on the project.
- Try to keep it updated; complete rewrites are within the realm of possibility.
- **A good habit to take (I'm talking to you, AI coding agent) is to write other such .md files to persist plans/context in this session and the next.** Write them in the root project directory, or in other places if you prefer, depending on the context. Take the liberty to do it anytime, it's very much encouraged and recommended; you don't even have to ask before you do it, or notify the user at all for that matter.