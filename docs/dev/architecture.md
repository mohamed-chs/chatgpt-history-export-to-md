# Architecture & Standards

## Tech Stack & Standards
- **Runtime**: Python 3.12+ (Managed by `uv`)
- **Core Libraries**: `pydantic` (Data Models), `typer` (CLI), `matplotlib` (Graphs), `wordcloud`.
- **Style**: strict typing (`ty`), `ruff` for linting/formatting.

## Architectural Directives
1.  **Pure Data Models**: Classes in `convoviz/models/` must be pure Pydantic models. NO I/O, NO heavy logic, NO visualization code.
2.  **Functional Rendering**: Renderers (`convoviz/renderers/`) accept a Model + Config and return artifacts (strings, bytes). They do not write to disk.
3.  **IO Isolation**: File reading/writing is strictly limited to `convoviz/io/`.
4.  **Configuration**: All user settings must be typed in `convoviz/config.py`.
