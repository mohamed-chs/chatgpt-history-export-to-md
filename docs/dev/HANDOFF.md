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

## Recent Updates (February 3, 2026)

- **Attachment Renaming**:
    - Attachments in the output are now renamed using the `name` field from `metadata.attachments` if available.
    - Updated `MessageMetadata` model and asset resolution pipeline to support this.
    - Added `tests/test_attachment_renaming.py`.

## Recent Updates (February 3, 2026 - earlier)


- **Citation Rendering**: Implemented robust parsing for both indexed (Tether v4) and inserted/embedded (Unicode) citations.
    - Handled "Ghost" citations where data is hidden in `metadata.search_result_groups`.
    - Implemented `Global Citation Map` in `Conversation` model to resolve citations across message boundaries.
    - Added fallback to strip unresolved citation placeholders.
    - Updated `README.md` features table to include Citations.
- **Metadata**: Added `is_starred` and `voice` field support.
- **Content Filtering**: Improved noise reduction (sonic_webpage, bio, web.run).

## Recent Updates (February 2, 2026)

**Deep Export Inspection & Spec v3**:
- **Comprehensive Data Audit**: Conducted a thorough semantic inspection of the latest ChatGPT export format (Feb 2026).
- **Spec v3.0 Published**: Created `docs/chatgpt-spec-unofficial-v3.md` covering:
    - New content types: `sonic_webpage` (full scraped text), `system_error`.
    - New tools: `web.search`, `web.run`, `bio` (Memory), `canmore` (Canvas).
    - `tether_v4` Citation protocol: mapping `start_ix`/`end_ix` to `【...】` placeholders.
    - Model slugs: `gpt-5-t-mini` confirmed.
- **Improvement Roadmap**: Drafted `docs/dev/RECS.md` with specific recommendations for filtering tool noise, parsing citations, and supporting Canvas.
- **Hidden Logic Refinement**: Identified that `tether_quote` from `browser` was accidentally hidden, while `sonic_webpage` (fluff) was shown.

## Recent Updates (February 1, 2026)

**Interactive CLI Fixes**:
- **Fixed "Outputs State Amnesia"**: The interactive prompt for selecting outputs (Markdown, Graphs, Wordclouds) now correctly respects the pre-existing configuration passed from CLI flags. Previously, it would reset to default (all selected).
- **Dynamic Configuration Prompts**: Refactored `interactive.py` to generate choices dynamically from `OutputKind` enum and `YAMLConfig` Pydantic model. This improves maintainability and ensures new options are automatically available in the interactive mode.
- **Regression Tests**: Added `test_outputs_prompt_respects_existing_config` to `tests/test_interactive.py`.

## Recent Updates (January 31, 2026)

**Improved Installation Scripts**:
- Both `install.sh` and `install.ps1` now include a step to pre-download NLTK stopwords using `uv run --with nltk`. This ensures that word cloud generation is ready to use immediately after installation without waiting for a download on the first run.

## Recent Updates (January 30, 2026)

**CONTRIBUTING.md Added**:
- Created succinct contributor guide covering dev setup, code quality, and testing.
- Links to existing issue templates.

**CLI Updates**:
- Added `--version` (`-V`) flag to display version number and exit.

**Issue Templates Refreshed**:
- Rewrote `bug_report.md`, `feature_request.md`, and `general_feedback.md` to be more specific and aligned with `CONTRIBUTING.md`.
- Added fields for system info, version numbers, and logs in bug reports.

## Recent Updates (January 28, 2026)

**Streamlined Installation Scripts**:
- **New `install.sh`**: One-liner installation for Linux/macOS. Checks for uv, installs if missing, then installs convoviz.
- **New `install.ps1`**: One-liner installation for Windows PowerShell. Same behavior as bash script.
- **README**: Added "Quick Install" section with copy-paste commands for both platforms.
- **Features**: Color output, proper error handling (`set -euo pipefail` / `Try-Catch`), graceful curl/wget fallback.

## Recent Updates (January 27, 2026)

**Pervasive Logging System**:
- **Console & File Logging**: Implemented a robust logging system using `rich` for console and standard logging for files.
- ** CLI Flags**: Added `--verbose` (`-v`) and `--log-file` to control logging.
- **Debug Logs**: Full debug tracebacks are captured in log files (temp file by default) for easier debugging.
- **Instrumentation**: Major components (CLI, Pipeline, Loaders, Writers, Assets, Analysis) are instrumented with logging calls.
- **Docs**: Updated `README.md` and `AGENTS.md` to reflect these changes.

## Project Overview

