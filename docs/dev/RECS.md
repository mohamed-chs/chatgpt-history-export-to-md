# Recommendations for Convoviz Improvement - Feb 2026

Future improvements and features to consider.

## 1. Canvas (Canmore) Support [IMPLEMENTED]
Canvas documents are now extracted from `conversations.json` and saved as standalone files in the `canvas/` folder.
- **Action**: Extracted `canmore.create_textdoc` messages.
    - Processed inline JSON content (name, type, content).
    - Prefixed filenames with conversation ID to avoid collisions.

## 2. Citations Refinement
- **Action**: Improve the visual style of citations. Consider using numeric footnotes `[1](URL)` instead of `[[Source Title](URL)]` for cleaner text flow in long research-heavy chats.

## 3. Metadata Enrichment
New fields like `is_starred` and `voice` are now supported, but more can be added to the YAML frontmatter as they are discovered.
- **Action**: Periodically audit new fields in `conversations.json` and update `render_yaml_header` in `convoviz/renderers/yaml.py`.

## 4. Performance: Async I/O
For exports with hundreds of conversations and thousands of images, the current sequential file copying might be slow.
- **Action**: Use `asyncio` for asset copying and file writing in `convoviz/io/writers.py`.

## 5. Multi-Source Loaders
- **Action**: Implement loaders for other LLM export formats (Claude, Gemini) to make `convoviz` a universal LLM history viewer.