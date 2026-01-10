This is the **Master Synthesis** of the ChatGPT User Data Export specification. It combines the structural precision of Gemini’s breakdown, the formal schema definitions and practical tooling from ChatGPT, and the edge-case handling from both.

> **Disclaimer:** This specification is **reverse-engineered**. OpenAI does not publish an official contract for this data. The format evolves silently (e.g., the addition of `textdocs` for Canvas or changes to DALL-E `asset_pointers`). This document reflects the state of exports as of **early 2025**.

---

# 1. Archive Structure & File System
When you export data (**Settings → Data controls → Export data**), you receive a `.zip` file.
**Root Contents:**

| File/Folder | Description |
| :--- | :--- |
| **`conversations.json`** | **The Core Data.** A JSON array containing every chat history in a DAG (Directed Acyclic Graph) structure. |
| **`user.json`** | User profile metadata (ID, email, subscription status). |
| **`message_feedback.json`** | Records of thumbs up/down and text feedback provided by the user. |
| **`model_comparisons.json`** | Data from "Is this response better or worse?" functionality. |
| **`shared_conversations.json`** | Metadata for public shared links you have created. |
| **`chat.html`** | A static, offline HTML viewer (renders the JSONs minimally). |
| **`textdocs/`** | **(Edge Case / New)** A folder containing **Canvas** documents as individual JSON files. |
| **`user_images/`** | (Sometimes present) A folder containing user-uploaded images, though often images are referenced via URL in the JSON instead. |

---

# 2. `conversations.json` — The Comprehensive Schema

This file is an `Array<Conversation>`. It is **not** a linear list of messages; it is a Graph.

