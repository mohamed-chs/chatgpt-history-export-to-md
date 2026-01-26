# Data Schema Notes

## ChatGPT Exports
- **Structure**: A **DAG** (Tree), not a list.
- **Navigation**: `mapping` contains nodes; `current_node` points to the active leaf.
- **Polymorphism**: `content.parts` is polymorphic (strings mixed with dicts).
- **Top-level**: Can be a list OR `{ conversations: [...] }`.
- **Content Types**: `text`, `multimodal_text`, `code`, `execution_output`, `tether_browsing_display`, `tether_quote`, `reasoning_recap`, `thoughts` (all supported).
- **Asset Protocols**: `sediment://` (current), `file-service://` (legacy).
- **Hidden Messages**: Internal/tooling messages are filtered via `Message.is_hidden`, including:
    - empty messages
    - most `system` messages (except custom instructions)
    - browser tool output / browsing status messages
    - assistant internal tool calls (e.g. `recipient="browser"` or `content_type="code"`)

## References
See `docs/chatgpt-spec-unofficial-v2.md` for comprehensive ChatGPT export schema (v2, Jan 2026).
