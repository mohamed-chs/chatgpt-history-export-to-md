# Handoff Document for Convoviz

This document provides context for continuing work on the convoviz project.

## Project Overview

**Convoviz** is a CLI tool that converts ChatGPT export data (ZIP files) into:
- Formatted Markdown files with YAML frontmatter
- Word cloud visualizations (weekly, monthly, yearly)
- Bar plot graphs showing usage patterns
- JSON export of custom instructions

## Recent Updates (January 11, 2026)

**Date-Based Folder Organization (Default)**:
- Markdown files are now organized by default in nested date folders: `year/month/week`
- Structure example: `2024/03-March/Week-02/`
- Week numbers are based on the day of the month (days 1-7 = Week-01, days 8-14 = Week-02, etc.)
- Added `--flat` (`-f`) CLI flag to disable date organization and put all files in a single folder
- Added `FolderOrganization` enum to `config.py` with `FLAT` and `DATE` (default) options
- Added `get_date_folder_path()` helper in `convoviz/io/writers.py`
- Tests in `tests/test_writers.py`

## Updates (January 10, 2026)

**Content Filtering (Fix)**:
- **Hidden Internal Tool Calls**: Improved logic to hide internal assistant tool calls (e.g., `search(...)` or Code Interpreter inputs) which were previously leaking into the Markdown output.
    - Updated `convoviz/models/message.py` to hide messages where `recipient="browser"` OR (`role="assistant"` AND `content_type="code"`).
    - Verified with new test cases in `tests/test_models.py`.

**Image Support & I/O Modernization**:
- **Image Rendering**: Implemented support for rendering images in Markdown (`![Image](assets/...)`).
- **Word Cloud Improvements**: Added programming language keywords and types to the stop words list to reduce noise in technical conversations.
    - Added `exclude_programming_keywords` to `WordCloudConfig`.
    - Defined `PROGRAMMING_STOPWORDS` in `convoviz/analysis/wordcloud.py`.
- **Input Flexibility**: 
    - CLI now accepts `--input` (or `-i`, `-z`, `--zip`) for **directories**, **JSON files**, or **ZIP files**.
    - Updated `config.py`, `pipeline.py`, and `loaders.py` to handle this flexibility.
- **Tests**: Added `tests/test_assets.py` and updated `tests/test_renderers.py`.

**JSON Schema Modernization (Previous)**:
- **Schema Support**: Updated `convoviz/models/message.py` and `loaders.py` to support the modern ChatGPT export format.
- **Documentation**: Created `AGENTS.md` for AI agent context.

**Hardening & Correctness (January 2026)**:
- **ZIP extraction safety**: Hardened ZIP member validation to reject Windows-style traversal (e.g. `..\\evil.txt`) in addition to `../evil.txt`.
- **Output path robustness**: Made pipeline output links resilient to relative paths (best-effort URI printing).
- **Safer output cleanup**: Output cleanup now avoids following symlinks for managed directories/files.
- **Collection merge correctness**: Fixed `ConversationCollection.update()` so it won’t skip “new but older-timestamped” conversations (common with bookmarklet data). Added tests.
- **YAML frontmatter correctness**: YAML frontmatter is now emitted as real YAML (quoted strings, lists/dicts, ISO datetimes) and supports `tags` when enabled.

## System Architecture

### Module Structure

```
convoviz/
├── __init__.py          # Public API exports
├── __main__.py          # python -m convoviz entry
├── cli.py               # Typer CLI
├── config.py            # Pydantic configuration models
├── exceptions.py        # Custom exception hierarchy
├── interactive.py       # Questionary prompts
├── pipeline.py          # Main processing pipeline
├── utils.py             # Utility functions
├── models/              # Pure data models (Pydantic)
│   ├── message.py       # Message, MessageAuthor, Content
│   ├── node.py          # Node (tree structure)
│   ├── conversation.py  # Conversation logic
│   └── collection.py    # ConversationCollection
├── renderers/           # Rendering logic
│   ├── markdown.py      # Markdown generation
│   └── yaml.py          # YAML frontmatter
├── io/                  # File I/O
│   ├── loaders.py       # ZIP/JSON loading
│   ├── writers.py       # File writing
│   └── assets.py        # Asset management (New)
└── analysis/            # Visualizations
    ├── graphs.py        # Bar plots
    └── wordcloud.py     # Word clouds
```

### Important Patterns

#### Configuration Flow
```
get_default_config() → ConvovizConfig
    └── Can be modified directly or via interactive prompts
    └── Passed to run_pipeline(config)
```

#### Data Flow
```
Input (ZIP/Dir/JSON) → loaders.py → ConversationCollection
    └── Contains list of Conversation objects
    └── Sets source_path for asset resolution
```

#### Rendering Flow
```
Conversation + Config → render_conversation() → Markdown string
    └── Uses render_yaml_header() for frontmatter
    └── Uses render_node() for each message
    └── Uses asset_resolver callback to copy/link images
```

## Key Files to Know

| File | Purpose |
|------|---------|
| `convoviz/config.py` | All configuration models (ConvovizConfig is the main one) |
| `convoviz/pipeline.py` | Main processing flow - start here to understand the app |
| `convoviz/io/assets.py`| Logic for finding and copying image assets |
| `AGENTS.md` | Context and operational guidelines for AI agents |

## Running the Project

```bash
# Install dependencies
uv sync

# Run CLI
uv run convoviz --help
uv run convoviz --input export.zip --output ./output
uv run convoviz --input ./extracted_export_dir --output ./output

# Full quality check (Tests + Type + Lint)
uv run ruff check convoviz tests && uv run mypy convoviz && uv run pytest
```

## Known Quirks & Gotchas

1.  **ChatGPT Data Structure**: It is a **Directed Acyclic Graph (DAG)**, not a linear list.
2.  **Polymorphic Content**: The `parts` field in messages can contain strings (text) OR dictionaries (images, tool calls).
3.  **Asset Resolution**: Images (DALL-E) are often in a `dalle-generations` subfolder (WebP), while user uploads are in the root. The code handles both.
4.  **Asset Pointer Protocols**: Modern exports use `sediment://` protocol; legacy used `file-service://`.
5.  **New Content Types (2025)**: `reasoning_recap`, `thoughts`, `tether_quote` for o1/o3 reasoning models.

## What's NOT Done (Roadmap)

- [ ] **Performance**: Large exports with thousands of images might be slow to copy. Consider async copy.
- [ ] **Citations**: Parse invisible characters/metadata in ChatGPT exports that denote citations.
- [ ] **Canvas Support**: Research and implement support for "Canvas" content.
- [x] **Interactive Tests**: Added tests covering cancellation behavior and prompt flow (`tests/test_interactive.py`).
- [ ] **Cross-Platform**: Loaders for Claude and Gemini are planned but not started.
- [x] **Schema Documentation**: Updated spec at `docs/chatgpt-spec-unofficial-v2.md` (Jan 2026).
- [ ] **Reasoning Content**: Support `reasoning_recap` and `thoughts` content types from o1/o3 models.
