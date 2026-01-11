# ChatGPT User Data Export Specification (Unofficial)

> **Version:** 2.0 — January 2026  
> **Status:** Reverse-engineered from real exports and community knowledge  
> **Disclaimer:** OpenAI does not publish an official schema. This format evolves silently. This document reflects exports observed through **January 2026** but may lag behind current production.

---

## 1. Archive Structure & File System

When you export data via **Settings → Data Controls → Export data**, you receive a `.zip` file via email (link valid ~24 hours).

### 1.1 Root Contents

| File/Folder | Description | Required |
|:---|:---|:---:|
| **`conversations.json`** | All chat histories in DAG (Directed Acyclic Graph) structure. The core data. | ✓ |
| **`user.json`** | User profile (ID, email, subscription status, phone). | ✓ |
| **`chat.html`** | Static offline HTML viewer (renders JSON minimally). | ✓ |
| **`message_feedback.json`** | Thumbs up/down and text feedback records. | ✓ |
| **`shared_conversations.json`** | Metadata for publicly shared conversation links. | ✓ |
| **`group_chats.json`** | **(New 2025)** Group chat metadata. Often empty (`{"chats": []}`). | |
| **`shopping.json`** | **(New 2025)** Shopping feature data. Often empty (`[]`). | |
| **`sora.json`** | **(New 2025)** Sora video generation data. Often empty (`{}`). | |
| **`textdocs/`** | Canvas documents as individual JSON files. | |
| **`dalle-generations/`** | DALL-E generated images (WebP format: `file-*-{uuid}.webp`). | |
| **`user-{user_id}/`** | **(New 2025)** Additional generated images (PNG format). | |
| **`file-*` (root)** | User-uploaded images/attachments (various formats). | |

### 1.2 Image File Naming Patterns

Exports now use multiple naming conventions for media files:

| Pattern | Location | Description |
|:---|:---|:---|
| `file-{alphanumeric}-{uuid}.webp` | `dalle-generations/` | DALL-E generated images (WebP) |
| `file_{hex}-{uuid}.png` | `user-{id}/` | System-generated images (PNG) |
| `file-{alphanumeric}-{original_filename}` | Root | User uploads (original extension) |
| `file_{hex}-sanitized.{ext}` | Root | Sanitized/processed uploads |

---

## 2. `conversations.json` — Complete Schema

This file is an `Array<Conversation>`. **Not** a linear list—it's a graph structure.

> [!NOTE]
> In some exports, the top level may be `{ "conversations": [...] }` instead of a bare array.

### 2.1 Conversation Object

```json
{
  "id": "uuid",
  "conversation_id": "uuid",
  "title": "string | null",
  "create_time": 1704067200.123,
  "update_time": 1704153600.456,
  "current_node": "uuid | null",
  "mapping": { "node_uuid": { /* Node */ } },
  
  // Model & GPT Configuration
  "default_model_slug": "auto | gpt-4o | gpt-4 | ...",
  "gizmo_id": "g-xxxxx | null",
  "gizmo_type": "gpt | null",
  "plugin_ids": ["plugin-uuid", ...] | null,
  "disabled_tool_ids": ["tool-id", ...] | null,
  
  // Status & Organization
  "is_archived": false,
  "is_starred": false,
  "is_read_only": false,
  "pinned_time": 1704067200.0 | null,
  
  // Memory & Privacy (New 2025)
  "is_do_not_remember": false,
  "memory_scope": "string | null",
  "context_scopes": { /* scope config */ } | null,
  
  // Voice & Study Mode (New 2025)
  "voice": "alloy | echo | fable | onyx | nova | shimmer | null",
  "is_study_mode": false,
  
  // URLs & Security
  "safe_urls": ["https://..."],
  "blocked_urls": ["https://..."],
  
  // Async & Templates
  "async_status": "string | null",
  "conversation_template_id": "uuid | null",
  "conversation_origin": "string | null",
  
  // Sugar Items (Internal)
  "sugar_item_id": "string | null",
  "sugar_item_visible": true | null,
  
  // Multi-user
  "owner": "user-uuid | null",
  
  // Moderation
  "moderation_results": []
}
```

#### New Fields (2025-2026)

| Field | Type | Description |
|:---|:---|:---|
| `is_starred` | boolean | User starred/favorited the conversation |
| `is_study_mode` | boolean | Conversation uses "Study Mode" feature |
| `is_do_not_remember` | boolean | Conversation excluded from memory learning |
| `memory_scope` | string? | Memory scope configuration |
| `context_scopes` | object? | Context scoping for personalization |
| `voice` | string? | Selected voice for voice mode (alloy, echo, etc.) |
| `pinned_time` | float? | Unix timestamp when conversation was pinned |
| `owner` | string? | User ID of conversation owner |
| `blocked_urls` | string[] | URLs blocked in this conversation |
| `gizmo_type` | string? | Type of custom GPT (`"gpt"`) |
| `disabled_tool_ids` | string[]? | Explicitly disabled tools |
| `async_status` | string? | Status of async operations |
| `conversation_origin` | string? | Origin/source of conversation |

