# JSON Schema Update - Jan 2026

## Overview
Updated `convoviz` to support the latest ChatGPT export JSON schema variations.

## Changes

### 1. `convoviz/models/message.py`
- **Updated `AuthorRole`**: Added `"function"` to the allowed literals.
- **Updated `MessageContent`**: Changed `parts` type from `list[str] | None` to `list[Any] | None`. This allows parsing of multimodal messages (images, tool calls) which now appear as dictionaries in the parts list.
- **Updated `Message.text`**: Refactored logic to iterate through `parts` and extract strings, ignoring non-string objects (like image assets or tool outputs) instead of just checking `parts[0]`.

### 2. `convoviz/io/loaders.py`
- **Updated `load_collection_from_json`**: Added logic to detect if the loaded JSON is a dictionary with a `"conversations"` key (the new wrapper format). If found, it extracts the list from there. Fallbacks to assuming the root is the list (legacy format).

## Validation
- Verified with mock data representing:
    - New schema with "function" role.
    - Multimodal content (mixed strings and dicts in `parts`).
    - Top-level object wrapper `{ "conversations": [...] }`.
- All existing tests passed.
