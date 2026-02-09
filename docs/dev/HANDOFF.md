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
├── message_logic.py     # Message extraction/visibility utilities
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
    └── Loaded from bundled TOML defaults
    └── User config (OS-native path) merges over defaults
    └── CLI flags override merged config
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
| `convoviz/assets/default_config.toml` | Bundled TOML defaults (source of truth for defaults) |
| `convoviz/pipeline.py` | Main processing flow - start here to understand the app |
| `convoviz/io/assets.py`| Logic for finding and copying image assets |
| `convoviz/message_logic.py` | Message extraction/visibility logic (kept out of models) |
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
7.  **Render Order**: Markdown output defaults to active-branch traversal; `conversation.markdown.render_order = "full"` renders all DAG nodes.
8.  **Identity Matching**: Markdown overwrite detection scans the first ~128KB for the hidden conversation ID marker/frontmatter.
9.  **Wordcloud Weeks**: Weekly wordcloud filenames use ISO week year/number (week starts Monday).
10. **Tool Noise Filtering**: `web.search` tool outputs are hidden (like `web.run` and `bio`), while `browser` `tether_quote` remains visible.
11. **LaTeX Delimiter Conversion**: When enabled, delimiter conversion skips fenced code blocks and inline code spans.

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
- **KEEP `HANDOFF.md` FOCUSED ON CURRENT STATE.** Use `CHANGELOG.md` for recording recent updates. This file should always reflect the *now*.
- **Changelog Hygiene**: Do not read `docs/dev/CHANGELOG.md` during active work; open it only at the end to append a new entry if needed.

Codebase updates are recorded in [**`docs/dev/CHANGELOG.md`**](CHANGELOG.md) — **check them out!**
