# Handoff Document for Convoviz

This document provides context for continuing work on the convoviz project.

## Project Overview

**Convoviz** is a CLI tool that converts ChatGPT export data (ZIP files) into:
- Formatted Markdown files with YAML frontmatter
- Word cloud visualizations (weekly, monthly, yearly)
- Bar plot graphs showing usage patterns
- JSON export of custom instructions

## Recent Changes (January 2026 Modernization)

The codebase was significantly refactored:

### Before → After

| Aspect | Before | After |
|--------|--------|-------|
| Python version | 3.9+ | 3.12+ |
| Config | TypedDict + deepcopy | Pydantic models |
| Models | ClassVar for config (anti-pattern) | Pure data classes |
| Structure | Flat modules | Organized subpackages |
| Type hints | `Optional[X]`, `from __future__` | `X \| None`, native |

### New Module Structure

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
├── models/              # Pure data models
│   ├── message.py       # Message, MessageAuthor, etc.
│   ├── node.py          # Node (tree structure)
│   ├── conversation.py  # Conversation
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

## Key Files to Know

| File | Purpose |
|------|---------|
| `convoviz/config.py` | All configuration models (ConvovizConfig is the main one) |
| `convoviz/pipeline.py` | Main processing flow - start here to understand the app |
| `convoviz/cli.py` | CLI entry point and argument handling |
| `convoviz/models/conversation.py` | Core data model with most business logic |
| `tests/conftest.py` | Test fixtures including mock conversation data |

## Running the Project

```bash
# Install dependencies
uv sync

# Run CLI
uv run convoviz --help
uv run convoviz --zip export.zip --output ./output

# Run tests
uv run pytest -v

# Run linter
uv run ruff check convoviz tests

# Run type checker
uv run mypy convoviz

# Format code
uv run ruff format convoviz tests
```

## Important Patterns

### Configuration Flow
```
get_default_config() → ConvovizConfig
    └── Can be modified directly or via interactive prompts
    └── Passed to run_pipeline(config)
```

### Data Flow
```
ZIP file → load_collection_from_zip() → ConversationCollection
    └── Contains list of Conversation objects
    └── Each Conversation has a tree of Node objects
    └── Each Node may have a Message
```

### Rendering Flow
```
Conversation + Config → render_conversation() → Markdown string
    └── Uses render_yaml_header() for frontmatter
    └── Uses render_node() for each message
```

## Test Structure

- `test_config.py` - Configuration model tests
- `test_models.py` - Data model tests
- `test_renderers.py` - Rendering function tests
- `test_loaders.py` - File loading tests
- `test_pipeline.py` - Integration tests
- `test_cli.py` - CLI tests
- `test_utils.py` - Utility function tests
- `test_exceptions.py` - Exception class tests

All tests use fixtures from `conftest.py`, especially `mock_conversation` and `mock_zip_file`.

## Known Quirks

1. **Font assets**: Fonts are bundled in `convoviz/assets/fonts/`. Default is RobotoSlab-Thin.

2. **NLTK stopwords**: Downloaded on first use, cached with `@lru_cache`.

3. **Bookmarklet support**: The tool can merge data from a browser bookmarklet export (looks for `*bookmarklet*.json` in Downloads).

4. **File naming**: Output files use sanitized conversation titles. Duplicates get `(1)`, `(2)` suffixes.

## What's NOT Done

highlights:

- [ ] Tests for `interactive.py`
- [ ] `GraphConfig` is empty (placeholder for future)
- [ ] ... and
- [ ] much ...
- [ ] more ...

## Dependencies

Key dependencies in `pyproject.toml`:
- `pydantic` + `pydantic-settings` - Config and data models
- `typer` + `rich` - CLI
- `questionary` - Interactive prompts
- `matplotlib` - Graphs
- `wordcloud` + `nltk` - Word clouds
- `orjson` - Fast JSON parsing
- `tqdm` - Progress bars

Dev dependencies:
- `pytest` - Testing
- `ruff` - Linting and formatting
- `mypy` - Type checking

## Commands Reference

```bash
# Full quality check
uv run ruff check convoviz tests && uv run mypy convoviz && uv run pytest

# Quick test run
uv run pytest -x -v

# Test specific file
uv run pytest tests/test_models.py -v

# Format all code
uv run ruff format convoviz tests

# Fix auto-fixable lint issues
uv run ruff check --fix convoviz tests
```

## Notes

This is a working document for brainstorming and info-sharing; it is not a directive.
It's kinda the entry point for working/continuing work on the project.
Try to keep it updated; complete rewrites are within the realm of possibility.

Also a good habit to take (I'm talking to you, AI coding agent) is to write other such .md files to persist plans/context in this session and the next. Write them in the root project directory, or in other places if you prefer, depending on the context.
