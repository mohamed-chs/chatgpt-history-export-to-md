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

- [ ] **Custom Instructions Export**: Re-enable and fix `custom_instructions.json` export (currently disabled).
- [x] **Optional Dependencies**: Visualization deps (`wordcloud`, `nltk`) are now in the optional `[viz]` extra. Markdown-only installs are fast. Runtime guards provide clear install guidance when deps are missing.
- [ ] **Performance**: Large exports with thousands of images might be slow to copy. Consider async copy.
- [ ] **Citations**: Parse invisible characters/metadata in ChatGPT exports that denote citations.
- [ ] **Canvas Support**: Research and implement support for "Canvas" content.
- [x] **Interactive Tests**: Added tests covering cancellation behavior and prompt flow (`tests/test_interactive.py`).
- [ ] **Cross-Platform**: Loaders for Claude and Gemini are planned but not started.
- [x] **Schema Documentation**: Updated spec at `docs/chatgpt-spec-unofficial-v2.md` (Jan 2026).
- [x] **Reasoning Content**: Support `reasoning_recap` and `thoughts` content types from o1/o3 models.
- [x] **Selectable Outputs**: Users can choose which outputs to generate (Markdown, Graphs, Wordclouds).

## Meta-Notes
- This is a working document for brainstorming and info-sharing; it is not a directive.
- It's the entry point for working/continuing work on the project.
- Try to keep it updated; complete rewrites are within the realm of possibility.
- **A GOOD HABIT TO HAVE (I'm talking to you, AI coding agent) is to write other such .md files to persist plans/context in this session and the next.** Write them in the root project directory, or in other places if you prefer (like ./dev/), depending on the context. Take the liberty to do it anytime, it's very much encouraged and recommended; you don't even have to ask before you do it, or notify the user at all for that matter.
- **ALWAYS KEEP ALL RELEVANT .MD FILES UPDATED WITH YOUR CHANGES. THIS IS CRITICAL.**

## Recent Updates (February 4, 2026 - later)
unhide recipient="python" messages

only a SINGLE (1) chat out of ALL is affected !
new version includes additional msg. checked using:
git diff --no-index out1/ out2/

> [!TIP]
> Older updates have been moved to [**`docs/dev/CHANGELOG.md`**](CHANGELOG.md).

## Recent Updates (February 4, 2026)

- **Explicit Bookmarklet Merge**: Refactored the integration to be explicit and transparent.
  - Removed implicit automatic merging from `pipeline.py`.
  - Added an interactive confirmation prompt in `interactive.py` to ask the user before merging bookmarklet data found in `~/Downloads`.
  - **Refinement**: Prompt is now skipped if the bookmarklet is already the primary input (fully resolved).
  - Added `bookmarklet_path` to `ConvovizConfig` in `config.py`.
  - **Identity-Based Upsert**: Implemented identity-aware file saving in `io/writers.py`.
    - `convoviz` now "peeks" at existing Markdown files to check their `conversation_id`.
    - If IDs match, it overwrites (updates) the file.
    - If names match but IDs differ, it increments (`title (1).md`).
    - This allows for an **additive, non-destructive flow** while avoiding duplicate files across repeated runs.

**Bookmarklet Script Update**:
- **Updated `js/script.js`**: Rewrote the browser bookmarklet script to be more robust and modern.
- **Asset Naming Fix**: Modified the script to prefix downloaded asset filenames with their Asset ID (e.g. `file-123_budget.csv` or `file-abc.png`).
  - This ensures `convoviz` can correctly resolve assets when the bookmarklet output (flat JSON + flat files) is used as input.
  - Matches `convoviz/io/assets.py` logic which searches for files starting with the Asset ID.
- **Asset Rendering Fix**: Updated `Message.images` property in `models/message.py` to include `metadata.attachments`.
  - Previously, only inline `image_asset_pointer` parts were rendered.
  - Now, files listed in `attachments` (common in bookmarklet exports) are also detected and linked in the Markdown.
- **Multiple Source Paths Support**: Refactored `ConversationCollection` and asset resolution logic to support multiple source paths.
  - Fixed a bug where merging a bookmarklet export into a ZIP export would lose the bookmarklet's source path, causing image resolution to fail.
  - `convoviz` now searches across all merged source directories for assets.