### 2.1 JSON Schema (Draft Specification)
This schema merges the field observations from community parsers and technical analysis.

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
      "current_node": { "type": ["string", "null"], "description": "UUID of the 'leaf' node (the very last message) of the currently active branch." },
      "mapping": {
        "type": "object",
        "description": "The Message Graph. Dictionary Key = UUID, Value = Node Object.",
        "additionalProperties": {
          "$ref": "#/definitions/Node"
        }
      },
      "moderation_results": { "type": "array", "default": [] },
      "plugin_ids": { "type": ["array", "null"], "items": { "type": "string" } },
      "gizmo_id": { "type": ["string", "null"], "description": "If a custom GPT was used." },
      "model_slug": { "type": ["string", "null"], "description": "e.g., 'gpt-4o', 'text-davinci-002-render-sha'" },
      "is_archived": { "type": "boolean" },
      "safe_urls": { "type": "array", "items": { "type": "string" } }
    }
  },
  "definitions": {
    "Node": {
      "type": "object",
      "properties": {
        "id": { "type": "string", "description": "UUID of this node" },
        "parent": { "type": ["string", "null"], "description": "UUID of the preceding message. Null if Root." },
        "children": { "type": "array", "items": { "type": "string" }, "description": "UUIDs of responses/edits. Multiple children = Branching." },
        "message": { "type": ["object", "null"], "description": "The actual content payload. Null for structural root nodes." }
      }
    }
  }
}
```

---

# 3. The Data Structure: Parsing the Graph (DAG)

To reconstruct a chat as seen in the UI, you cannot just iterate through the file. You must traverse the `mapping` object.

### 3.1 The `mapping` Object
*   **Keys:** UUID strings.
*   **Values:** Node objects.
*   **Root Node:** Every conversation has exactly one node where `parent: null`. It usually contains a `message: null` or a system message.
*   **Branching (Edits & Regenerations):**
    *   If a User edits their message, or requests a regeneration, the *Parent* node acquires a new ID in its `children` array.
    *   The `current_node` field in the Conversation object tells you which specific "timeline" (branch) was last active.

### 3.2 The "Golden Path" Algorithm (Reconstruction)
To get the linear chat log:
1.  Read `current_node` (UUID).
2.  Look up `mapping[current_node]`.
3.  Extract the `message` object.
4.  Move to `mapping[node.parent]`.
5.  Repeat until `node.parent` is `null`.
6.  **Reverse** the collected list to get chronological order.

---

# 4. The `message` Object Details

The `message` object (inside a Node) is polymorphic. Its structure changes based on whether it is text, an image, a tool output, or a Canvas event.

### 4.1 Base Structure
```json
{
  "id": "UUID",
  "author": {
    "role": "system" | "user" | "assistant" | "tool",
    "name": "dalle.text2im" | "browser" | null,
    "metadata": {}
  },
  "create_time": 1678992345.123,
  "content": { /* Polymorphic Content - See 4.2 */ },
  "status": "finished_successfully" | "completed" | "failed",
  "end_turn": true,
  "weight": 1.0,
  "metadata": { /* Internal State - See 4.3 */ },
  "recipient": "all" // or specific tool name
}
```

### 4.2 Content Types & Edge Cases
The `content` object is the most complex part of the schema.

#### **Case A: Standard Text**
```json
{
  "content_type": "text",
  "parts": [ "The actual text string." ]
}
```
*Note: `parts` is always an array. In standard text, it usually has 1 element. Community parsers often join with `\n` just in case.*

#### **Case B: Multimodal / DALL-E / Images**
Used when GPT-4 Vision analyzes an image or DALL-E generates one.
```json
{
  "content_type": "multimodal_text",
  "parts": [
    {
      "content_type": "image_asset_pointer",
      "asset_pointer": "file-service://file-ID-12345",
      "metadata": {
        "dalle": { "prompt": "A cat in space", "seed": 12345, "gen_id": "..." }
      }
    },
    "Here is the image you requested." // Optional accompanying text
  ]
}
```
*   **Edge Case:** The actual image file is often **not** in the zip. The `asset_pointer` is an internal reference. If `Include attachments` wasn't selected, these links may be dead.

#### **Case C: Canvas (New / Edge Case)**
Canvas data is often decoupled from `conversations.json`.
1.  **In `conversations.json`:** The message will have a reference to a `text_doc_id` or similar metadata indicating a Canvas event.
2.  **In `textdocs/` folder:** Look for `{UUID}.json`.
    *   **Schema:**
        ```json
        {
          "id": "UUID",
          "title": "Document Title",
          "content": "# Markdown content of the canvas...",
          "created_at": "Timestamp",
          "type": "text/markdown"
        }
        ```

#### **Case D: Tool Calls (Code Interpreter / Search)**
*   **Input (`role: user` or `assistant`):**
    ```json
    {
      "content_type": "code",
      "language": "python",
      "text": "import pandas as pd..."
    }
    ```
    *Observation:* Assistant inputs (e.g., `search('query')`) often have `recipient: "browser"` BUT can also have `recipient: "all"`. Reliable filtering requires checking `role="assistant"` AND (`recipient="browser"` OR `content_type="code"`).

*   **Output (`role: tool`):**
    ```json
    {
      "content_type": "execution_output",
      "text": "Result: 42",
      "parts": [] // May contain references to generated CSVs or charts
    }
    ```
*   **Browsing (`tether_browsing_display`):** Used for citations. `content.metadata` usually contains the citation URL list.

### 4.3 Metadata Field (Variable)
*   `is_user_system_message`: Boolean. If `true`, this is a "Custom Instruction" added by the user, appearing as a system message.
*   `finish_details`: `{ "type": "stop", "stop_tokens": [...] }`
*   `citations`: Array of source objects (for Search/Browsing).
*   `user_context_message_data`: Contains "About User" / "About Model" memory data.

---

# 5. Specialized Feature Edge Cases

### 5.1 Voice Mode
*   **Audio:** Actual audio blobs are **not** currently included in the standard JSON export.
*   **Transcription:** The conversation renders as standard `user` (transcript of your voice) and `assistant` (transcript of AI voice) text messages.
*   **Detection:** Look for specific model slugs like `gpt-4o-audio-preview` or metadata flags indicating audio input.

### 5.2 System Messages
There are two types of system messages:
1.  **Internal:** "You are ChatGPT, a large language model..." (Often hidden or `message: null` in the root).
2.  **User Defined:** Custom Instructions. These appear with `role: system` but often have `metadata.is_user_system_message: true`. Community parsers explicitly extract these.

### 5.3 Missing Content (Nulls)
*   **Failed Generations:** If a request fails (orange text in UI), the `content` or `parts` might be `null`.
*   **Structural Nodes:** The root node almost always has `message: null`.
*   **Defensive Parsing:** Always check `if node.message and node.message.content and node.message.content.parts`.

---

# 6. Auxiliary File Schemas

### `user.json`
```json
{
  "id": "user-UUID",
  "email": "user@email.com",
  "name": "Display Name",
  "image": "https://gravatar...",
  "chatgpt_plus_user": true,
  "structure": "user_system"
}
```

### `message_feedback.json`
```json
[
  {
    "id": "UUID",
    "conversation_id": "UUID",
    "message_id": "UUID-of-target-message",
    "rating": "thumbsUp" | "thumbsDown",
    "text": "User written feedback",
    "create_time": 1679999999
  }
]
```

---

# 7. Tools, Scripts, and Resources

Since there is no official API documentation for the export, community tools are the standard.

### 7.1 `jq` One-Liners (Command Line extraction)

**Extract Title and Creation Time:**
```bash
jq -r '.[] | "\(.title // "NO_TITLE") | \(.create_time)"' conversations.json
```

**Extract Linear Text from specific conversation (simplified):**
```bash
jq -r '.[] | select(.title=="Specific Title") | .mapping[] | select(.message != null) | "\(.message.author.role): \(.message.content.parts[0])"' conversations.json
```
*(Note: The above `jq` dumps all branches mixed together. For proper linear order, you need a script that follows the `parent` pointers).*

### 7.2 Key Community Repositories
*   **[sanand0/openai-conversations](https://github.com/sanand0/openai-conversations):** TypeScript schema & analysis. Excellent for type definitions.
*   **[slyubarskiy/chatgpt-conversation-extractor](https://github.com/slyubarskiy/chatgpt-conversation-extractor):** Python tool. Implements the "Golden Path" graph traversal correctly.
*   **[z1shivam/chatgpt-export-explorer](https://github.com/z1shivam/chatgpt-export-explorer):** A web UI to load and visualize the JSON structure.

### 7.3 Sources
1.  **OpenAI Help:** [How do I export my data?](https://help.openai.com/en/articles/7260999-how-do-i-export-my-chatgpt-history-and-data)
2.  **OpenAI Developer Forum:** [Decoding Exported Data](https://community.openai.com/t/decoding-exported-data-by-parsing-conversations-json-and-or-chat-html/403144)
3.  **Hugging Face:** [Discussions on extraction edge cases](https://discuss.huggingface.co/t/how-can-i-extract-all-conversations-from-my-chatgpt-json-export-files-i-m-not-a-developer/157146)
