# Handoff Document for Convoviz

This document provides context for continuing work on the convoviz project.

## Project Overview

**Convoviz** is a CLI tool that converts ChatGPT export data (ZIP files) into:
- Formatted Markdown files with YAML frontmatter
- Word cloud visualizations (weekly, monthly, yearly)
- Bar plot graphs showing usage patterns
- JSON export of custom instructions

## Recent Updates (January 8, 2026)

**JSON Schema Modernization**:
- **Schema Support**: Updated `convoviz/models/message.py` and `loaders.py` to support the modern ChatGPT export format:
    - Added `function` role to `AuthorRole`.
    - Handled polymorphic `parts` (mixed strings and dicts) in `MessageContent`.
    - Supported top-level dictionary wrappers (`{"conversations": [...]}`) in JSON exports.
- **Documentation**: Created `AGENTS.md` (symlinked as `GEMINI.md`) for AI agent context.

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
│   └── writers.py       # File writing
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
ZIP file → load_collection_from_zip() → ConversationCollection
    └── Contains list of Conversation objects
    └── Each Conversation has a tree of Node objects (DAG)
    └── Each Node may have a Message
```

#### Rendering Flow
```
Conversation + Config → render_conversation() → Markdown string
    └── Uses render_yaml_header() for frontmatter
    └── Uses render_node() for each message
```

## Key Files to Know

| File | Purpose |
|------|---------|
| `convoviz/config.py` | All configuration models (ConvovizConfig is the main one) |
| `convoviz/pipeline.py` | Main processing flow - start here to understand the app |
| `convoviz/models/conversation.py` | Core data model with most business logic |
| `AGENTS.md` | Context and operational guidelines for AI agents |

## Running the Project

```bash
# Install dependencies
uv sync

# Run CLI
uv run convoviz --help
uv run convoviz --zip export.zip --output ./output

# Full quality check (Tests + Type + Lint)
uv run ruff check convoviz tests && uv run mypy convoviz && uv run pytest
```

## Known Quirks & Gotchas

1.  **ChatGPT Data Structure**: It is a **Directed Acyclic Graph (DAG)**, not a linear list. We traverse from `current_node` backwards or recursively through `children`.
2.  **Polymorphic Content**: The `parts` field in messages can contain strings (text) OR dictionaries (images, tool calls).
3.  **Font assets**: Fonts are bundled in `convoviz/assets/fonts/`. Default is RobotoSlab-Thin.
4.  **NLTK stopwords**: Downloaded on first use, cached with `@lru_cache`.
5.  **Bookmarklet support**: The tool can merge data from a browser bookmarklet export.

## What's NOT Done (Roadmap)

- [ ] **Content Rendering**: `Message.text` currently ignores non-string parts (like images). It needs to handle multimodal content properly.
- [ ] **Citations**: Parse invisible characters/metadata in ChatGPT exports that denote citations.
- [ ] **Canvas Support**: Research and implement support for "Canvas" content.
- [ ] **Interactive Tests**: No tests exist for `interactive.py`.
- [ ] **GraphConfig**: Currently empty placeholder.
- [ ] **Cross-Platform**: Loaders for Claude and Gemini are planned but not started.

## Dependencies

Key dependencies in `pyproject.toml`:
- `pydantic` - Config and data models
- `typer` + `rich` - CLI
- `questionary` - Interactive prompts
- `matplotlib` - Graphs
- `wordcloud` - Word clouds
- `orjson` - Fast JSON parsing
