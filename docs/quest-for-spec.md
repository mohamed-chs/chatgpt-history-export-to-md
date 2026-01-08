# **Executive Summary: The State of AI Exports**

*   **ChatGPT (OpenAI):** The most complex and mature export. It utilizes a **Directed Acyclic Graph (DAG)** structure. It captures every edit, branch, and retry in a tree format. It is *not* a linear list. The official export is a global archive.
*   **Claude (Anthropic):** A simpler, generally **Linear** export. It heavily relies on embedding "Artifacts" (code/previews) directly into the message text rather than separating them. Export methods vary significantly between Consumer (Email/ZIP) and Enterprise/Browser-sniffing methods.
*   **Gemini (Google):** The most fragmented and inconsistent. Data is split between **Google Takeout** (often buggy or empty) and **My Activity**. Community developers often prefer parsing "Shared Public Pages" over the official Takeout files due to reliability issues.

---

# **1. ChatGPT (OpenAI)**

### **Source & Retrieval**
*   **Official Method:** Settings > Data Controls > Export Data. (Result: ZIP file sent to email).
*   **Primary File:** `conversations.json` (inside the ZIP).
*   **Asset Location:** Images (DALL-E) and other binaries are stored in a separate folder within the ZIP, referenced by hashed filenames in the JSON.

### **The Schema (Comprehensive Superset)**
The core structure is a **mapping** of message UUIDs. You cannot simply iterate through a list; you must traverse the graph from `current_node` backwards to `parent` to reconstruct a conversation, or traverse `children` to find forks.

```typescript
interface ChatGPTExport {
  // Sometimes top-level array, sometimes wrapped in an object depending on version
  [index: number]: Conversation; 
}

interface Conversation {
  id: string;             // UUID of the conversation
  title: string;          // Inferred title
  create_time: number;    // Unix timestamp (float)
  update_time: number;
  mapping: {
    [messageId: string]: Node; // The core graph structure
  };
  moderation_results: any[];
  current_node: string;   // The UUID of the last message in the "active" branch
  plugin_ids: string[] | null;
  gizmo_id: string | null; // If this is a custom GPT
  is_archived?: boolean;
}

interface Node {
  id: string;
  message: Message | null; // Null for system/root nodes
  parent: string | null;   // UUID of parent message
  children: string[];      // UUIDs of all children (Edits/Regens = multiple children)
}

interface Message {
  id: string;
  author: {
    role: "system" | "user" | "assistant" | "tool" | "function";
    name: string | null;
    metadata: any;
  };
  create_time: number;
  update_time: number | null;
  content: Content; 
  status: "finished_successfully" | "in_progress";
  end_turn: boolean | null;
  weight: number;
  metadata: MessageMetadata;
  recipient: "all" | string;
}

// Content is Polymorphic and Complex
type Content = 
  | { content_type: "text"; parts: string[] } // Standard text (parts can contain markdown)
  | { content_type: "code"; text: string; language: string } // Code Interpreter input
  | { content_type: "execution_output"; text: string } // Code Interpreter output
  | { content_type: "multimodal_text"; parts: MultiModalPart[] } // GPT-4o Vision inputs
  | { content_type: "tether_quote"; ... } // Citations/Search references
  | { content_type: "tether_browsing_code"; ... } // Search queries
  | { content_type: "image_asset_pointer"; asset_pointer: string; ... } // DALL-E ref
  | { content_type: "canvas"; ... }; // New Canvas feature

interface MessageMetadata {
  is_visually_hidden_from_conversation?: boolean; // Common for tool calls
  timestamp_: string;       // often "absolute" ISO string
  model_slug?: string;      // e.g., "gpt-4o"
  parent_id?: string;
  finish_details?: { type: "stop" | "max_tokens" | "interrupted" };
  // Citation/Search metadata:
  _cite_metadata?: any; 
}
```

### **Critical Edge Cases & "Gotchas"**

1.  **Non-Linearity (The Graph):** Unlike other apps, ChatGPT does not overwrite old messages when you edit or regenerate. It creates a new sibling node.
    *   *Parsing Hint:* To get the "chat as viewed," start at `current_node` and recursively follow `parent` links. To get "all history," you must recursively map all `children`.
