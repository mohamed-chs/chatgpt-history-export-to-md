# Recommendations for Convoviz Improvement - Feb 2026

Based on the deep inspection of the Feb 2026 ChatGPT export data.

## 1. Filter "Tool Noise"
Many new tools (`web.search`, `web.run`, `bio`) generate messages that clutter the Markdown output.
- **Action**: Update `Message.is_hidden` in `convoviz/models/message.py` to:
    - Hide `content_type == "sonic_webpage"` (massive scraped text).
    - Hide `author.name == "bio"` (Memory updates).
    - Hide `author.name == "web.run"` (Internal search status).
    - Ensure `tether_quote` is NOT hidden even if it comes from `browser`.

## 2. Implement Citation Parsing
Citations in `tether_v4` format are currently rendered as ugly `【数字†L数字】` strings.
- **Action**: Use the `metadata.citations` list to replace these placeholders with Markdown links.
    - Match `start_ix` and `end_ix` to the text.
    - Replace with `[Source Title](URL)` or numeric footnotes `[1](URL)`.

## 3. Canvas (Canmore) Support
Canvas documents are becoming a primary way of interacting with code/text.
- **Action**: Support extracting `canmore.create_textdoc` and `canmore.update_textdoc` messages.
    - Since `textdocs/` folder might be missing, the only source is `conversations.json`.
    - Idea: Render the "final" state of a Canvas document at the end of the conversation or as a separate file.

## 4. DALL-E Status Cleanup
DALL-E generations often have a redundant text message: *"DALL·E displayed 1 images..."*.
- **Action**: Hide `role="tool"`, `author.name="dalle.text2im"`, `content_type="text"` messages as they add no value to the export.

## 5. Metadata Enrichment
New fields like `is_starred` and `voice` can be added to the YAML frontmatter.
- **Action**: Update `render_yaml_header` in `convoviz/renderers/yaml.py`.

## 6. GPT-5 Support
The spec now includes `gpt-5-t-mini`.
- **Action**: Ensure all model slug checks handle the `gpt-5` prefix if any specialized logic is needed (none currently required).
