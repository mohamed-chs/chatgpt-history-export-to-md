# Recommendations for Convoviz Improvement - Feb 2026

Future improvements and features to consider.

## 1. Canvas (Canmore) Support
Canvas documents are becoming a primary way of interacting with code/text.
- **Action**: Support extracting `canmore.create_textdoc` and `canmore.update_textdoc` messages.
    - Since `textdocs/` folder might be missing, the only source is `conversations.json`.
    - Idea: Render the "final" state of a Canvas document at the end of the conversation or as a separate file.

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