**Convoviz** is a CLI tool that converts ChatGPT export data (ZIP files) into:
- Formatted Markdown files with YAML frontmatter
- Word cloud visualizations (weekly, monthly, yearly)
- Bar plot graphs showing usage patterns
- JSON export of custom instructions

## Recent Updates (January 26, 2026)

**CI/CD Pipeline Automation**:
- **Automated PyPI Publishing**: Replaced manual `uv publish` with a fully automated GitHub Actions workflow (`release.yml`). Pushing a version tag (e.g., `v0.3.7`) now triggers the build and publish process.
- **Trusted Publishing & Provenance**: Enabled OIDC-based Trusted Publishing and configured `attestations: write` permission to generate PEP 740 provenance attestations on PyPI.
- **Workflow Docs**: Updated `docs/dev/workflow.md` to reflect the new release procedure (Tag & Push).

## Recent Updates (January 22, 2026)

**Selectable Output Types**:
- Users can now choose which outputs to generate: **Markdown**, **Graphs**, **Wordclouds** (defaults to all).
- **Interactive mode**: New checkbox prompt to select outputs; markdown-specific prompts (author headers, flavor, YAML fields) are skipped when markdown is not selected; wordcloud-specific prompts (font, colormap, stopwords) are skipped when wordclouds are not selected.
- **CLI mode**: New `--outputs` flag (repeatable) to select outputs, e.g. `--outputs markdown --outputs graphs`.
- **Pipeline changes**:
  - Only creates/cleans directories for selected outputs.
  - Lazy imports for `graphs` and `wordcloud` modules (prepares for future optional dependencies).
  - **Note**: `custom_instructions.json` export is temporarily disabled (needs rework).
- **Config changes**: Added `OutputKind` enum and `ConvovizConfig.outputs` field in `config.py`.
- **Tests**: New tests in `test_pipeline.py`, `test_cli.py`, `test_interactive.py`, `test_config.py`.
- **Docs**: Updated `README.md` with new `--outputs` flag documentation.

## Updates (January 11, 2026)

**Obsidian Markdown Flavor Enhancements**:
- **AI Reasoning Callouts**: For `obsidian` flavor, `reasoning_recap` and `thoughts` content types (o1/o3 models) are now rendered as collapsible callouts (`> [!NOTE]- 🧠 AI Reasoning`) instead of being hidden.
- This uses Obsidian's native collapsible callout syntax which degrades gracefully on GitHub (renders as a blockquote with `[!NOTE]` prefix).
- Standard flavor behavior unchanged (these content types remain hidden).

**Spec v2 Alignment**:
- **Fixed `is_hidden` Logic**: Now hides ALL tool-targeted assistant messages (`recipient not in ("all", None)`), not just `recipient="browser"`. This correctly hides internal calls to `dalle.text2im`, `python`, etc.
- **Added `is_visually_hidden_from_conversation` Check**: Messages explicitly marked as hidden by OpenAI are now respected.
- **New Content Types Supported**:
  - `reasoning_recap`: o1/o3 model reasoning summaries — **hidden by default** (internal noise)
  - `thoughts`: o1/o3 internal reasoning (list of thought objects) — **hidden by default** (internal noise)
  - `tether_quote`: Web citations rendered as blockquotes with source attribution — **visible**
- **Asset Resolution**: Now searches `user-*/` folders for images (new 2025 export format).

**Date-Based Folder Organization (Default)**:
- Markdown files are now organized by default in nested date folders: `year/month`
- Structure example: `2024/03-March/`
- Index files (`_index.md`) are auto-generated for year and month folders (underscore prefix for alphabetical sorting)
- Added `--flat` (`-f`) CLI flag to disable date organization and put all files in a single folder
- Added `FolderOrganization` enum to `config.py` with `FLAT` and `DATE` (default) options
- Added `get_date_folder_path()` helper in `convoviz/io/writers.py`
- Tests in `tests/test_writers.py`

**Word Cloud Naming Convention**:
- Weekly: `2024-W15.png` (ISO week format)
- Monthly: `2024-03-March.png` (consistent with folder naming)
- Yearly: `2024.png`

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
- **ZIP extraction safety**: Hardened ZIP member validation to reject Windows-style traversal (e.g. `..\evil.txt`) in addition to `../evil.txt`.
- **Output path robustness**: Made pipeline output links resilient to relative paths (best-effort URI printing).
- **Safer output cleanup**: Output cleanup now avoids following symlinks for managed directories/files.
- **Collection merge correctness**: Fixed `ConversationCollection.update()` so it won’t skip “new but older-timestamped” conversations (common with bookmarklet data). Added tests.
- **YAML frontmatter correctness**: YAML frontmatter is now emitted as real YAML (quoted strings, lists/dicts, ISO datetimes) and supports `tags` when enabled.

