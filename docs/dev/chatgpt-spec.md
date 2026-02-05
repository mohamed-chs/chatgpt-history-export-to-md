# ChatGPT User Data Export Specification (Unofficial)

> **Version:** 3.0 — February 5, 2026  
> **Status:** Reverse-engineered from real exports and community knowledge  
> **Disclaimer:** OpenAI does not publish an official contract for this data. The format evolves silently (e.g., the addition of `textdocs` for Canvas or changes to DALL-E `asset_pointers`). This document reflects the state of exports as observed up to **February 2026**, but may still lag behind current production.

---

## 1. Archive Structure & File System

When you export data (**Settings → Data controls → Export data**), you receive a `.zip` file via email.

### 1.1 Root Contents

| File/Folder | Description | Required |
|:---|:---|:---:|
| **`conversations.json`** | **The Core Data.** All chat histories in a DAG structure. | ✓ |
| **`user.json`** | User profile (ID, email, subscription status, phone). | ✓ |
| **`chat.html`** | Static offline HTML viewer (renders JSON minimally). | ✓ |
| **`message_feedback.json`** | Thumbs up/down and text feedback records. | ✓ |
| **`shared_conversations.json`** | Metadata for publicly shared conversation links. | ✓ |
| **`group_chats.json`** | **(New 2025)** Group chat metadata. Often empty (`{"chats": []}`). | |
| **`shopping.json`** | **(New 2025)** Shopping feature data. Often empty (`[]`). | |
| **`sora.json`** | **(New 2025)** Sora video generation data. Often empty (`{}`). | |
| **`model_comparisons.json`** | Data from "Is this response better or worse?" functionality. | |
| **`textdocs/`** | **(Optional)** Canvas documents as individual JSON files. | |
| **`dalle-generations/`** | DALL-E generated images (WebP format: `file-*-{uuid}.webp`). | |
| **`user-{user_id}/`** | **(New 2025)** Additional generated images (PNG format). | |
| **`file-*` (root)** | User-uploaded images/attachments (various formats). | |

### 1.2 Image File Naming Patterns

Exports use multiple naming conventions for media files:

| Pattern | Location | Description |
|:---|:---|:---|
| `file-{alphanumeric}-{uuid}.webp` | `dalle-generations/` | DALL-E generated images (WebP) |
| `file_{hex}-{uuid}.png` | `user-{id}/` | System-generated images (PNG) |
| `file-{alphanumeric}-{original_filename}` | Root | User uploads (original extension) |
| `file_{hex}-sanitized.{ext}` | Root | Sanitized/processed uploads |

---

## 2. `conversations.json` — The Comprehensive Schema

This file is an `Array<Conversation>` (or an object with a `"conversations"` key). It is **not** a linear list—it's a graph structure.

### 2.1 JSON Schema (Draft Specification)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "array",
  "items": {
    "title": "Conversation",
    "type": "object",
    "properties": {
      "id": { "type": "string", "description": "Internal UUID for the conversation object" },
      "conversation_id": { "type": "string", "description": "Public UUID (often matches 'id')" },
      "title": { "type": ["string", "null"], "description": "Chat title. Can be null if new/empty." },
      "create_time": { "type": "number", "description": "Unix timestamp (float/epoch seconds)." },
      "update_time": { "type": "number", "description": "Unix timestamp of last activity." },
      "current_node": { "type": ["string", "null"], "description": "UUID of the 'leaf' node of the active branch." },
      "mapping": {
        "type": "object",
        "description": "The Message Graph. Dictionary Key = UUID, Value = Node Object.",
        "additionalProperties": { "$ref": "#/definitions/Node" }
      },
      "default_model_slug": { "type": "string" },
      "model_slug": { "type": ["string", "null"], "description": "Model used for the conversation." },
      "gizmo_id": { "type": ["string", "null"] },
      "gizmo_type": { "type": ["string", "null"] },
      "is_archived": { "type": "boolean" },
      "is_starred": { "type": "boolean" },
      "voice": { "type": ["string", "null"] },
      "pinned_time": { "type": ["number", "null"] },
      "moderation_results": { "type": "array", "default": [] },
      "safe_urls": { "type": "array", "items": { "type": "string" } }
    }
  },
  "definitions": {
    "Node": {
      "type": "object",
      "properties": {
        "id": { "type": "string" },
        "parent": { "type": ["string", "null"] },
        "children": { "type": "array", "items": { "type": "string" } },
        "message": { "type": ["object", "null"] }
      }
    }
  }
}
```

#### New/Key Fields (2025-2026)

| Field | Type | Description |
|:---|:---|:---|
| `model_slug` | string? | Model used for the conversation (GPT-5 series observed) |
| `is_starred` | boolean | User starred/favorited the conversation |
| `is_study_mode` | boolean | Conversation uses "Study Mode" feature |
| `is_do_not_remember` | boolean | Conversation excluded from memory learning |
| `voice` | string? | Selected voice for voice mode (alloy, echo, etc.) |
| `pinned_time` | float? | Unix timestamp when conversation was pinned |
| `owner` | string? | User ID of conversation owner |
| `memory_scope` | string? | Memory scope configuration |
| `context_scopes` | object? | Context scoping for personalization |
| `blocked_urls` | string[] | URLs blocked in this conversation |
| `gizmo_type` | string? | Type of custom GPT (`"gpt"`) |
| `disabled_tool_ids` | string[]? | Explicitly disabled tools |
| `async_status` | string? | Status of async operations |
| `conversation_origin` | string? | Origin/source of conversation |
| `sugar_item_id` | string? | Internal UI/Sugar item ID |
| `sugar_item_visible` | boolean? | Visibility of sugar item |

---

## 3. Graph Structure (DAG)

### 3.1 The `mapping` Object

The `mapping` is a dictionary where keys are UUIDs and values are Node objects.
- **Root Node**: `parent: null`, often `message: null`.
- **Branching**: Multiple `children` indicate edits or regenerations.
- **`current_node`**: Points to the active leaf node (the "golden path").

### 3.2 Reconstruction Algorithm ("Golden Path")

To reconstruct the linear conversation as displayed in the UI:

```python
def get_linear_conversation(conversation):
    messages = []
    node_id = conversation["current_node"]
    mapping = conversation["mapping"]
    
    while node_id and node_id in mapping:
        node = mapping[node_id]
        if node.get("message"):
            messages.append(node["message"])
        node_id = node.get("parent")
    
    return list(reversed(messages))  # Chronological order