2.  **Mapping vs. Arrays:** While the schema above shows `mapping`, some older or mobile-specific exports occasionally dumped `messages` as a linear array. Robust parsers must detect if `mapping` exists; if so, convert it to an array sorted by timestamp to make it usable.
3.  **Hashed Binary Assets:** DALL-E images and voice clips are not in the JSON. They are in the ZIP folder. The JSON `content` will refer to them via a file-hash string (e.g., `file-service_<hex>`). You must map these strings to the physical files in the extracted directory.
4.  **Canvas (New Feature):** Canvas content is often treated as a specialized tool call (e.g., `canmore`) or a specific `content_type`. The export may contain the *final* text of the canvas but might lose the granular "diffs" or version history of the canvas document unless you parse the specific tool inputs.
5.  **Hidden Unicode & Citations:** ChatGPT often uses hidden Unicode control characters within the `text` parts to mark where citations (footnotes) should appear. Naive Markdown converters might render these as broken artifacts.
6.  **Voice Mode:** Voice chats are exported as **transcriptions** (text). The actual audio files are rarely included in the standard `conversations.json` export flow, though metadata about the voice session exists.
7.  **Model Switching:** A single conversation can switch models mid-stream (e.g., GPT-3.5 to GPT-4). Do not assume one model per conversation; check `message.metadata.model_slug` on every node.
8.  **Deleted Branches:** If a user explicitly deletes a specific branch, it is removed from the `mapping`. However, if the tree integrity isn't maintained by the backend, this can result in "orphan" nodes (nodes with a `parent` ID that doesn't exist in the map).

---

# **2. Claude (Anthropic)**

### **Source & Retrieval**
*   **Official Method:** Settings > Privacy > Export Data (Emailed Link).
*   **Alternative (Simon Willison Method):** Copying the JSON response from Browser DevTools (Network Tab) for a specific chat.
*   **Primary File:** `conversations.json` (Consumer) or sometimes `.dms` / `jsonl` files (Enterprise/Beta features).

### **The Schema (Linear & Embedded)**
Claude's export is significantly flatter. It generally presents a linear view of the *current* state of the chat.

```typescript
interface ClaudeExport {
  [index: number]: ClaudeConversation;
}

interface ClaudeConversation {
  uuid: string;
  name: string;
  created_at: string; // ISO 8601 (e.g., "2024-01-01T12:00:00Z")
  updated_at: string;
  account: {
    uuid: string;
  };
  chat_messages: ClaudeMessage[];
}

interface ClaudeMessage {
  uuid: string;
  sender: "human" | "assistant";
  text: string;       // The raw message content
  created_at: string;
  updated_at: string;
  attachments: any[]; // Uploaded files metadata
  files: any[];       // Often distinct from attachments
  edits?: any[];      // Occasional array showing previous versions (inconsistent)
}
```

### **Critical Edge Cases & "Gotchas"**

1.  **Artifacts (The Big Missing Piece):**
    *   **The Issue:** Claude's UI shows "Artifacts" (React apps, SVGs, HTML previews) in a dedicated window.
    *   **The Data:** In the export, Artifacts do **not** exist as separate objects. The raw code is embedded directly inside the `text` string of the message, usually wrapped in XML tags like `<antArtifact>` or standard Markdown code blocks. You must write Regex to extract them.
2.  **Projects Data Excluded:** Data inside "Claude Projects" (custom instructions, uploaded knowledge base files) is **NOT** included in the standard user data export. Only the *chats* within that project are exported. The project knowledge base structure is lost.
3.  **Linearization:** If you retried a message 5 times, the official export usually contains only the *final/active* version. The complex tree structure seen in ChatGPT is flattened or discarded.
4.  **Browser JSON vs. Export JSON:** The JSON you can "sniff" from the browser network tab (`chat_messages`) is often richer than the official ZIP export, sometimes containing more metadata about tool use or rendering hints (`html` fields).
5.  **Format Variance:** Users have reported receiving `.jsonl` (JSON Lines) files or `.dms` files depending on the era of the export or if they are using "Claude Code" features.

---

# **3. Gemini (Google)**

### **Source & Retrieval**
*   **Method A (Official):** Google Takeout (Select "Gemini", formerly "Bard").
*   **Method B (Community Preferred):** Parsing "Shared Public Links" (`gemini.google.com/share/...`).
*   **Primary File:** `conversations.json` (inside `Gemini/` folder) OR `All Data.json`.

### **The Schema (Two Variants)**

#### **Variant A: Google Takeout (Official but Flaky)**
*Warning:* Google changes this format frequently. It is often less developer-friendly.

```typescript
interface GeminiTakeoutExport {
  conversations: GeminiConversation[];
}

interface GeminiConversation {
  id: string;
  title: string;
  createdTime: string;
  updatedTime: string;
  // Google often flattens messages into a list of "events"
  messages: GeminiMessage[];
}

interface GeminiMessage {
  id: string;
  author: "user" | "model" | "gemini";
  content: {
    parts: GeminiPart[]; 
  };
  timestamp: string;
  citations?: {
    uri: string;
    title: string;
    startIndex: number;
    endIndex: number;
  }[];
}

interface GeminiPart {
  text?: string;
  inlineData?: {
    mimeType: string;
    data: string; // Base64 (Rare)
  };
  fileData?: {
    fileUri: string; // Link to Google Drive/Photos
  };
}
```

