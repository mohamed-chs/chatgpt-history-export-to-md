# Handoff Document for Convoviz

This document provides context for continuing work on the convoviz project.

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
├── renderers/           # Markdown & YAML templates
│   ├── markdown.py      # Markdown generation
│   └── yaml.py          # YAML frontmatter
├── io/                  # File I/O
│   ├── __init__.py      # I/O package entry
│   ├── assets.py        # Attachment handling
│   ├── loaders.py       # ZIP/JSON loaders
│   ├── writers.py       # Markdown/JSON writers
│   └── canvas.py        # Canvas document extraction
├── analysis/            # Visualizations
    ├── graphs/          # Graph generation (modular)
    │   ├── common.py    # Shared utilities
    │   ├── timeseries.py # Activity charts
    │   ├── distributions.py # Histograms
    │   ├── heatmaps.py  # Heatmap charts
    │   └── dashboard.py # Summary dashboard
    └── wordcloud.py     # Word clouds
└── utils.py             # Shared helpers
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
uv run ruff check convoviz tests && uv run ty check convoviz && uv run pytest
```

## Known Quirks & Gotchas

1.  **ChatGPT Data Structure**: It is a **Directed Acyclic Graph (DAG)**, not a linear list.
2.  **Polymorphic Content**: The `parts` field in messages can contain strings (text) OR dictionaries (images, tool calls).
3.  **Asset Resolution**: Images (DALL-E) are often in a `dalle-generations` subfolder (WebP), while user uploads are in the root. The code handles both.
4.  **Asset Pointer Protocols**: Modern exports use `sediment://` protocol; legacy used `file-service://`.
5.  **New Content Types (2025)**: `reasoning_recap`, `thoughts`, `tether_quote` for o1/o3 reasoning models — now supported.
6.  **New Asset Folders (2025)**: `user-{id}/` directories contain system-generated images in PNG format — now supported.

## What's NOT Done (Roadmap)

- [ ] **Performance**: Large exports with thousands of images might be slow to copy. Consider async copy.
- [ ] **Cross-Platform**: Loaders for Claude and Gemini are planned but not started.
- [x] **Custom Instructions Export**: Fixed and re-enabled extraction of user/model system messages into `custom_instructions.json`.
- [x] **Canvas Support**: Implemented extraction of `canmore` documents (text/code) into standalone files with auto-extensions.
- [x] **Schema Documentation**: Updated spec at `chatgpt-spec.md` (Feb 2026).
- [x] **Citations**: Implemented robust parsing for both indexed (Tether v4) and inserted/embedded (Unicode) citations.
- [x] **Reasoning Content**: Support `reasoning_recap` and `thoughts` content types from o1/o3 models.
- [x] **Selectable Outputs**: Users can choose which outputs to generate (Markdown, Graphs, Wordclouds).

## Meta-Notes
- This is a working document for brainstorming and info-sharing; it is not a directive.
- It's the entry point for working/continuing work on the project.
- Try to keep it updated; complete rewrites are within the realm of possibility.
- **A GOOD HABIT TO HAVE (I'm talking to you, AI coding agent) is to write other such .md files to persist plans/context in this session and the next.** Write them in the root project directory, or in other places if you prefer (like ./dev/), depending on the context. Take the liberty to do it anytime, it's very much encouraged and recommended; you don't even have to ask before you do it, or notify the user at all for that matter.
- **ALWAYS KEEP ALL RELEVANT .MD FILES UPDATED WITH YOUR CHANGES. THIS IS CRITICAL.**

> [!TIP]
> Historical updates have been moved to [**`docs/dev/CHANGELOG.md`**](CHANGELOG.md).

## Recent Updates (February 6, 2026)

- **Direct Export (formerly Bookmarklet) Enhancements**:
  - Updated `js/script.js` to package conversations and assets into a single `convoviz_export.zip` file using **JSZip**.
  - Renamed internal discovery logic to `find_script_export`.
  - Updated `pipeline.py` and `interactive.py` to support merging both JSON and ZIP external exports.
  - Updated `js/HOW_TO_USE.md` with instructions for loading JSZip in the browser console.
- **Timestamp Enhancements**:
  - Implemented **Filename Timestamps**: New `--timestamp` (`-t`) flag to prepend `YYYY-MM-DD_HH-MM-SS` to filenames for chronological sorting.
  - Implemented **Message Timestamps**: Added *italics* timestamps after author headers. Uses a smart date display (full date only on date change, otherwise just time).
  - Configurable: `config.markdown.show_timestamp` (on by default) and `config.prepend_timestamp_to_filename` (off by default).

## Recent Updates (February 5, 2026)

- **Custom Instructions & Canvas Support**:
  - Fixed extraction of **Custom Instructions**: Now properly includes hidden system messages. Enabled export to `custom_instructions.json`.
  - Added **Canvas (Canmore) Support**: Extracted documents from `conversations.json` are saved to a `canvas/` folder with appropriate extensions (`.html`, `.py`, `.md`).
  - Improved `Message.text` extraction to handle and render embedded Canvas documents in the conversation history.
- **Graphs Module Refactor**: Split 880-line `graphs.py` into focused submodules:
  - `graphs/common.py` - Shared utilities (font loading, styling, time conversions)
  - `graphs/timeseries.py` - Weekday, hourly, monthly, daily activity charts
  - `graphs/distributions.py` - Model usage, conversation length histograms
  - `graphs/heatmaps.py` - Activity heatmaps
  - `graphs/dashboard.py` - Summary dashboard and orchestration
- **Wordcloud Fix**: Fixed `DeprecationWarning` about fork in multi-threaded processes by using `spawn` context in `ProcessPoolExecutor`.
- **Minor Fixes**:
  - Fixed `has_content` property to include `reasoning_recap` and `thoughts` content types.
  - Renamed `FileNotFoundError` to `ConvovizFileNotFoundError` to avoid shadowing Python builtin.

## Earlier Updates (February 4, 2026)

- **Explicit Direct Export Merge**: Refactored the integration to be explicit and transparent.
  - Added an interactive confirmation prompt in `interactive.py` to ask the user before merging direct export data found in `~/Downloads`.
  - Implemented identity-aware file saving in `io/writers.py` to avoid duplicates across repeated runs.
- **Direct Export Script Update**: Rewrote `js/script.js` to be more robust and modern, including asset naming fixes (prefixing with Asset ID).
- **Multiple Source Paths Support**: `convoviz` now searches across all merged source directories for assets.