```

---

## 4. Message Object

### 4.1 Base Structure

```json
{
  "id": "uuid",
  "author": {
    "role": "system | user | assistant | tool",
    "name": "dalle.text2im | browser | python | bio | null",
    "metadata": {}
  },
  "create_time": 1704067200.123,
  "update_time": 1704067200.456,
  "content": { /* Content object - polymorphic */ },
  "status": "finished_successfully | in_progress | error",
  "end_turn": true | null,
  "weight": 1.0,
  "recipient": "all | browser | dalle.text2im | python | canmore.create_textdoc | ...",
  "metadata": { /* Message metadata */ }
}
```

### 4.2 Content Types (Polymorphic)

#### **Type A: Standard Text** (`content_type: "text"`)
```json
{ "content_type": "text", "parts": ["The actual text content."] }
```

#### **Type B: Multimodal / Images** (`content_type: "multimodal_text"`)
```json
{
  "content_type": "multimodal_text",
  "parts": [
    {
      "content_type": "image_asset_pointer",
      "asset_pointer": "sediment://file_00000000...",
      "size_bytes": 48029, "width": 1024, "height": 1024,
      "metadata": { "dalle": { "prompt": "...", "seed": 12345 } }
    },
    "Here is the image you requested." 
  ]
}
```

#### **Type C: Code** (`content_type: "code"`)
Assistant input for Code Interpreter or Canvas creation.

#### **Type D: Execution Output** (`content_type: "execution_output"`)
Result from Code Interpreter.

#### **Type E: Sonic Webpage** (`content_type: "sonic_webpage"`) — New 2026
Full scraped webpage text from `web.search` or `web.run` tools.
```json
{
  "content_type": "sonic_webpage",
  "url": "https://...", "domain": "example.com", "title": "Page Title",
  "text": "Full scraped content...", "snippet": "...", "pub_timestamp": 1700000000.0
}
```

#### **Type F: System Error** (`content_type: "system_error"`)
Tool execution errors (e.g., `robots.txt` denial).

#### **Type G: Reasoning Recap** (`content_type: "reasoning_recap"`) — New 2025
Summary of chain-of-thought reasoning (o1/o3 models).

#### **Type H: Thoughts** (`content_type: "thoughts"`) — New 2025
Internal reasoning thoughts. `thoughts` is a list of objects with `summary` and `content`.

#### **Type I: Tether Quote** (`content_type: "tether_quote"`)
Citation/quote from web source.

#### **Type J: Browsing Display** (`content_type: "tether_browsing_display"`)
Web browsing status/results summary.

### 4.3 Message Metadata

Common keys in the `metadata` object:
| Key | Description |
|:---|:---|
| `is_visually_hidden_from_conversation` | Hide in UI |
| `is_user_system_message` | User's Custom Instructions |
| `model_slug` | Model used for this response |
| `citations` | Array of citation objects |
| `attachments` | File attachment metadata |
| `_cite_metadata` | Citation display metadata |

---

## 5. Tools & Authors (Updated 2026)

| Tool Name | Description | Role |
|:---|:---|:---|
| `web.search` | Modern web search tool. Produces `sonic_webpage`. | tool |
| `web.run` | Advanced web research orchestrator. | tool |
| `bio` | Personalization/Memory tool. Updates model context. | tool |
| `canmore.*` | **Canvas** toolset (`create_textdoc`, `update_textdoc`). | tool |
| `dalle.text2im` | Image generation. | tool |
| `python` | Code interpreter. | tool |

### 5.1 Canvas (Canmore) Protocol

Canvas documents are managed via the `canmore` tool.
- **Creation**: Assistant sends `code` message with `recipient: "canmore.create_textdoc"`.
- **Updates**: Assistant sends `recipient: "canmore.update_textdoc"` with a JSON patch.

---

## 6. Citations (Tether v4)

Modern citations use the `tether_v4` format, mapping metadata to specific indices in the message text.
- **`start_ix` / `end_ix`**: Map placeholders like `【1†source】` to metadata.
- **Metadata**: Contains `title`, `url`, and `text` snippet.

---

## 7. Identifying Hidden Messages

Messages should be suppressed when they represent internal state or tool noise:

```python
def is_hidden(message):
    if not message or not message.get("content"):
        return True
    
    metadata = message.get("metadata", {})
    if metadata.get("is_visually_hidden_from_conversation"):
        return True
        
    author = message.get("author", {})
    role = author.get("role")
    content_type = message.get("content", {}).get("content_type")
    recipient = message.get("recipient", "all")
    
    # Hidden system messages (unless Custom Instructions)
    if role == "system" and not metadata.get("is_user_system_message"):
        return True
    
    # Tool Noise
    if role == "tool":
        if content_type in ("execution_output", "tether_quote", "multimodal_text"):
            return False
        return True
    
    # Internal Assistant Calls
    if role == "assistant" and recipient not in ("all", None):
        return True
        
    # Internal reasoning/status
    if content_type in ("tether_browsing_display", "thoughts", "reasoning_recap"):
        return True
    
    return False