#### **Variant B: Public Share Page (Scraped)**
This is often used by community tools (like `Gemini-Conversation-Downloader`) because it renders the final HTML/Markdown reliably.

```json
{
  "title": "Conversation title",
  "url": "https://gemini.google.com/share/...",
  "messages": [
    {
      "id": "msg-uuid",
      "role": "user" | "assistant",
      "timestamp": "ISO-Date",
      "content_html": "<p>...</p>",
      "content_text": "plain text fallback",
      "attachments": [ { "type": "image", "url": "...", "mime":"image/webp" } ],
      "metadata": { "model": "gemini-pro" }
    }
  ]
}
```

### **Critical Edge Cases & "Gotchas"**

1.  **The "Empty Takeout" Bug:** Several community threads report that Google Takeout sometimes returns an empty JSON file or strictly lists prompts without the model's responses. Always validate that `conversations.json` actually contains data.
2.  **Drafts/Candidates Discarded:** Gemini generates 3 drafts for every response. The export almost strictly contains **only the selected response**.
3.  **Image Link Rot:** Images generated by Gemini (Imagen) or uploaded by the user are often referenced by **URI** (links to Google infrastructure) rather than included as Base64 data or separate files in the ZIP. If the underlying Drive file is deleted or the link expires, the export contains broken references.
4.  **Split Personality (My Activity vs. App):**
    *   **Gemini App Takeout:** Contains the chat history (if not buggy).
    *   **My Activity Takeout:** Contains a log of your *queries* (prompts) mixed in with Google Search history, often without the model's reply.
5.  **Workspace Extensions Privacy:** If you used `@Gmail` or `@Drive` inside Gemini, the content retrieved from your personal emails/docs is generally **redacted** or not logged in the export for privacy reasons.

---

# **Comprehensive Summary Table**

| Feature | ChatGPT (`conversations.json`) | Claude (`conversations.json`) | Gemini (Takeout / Share) |
| :--- | :--- | :--- | :--- |
| **Structure** | **DAG / Tree** (Complex `mapping`) | **Linear List** | **Linear List** |
| **Parsing Difficulty** | **High** (Must handle recursion) | **Low** (Simple iteration) | **Med** (Inconsistent schema) |
| **Branches/Edits** | **Full History** (Parent/Child nodes) | **Final State Only** (Usually) | **Final State Only** |
| **Code/Artifacts** | Tool calls / Special Content Type | Embedded in `text` (Markdown/XML) | Embedded in `text` |
| **Images/Assets** | **Hashed References** (in ZIP) | Metadata / Link references | **URI Links** (prone to rot) |
| **Voice/Audio** | **Text Transcription** | N/A | **Text Transcription** |
| **Reliability** | **High** (Standardized) | **High** (Standardized) | **Low** (Takeout often empty) |

---

# **Community Resources & Tools**

Use these repositories to find the most up-to-date schema definitions in code (`types.ts`, `models.py`) and to see how developers handle the normalization logic.

### **For ChatGPT**
*   **[sanand0/openai-conversations](https://github.com/sanand0/openai-conversations):** The "Gold Standard" for the schema. Contains TypeScript definitions and logic to convert the `mapping` DAG into a linear list.
*   **[pionxzh/chatgpt-exporter](https://github.com/pionxzh/chatgpt-exporter):** A UI tool. Excellent for seeing how to visualize the graph structure.
*   **[mohamed-chs/chatgpt-history-export-to-md](https://github.com/mohamed-chs/chatgpt-history-export-to-md):** Python-based parser showing how to extract message content.

### **For Claude**
*   **[ryanschiang/claude-export](https://github.com/ryanschiang/claude-export):** Browser script that yields JSON/Markdown from active conversations.
*   **[Simon Willison's Notebook](https://simonwillison.net/2024/Aug/8/convert-claude-json-to-markdown/):** Explains the method of sniffing the Network tab to get a richer JSON than the official export.

### **For Gemini**
*   **[GeoAnima/Gemini-Conversation-Downloader](https://github.com/GeoAnima/Gemini-Conversation-Downloader):** A user script that parses the "Shared Page" JSON, which is often more reliable than the Google Takeout dump.
*   **[ChatExport.guide](https://chatexport.guide/en/guides/gemini/):** Community documentation tracking the changes in Google's export formats.