---

## 3. Graph Structure (DAG)

### 3.1 The `mapping` Object

The `mapping` is a dictionary where:
- **Keys**: UUID strings identifying each node
- **Values**: Node objects (see below)

```json
{
  "mapping": {
    "node-uuid-1": { "id": "node-uuid-1", "parent": null, "children": [...], "message": null },
    "node-uuid-2": { "id": "node-uuid-2", "parent": "node-uuid-1", "children": [...], "message": {...} }
  }
}
```

### 3.2 Node Object

```json
{
  "id": "uuid",
  "parent": "uuid | null",
  "children": ["uuid", ...],
  "message": { /* Message object */ } | null
}
```

- **Root Node**: `parent: null`, often `message: null` or system message
- **Branching**: Multiple `children` means edits/regenerations created alternate branches
- **`current_node`**: Points to the active leaf (end of the "golden path")

### 3.3 Reconstruction Algorithm ("Golden Path")

To reconstruct the linear conversation as displayed in the UI:

```python
def get_linear_conversation(conversation):
    messages = []
    node_id = conversation["current_node"]
    mapping = conversation["mapping"]
    
    while node_id:
        node = mapping[node_id]
        if node.get("message"):
            messages.append(node["message"])
        node_id = node.get("parent")
    
    return list(reversed(messages))  # Chronological order
```

---

## 4. Message Object

Messages are **polymorphic**—structure varies by content type.

### 4.1 Base Structure

```json
{
  "id": "uuid",
  "author": {
    "role": "system | user | assistant | tool",
    "name": "dalle.text2im | browser | python | null",
    "metadata": {}
  },
  "create_time": 1704067200.123,
  "update_time": 1704067200.456,
  "content": { /* Content object - polymorphic */ },
  "status": "finished_successfully | in_progress | error",
  "end_turn": true | null,
  "weight": 1.0,
  "recipient": "all | browser | dalle.text2im | python | ...",
  "channel": "string | null",
  "metadata": { /* Message metadata */ }
}
```

#### New Message Fields

| Field | Type | Description |
|:---|:---|:---|
| `channel` | string? | Communication channel (new in 2025) |
| `update_time` | float? | Last update timestamp |

### 4.2 Content Types

#### **Type A: Standard Text** (`content_type: "text"`)

```json
{
  "content_type": "text",
  "parts": ["The actual text content."]
}
```

> [!TIP]
> `parts` is always an array. Usually contains 1 element for text. Join with `\n` for safety.

#### **Type B: Multimodal / Images** (`content_type: "multimodal_text"`)

```json
{
  "content_type": "multimodal_text",
  "parts": [
    {
      "content_type": "image_asset_pointer",
      "asset_pointer": "sediment://file_00000000d9d871f4...",
      "size_bytes": 48029,
      "width": 1024,
      "height": 1024,
      "fovea": null,
      "metadata": {
        "dalle": { "prompt": "...", "seed": 12345, "gen_id": "..." },
        "gizmo": { /* custom GPT info */ },
        "generation": { /* generation params */ },
        "sanitized": true,
        "asset_pointer_link": "file:///...",
        "watermarked_asset_pointer": "...",
        "is_no_auth_placeholder": false,
        "container_pixel_height": 1024,
        "container_pixel_width": 1024
      }
    },
    "Here is the image you requested." 
  ]
}
```

##### Asset Pointer Protocols

| Protocol | Description | Example |
|:---|:---|:---|
| `sediment://` | Current standard (2025+) | `sediment://file_00000000...` |
| `file-service://` | Legacy format | `file-service://file-ID-12345` |

> [!IMPORTANT]
> Images may not be included in the export if "Include attachments" wasn't selected. The `asset_pointer` becomes a dead reference.

#### **Type C: Code** (`content_type: "code"`)

Code Interpreter input:

```json
{
  "content_type": "code",
  "language": "python",
  "text": "import pandas as pd\ndf = pd.read_csv('data.csv')"
}
```

#### **Type D: Execution Output** (`content_type: "execution_output"`)

Code Interpreter result:

```json
{
  "content_type": "execution_output",
  "text": "Result: 42"
}
```

#### **Type E: Browsing Display** (`content_type: "tether_browsing_display"`)

Web browsing results with citations:

```json
{
  "content_type": "tether_browsing_display",
  "result": "Search results...",
  "summary": "Brief summary",
  "assets": [],
  "tether_id": "uuid"
}
```

#### **Type F: Tether Quote** (`content_type: "tether_quote"`)

Citation/quote from web source:

```json
{
  "content_type": "tether_quote",
  "url": "https://...",
  "domain": "example.com",
  "text": "Quoted text...",
  "title": "Page Title",
  "tether_id": "uuid"
}
```

#### **Type G: Reasoning Recap** (`content_type: "reasoning_recap"`) — New 2025

Summary of chain-of-thought reasoning (o1/o3 models):

```json
{
  "content_type": "reasoning_recap",
  "content": "Summary of the reasoning process..."
}
```

#### **Type H: Thoughts** (`content_type: "thoughts"`) — New 2025

Internal reasoning thoughts (visible in some contexts):

```json
{
  "content_type": "thoughts",
  "thoughts": "Internal chain of thought...",
  "source_analysis_msg_id": "uuid"
}
```

### 4.3 Message Metadata

The `metadata` field varies significantly. Common keys:

| Key | Description |
|:---|:---|
| `is_visually_hidden_from_conversation` | Boolean — hide in UI |
| `is_user_system_message` | Boolean — user's Custom Instructions |
| `model_slug` | Model used for this response |
| `finish_details` | `{ "type": "stop" }` — completion reason |
| `citations` | Array of citation objects |
| `user_context_message_data` | Memory/personalization data |
| `attachments` | File attachment metadata |
| `_cite_metadata` | Citation display metadata |
| `aggregate_result` | Aggregated tool results |
| `command` | Tool command issued |
| `args` | Tool arguments |

---

## 5. Author Roles & Hidden Messages

### 5.1 Role Types

| Role | Description |
|:---|:---|
| `system` | System prompts (hidden or Custom Instructions) |
| `user` | User messages and uploads |
| `assistant` | AI responses |
| `tool` | Tool outputs (Code Interpreter, browser, etc.) |

### 5.2 Identifying Hidden Messages

Messages should be hidden from display when:

```python
def is_hidden(message):
    if not message:
        return True
    if not message.get("content") or not message["content"].get("parts"):
        return True
    
    author = message.get("author", {})
    role = author.get("role")
    content_type = message.get("content", {}).get("content_type")
    recipient = message.get("recipient", "all")
    metadata = message.get("metadata", {})
    
    # Hidden system messages (unless Custom Instructions)
    if role == "system" and not metadata.get("is_user_system_message"):
        return True
    
    # Tool-targeted assistant messages (internal calls)
    if role == "assistant" and recipient not in ("all", None):
        return True
    
    # Code Interpreter input messages
    if role == "assistant" and content_type == "code":
        return True
    
    # Visually hidden
    if metadata.get("is_visually_hidden_from_conversation"):
        return True
    
    return False
```

---

## 6. Auxiliary File Schemas

### 6.1 `user.json`

```json
{
  "id": "user-88H1MxSxRRAxggyczSAzUGcc",
  "email": "user@example.com",
  "chatgpt_plus_user": false,
  "phone_number": "+1234567890"
}
```

> [!NOTE]
> Field `name` and `image` (Gravatar URL) are sometimes present for Plus users.

### 6.2 `message_feedback.json`

```json
[
  {
    "id": "uuid",
    "conversation_id": "uuid",
    "message_id": "uuid",
    "rating": "thumbsUp | thumbsDown",
    "text": "Optional feedback text",
    "create_time": 1704067200
  }
]
```

### 6.3 `shared_conversations.json`

```json
[
  {
    "id": "share-uuid",
    "conversation_id": "conv-uuid",
    "title": "Conversation Title",
    "is_anonymous": true
  }
]
```

### 6.4 `group_chats.json` — New 2025

```json
{
  "chats": [
    {
      "id": "uuid",
      "title": "Group Chat Name",
      "participants": ["user-id-1", "user-id-2"],
      "create_time": 1704067200
    }
  ]
}
```

> Usually empty for most users.

### 6.5 `shopping.json` — New 2025

Shopping research and checkout data. Structure TBD—typically empty (`[]`).

### 6.6 `sora.json` — New 2025

Sora video generation data. Structure TBD—typically empty (`{}`).

### 6.7 `textdocs/{uuid}.json` — Canvas

```json
{
  "id": "uuid",
  "title": "Document Title",
  "content": "# Markdown content...",
  "created_at": "2024-01-01T00:00:00Z",
  "type": "text/markdown"
}
```

---

## 7. Model Slugs Reference

Common `model_slug` and `default_model_slug` values:

| Slug | Model |
|:---|:---|
| `auto` | Automatic model selection |
| `gpt-4o` | GPT-4o (omni) |
| `gpt-4o-mini` | GPT-4o Mini |
| `gpt-4` | GPT-4 |
| `gpt-4-browsing` | GPT-4 with browsing |
| `gpt-4-code-interpreter` | GPT-4 with Code Interpreter |
| `gpt-4-plugins` | GPT-4 with plugins |
| `gpt-4-gizmo` | GPT-4 via custom GPT |
| `o1` | o1 reasoning model |
| `o1-mini` | o1-mini |
| `o1-preview` | o1-preview |
| `o3` | o3 reasoning model |
| `o3-mini` | o3-mini |
| `text-davinci-002-render-sha` | Legacy GPT-3.5 |
| `gpt-3.5-turbo` | GPT-3.5 Turbo |