```

---

## 8. Auxiliary File Schemas

### 8.1 `user.json`
Contains user profile details (`id`, `email`, `chatgpt_plus_user`, `phone_number`).

### 8.2 `message_feedback.json`
Records of `thumbsUp` / `thumbsDown` ratings and text feedback.

### 8.3 `textdocs/{uuid}.json` (Canvas)
If present, contains the full Markdown/Code content of a Canvas document.

---

## 9. Model Slugs Reference (2026)

| Slug | Model |
|:---|:---|
| `gpt-5-t-mini` | GPT-5 Turbo Mini (observed Feb 2026) |
| `o3-mini` / `o1` | Reasoning models |
| `gpt-4o` / `gpt-4o-mini` | Omni models |
| `text-davinci-002-render-sha` | Legacy GPT-3.5 |

---

## 10. Tools & Scripts

### 10.1 `jq` Examples
**Extract unique model slugs**:
```bash
jq -r '[.[].mapping[].message.metadata.model_slug // empty] | unique[]' conversations.json
```

### 10.2 Python Quick Parse
```python
def load_conversations(path):
    data = json.loads(path.read_text())
    return data["conversations"] if isinstance(data, dict) else data

def iter_messages(conversation):
    mapping = conversation.get("mapping", {})
    node_id = conversation.get("current_node")
    messages = []
    while node_id and node_id in mapping:
        node = mapping[node_id]
        if msg := node.get("message"):
            messages.append(msg)
        node_id = node.get("parent")
    yield from reversed(messages)
```

---

## 11. Known Quirks & Edge Cases

- **Asset Protocols**: Modern standard is `sediment://`; legacy is `file-service://`.
- **Missing Content**: Failed generations or structural root nodes may have `message: null`.
- **Polymorphic Parts**: `content.parts` can contain strings OR objects (image pointers).
- **Unicode**: Citations often use invisible or special Unicode placeholders.

---

## Changelog

### v3.0 (February 2026)
- Consolidated all specifications into a single master document.
- Added `sonic_webpage`, `system_error`, and `canmore` (Canvas) protocols.
- Documented `tether_v4` citation mapping.
- Added GPT-5 and o3 model slugs.
- Refined `is_hidden` logic for 2026 tool noise.

### v2.0 (January 2026)
- Added new conversation fields (`is_starred`, `voice`, etc.) and 2025 content types.

### v1.0 (Early 2026)
- Initial synthesis of reverse-engineered export data.
