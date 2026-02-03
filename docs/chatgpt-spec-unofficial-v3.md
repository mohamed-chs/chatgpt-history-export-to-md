# ChatGPT User Data Export Specification (Unofficial)

> **Version:** 3.0 — February 2, 2026  
> **Status:** Reverse-engineered from real exports and community knowledge  
> **Disclaimer:** OpenAI does not publish an official schema. This format evolves silently. This document reflects exports observed through **February 2026**.

---

## 1. Archive Structure & File System

### 1.1 Root Contents

| File/Folder | Description | Required |
|:---|:---|:---:|
| **`conversations.json`** | All chat histories in DAG structure. | ✓ |
| **`user.json`** | User profile (ID, email, subscription status, phone). | ✓ |
| **`chat.html`** | Static offline HTML viewer. | ✓ |
| **`message_feedback.json`** | Thumbs up/down and text feedback records. | ✓ |
| **`shared_conversations.json`** | Metadata for publicly shared conversation links. | ✓ |
| **`group_chats.json`** | Group chat metadata. | |
| **`shopping.json`** | Shopping feature data. | |
| **`sora.json`** | Sora video generation data. | |
| **`textdocs/`** | **(Optional)** Canvas documents as individual JSON files. | |
| **`dalle-generations/`** | DALL-E generated images (WebP). | |
| **`user-{user_id}/`** | Additional generated images (PNG). | |
| **`file-*` (root)** | User-uploaded images/attachments. | |

---

## 2. `conversations.json` — Complete Schema

### 2.1 Conversation Object

New fields observed in 2026:

| Field | Type | Description |
|:---|:---|:---|
| `model_slug` | string? | Model used for the conversation (GPT-5 series observed) |

---

## 3. Message Object

### 3.1 Content Types (New in v3.0)

#### **Type I: Sonic Webpage** (`content_type: "sonic_webpage"`) — New 2026
Full scraped webpage text from `web.search` or `web.run` tools.

```json
{
  "content_type": "sonic_webpage",
  "url": "https://...",
  "domain": "example.com",
  "title": "Page Title",
  "text": "Full scraped content of the page...",
  "snippet": "Short summary...",
  "pub_timestamp": 1700000000.0
}
```

#### **Type J: System Error** (`content_type: "system_error"`)
Tool execution errors (e.g., `robots.txt` denial).

```json
{
  "content_type": "system_error",
  "name": "tool_error",
  "text": "Error message details..."
}
```

---

## 4. Tools & Authors (Updated v3.0)

2026 exports show a proliferation of specialized tools:

| Tool Name | Description | Role |
|:---|:---|:---|
| `web.search` | Modern web search tool. Produces `sonic_webpage`. | tool |
| `web.run` | Advanced web research orchestrator. | tool |
| `bio` | Personalization/Memory tool. Updates model context. | tool |
| `canmore.*` | **Canvas** toolset (`create_textdoc`, `update_textdoc`). | tool |
| `dalle.text2im` | Image generation. | tool |
| `file_search` | Knowledge base/document search. | tool |
| `python` | Code interpreter. | tool |

### 4.1 Canvas (Canmore) Protocol

Canvas documents are managed via the `canmore` tool.

**Creation:**
Assistant sends a `code` message with `recipient: "canmore.create_textdoc"`. The `text` field contains a JSON string:
```json
{
  "name": "filename.py",
  "type": "code/python",
  "content": "Full source code..."
}
```

**Updates:**
Assistant sends `recipient: "canmore.update_textdoc"` with a JSON patch:
```json
{
  "updates": [
    { "pattern": ".*", "replacement": "New full content..." }
  ]
}
```

---

## 5. Citations (Tether v4)

Modern citations use the `tether_v4` format, which maps metadata to specific indices in the message text.

### 5.1 Citation Metadata

```json
{
  "metadata": {
    "citations": [
      {
        "start_ix": 204,
        "end_ix": 216,
        "citation_format_type": "tether_v4",
        "metadata": {
          "type": "webpage",
          "title": "Source Title",
          "url": "https://...",
          "text": "Snippet from source"
        }
      }
    ]
  }
}
```

### 5.2 Text Representation
The message text contains placeholders like `【89†L44-L48】` or `【1†source】` at the specified indices.

---

## 6. Identifying Hidden Messages (Refined)

To maintain a clean export, the following messages should be suppressed:

```python
def is_hidden(message):
    # Standard checks (Empty, Visually Hidden, Internal System)
    if message.is_empty or message.metadata.is_visually_hidden_from_conversation:
        return True
    if message.author.role == "system" and not message.metadata.is_user_system_message:
        return True

    # Tool Noise
    if message.author.role == "tool":
        # Keep essential tool outputs
        if message.content.content_type in ("execution_output", "tether_quote", "multimodal_text"):
            return False
        # Hide everything else (sonic_webpage, system_error, status updates)
        return True

    # Internal Assistant Calls
    if message.author.role == "assistant" and message.recipient not in ("all", None):
        # Exception: You might want to show Canvas creation or Code input in some flavors
        return True

    # Status/Reasoning Types
    if message.content.content_type in ("tether_browsing_display", "thoughts", "reasoning_recap"):
        return True

    return False
```

---

## 7. Model Slugs Reference (Updated 2026)

| Slug | Model |
|:---|:---|
| `gpt-5-t-mini` | GPT-5 Turbo Mini (observed Feb 2026) |
| `o3-mini` | o3-mini reasoning model |
| `o1` | o1 reasoning model |

---

## Changelog

### v3.0 (February 2026)
- Documented `sonic_webpage` and `system_error` content types.
- Detailed `canmore` (Canvas) creation and update protocol.
- Added `web.search`, `web.run`, `bio` tool documentation.
- Documented `tether_v4` citations with `start_ix`/`end_ix` mapping.
- Updated `is_hidden` logic to suppress new tool noise (`sonic_webpage`, `bio`, etc.).
- Added `gpt-5-t-mini` model slug.
- Noted that `textdocs/` folder may be missing even if Canvas is used.