---

## 8. Voice Mode

### 8.1 Voice Options

The `voice` field on conversations indicates Advanced Voice Mode:

| Voice | Description |
|:---|:---|
| `alloy` | Neutral, balanced |
| `echo` | Warm, conversational |
| `fable` | Expressive, storytelling |
| `onyx` | Deep, authoritative |
| `nova` | Friendly, upbeat |
| `shimmer` | Clear, professional |

### 8.2 Audio Content

> [!CAUTION]
> Actual audio blobs are **not** included in data exports. Voice conversations appear as text transcriptions in the message content.

---

## 9. Memory & Personalization (2025)

### 9.1 Memory-Related Fields

| Field | Location | Description |
|:---|:---|:---|
| `is_do_not_remember` | Conversation | Exclude from memory training |
| `memory_scope` | Conversation | Scope restriction for memory |
| `context_scopes` | Conversation | Personalization context config |
| `user_context_message_data` | Message metadata | Memory data snapshot |

### 9.2 Custom Instructions

Custom Instructions appear as system messages with:
```json
{
  "author": { "role": "system" },
  "metadata": { "is_user_system_message": true }
}
```

---

## 10. Tools & Scripts

### 10.1 `jq` Examples

**List all conversation titles with timestamps:**
```bash
jq -r '.[] | "\(.title // "Untitled") | \(.create_time | todate)"' conversations.json
```

**Extract all unique model slugs used:**
```bash
jq -r '[.[].mapping[].message.metadata.model_slug // empty] | unique[]' conversations.json
```

**Count messages by role:**
```bash
jq '[.[].mapping[].message.author.role // empty] | group_by(.) | map({(.[0]): length}) | add' conversations.json
```

### 10.2 Python Quick Parse

```python
import json
from pathlib import Path

def load_conversations(path: Path):
    data = json.loads(path.read_text())
    # Handle both array and object wrapper formats
    if isinstance(data, dict) and "conversations" in data:
        return data["conversations"]
    return data

def iter_messages(conversation):
    """Yield messages in chronological order (golden path)."""
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

### 11.1 Structural Issues

- **Root nodes**: Always have `message: null` — skip them
- **Empty parts**: `content.parts` can be `[]` or contain `null`
- **Failed generations**: `status: "error"` messages may have empty content

### 11.2 Content Gotchas

- **Polymorphic parts**: Array elements in `parts` can be strings OR objects
- **Unicode issues**: Some text contains invisible Unicode (citations, formatting)
- **Missing images**: Asset pointers may be dead links if attachments weren't exported

### 11.3 Defensive Parsing

```python
def safe_get_text(message):
    content = message.get("content", {})
    parts = content.get("parts", [])
    
    text_parts = []
    for part in parts:
        if isinstance(part, str):
            text_parts.append(part)
        elif isinstance(part, dict) and part.get("content_type") == "text":
            text_parts.append(part.get("text", ""))
    
    return "\n".join(text_parts)
```

---

## 12. Sources & References

### Official Resources

1. [OpenAI Help: Export Data](https://help.openai.com/en/articles/7260999-how-do-i-export-my-chatgpt-history-and-data)
2. [OpenAI Developer Forum: Decoding Exports](https://community.openai.com/t/decoding-exported-data-by-parsing-conversations-json-and-or-chat-html/403144)

### Community Tools

- [convoviz](https://github.com/mohamed-chs/chatgpt-history-export-to-md) — Python: Markdown conversion + visualizations
- [sanand0/openai-conversations](https://github.com/sanand0/openai-conversations) — TypeScript schema & analysis
- [chatgpt-export-explorer](https://github.com/z1shivam/chatgpt-export-explorer) — Web UI for JSON visualization

---

## Changelog

### v2.0 (January 2026)
- Added 15+ new conversation-level fields (`is_starred`, `is_study_mode`, `voice`, `memory_scope`, etc.)
- Documented new content types: `reasoning_recap`, `thoughts`, `tether_quote`
- New asset pointer protocol: `sediment://`
- New image part fields: `size_bytes`, `width`, `height`, `fovea`
- New export files: `group_chats.json`, `shopping.json`, `sora.json`
- New folder: `user-{id}/` for system-generated images
- Documented WebP format for DALL-E images
- Updated model slugs for o1/o3 series
- Added voice mode documentation
- Memory & personalization fields documentation

### v1.0 (Early 2026)
- Initial synthesis from community knowledge
