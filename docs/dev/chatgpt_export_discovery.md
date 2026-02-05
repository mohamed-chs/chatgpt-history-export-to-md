# ChatGPT Export Audit Guide

This guide details the methodology and commands used to perform a "Deep Audit" of a ChatGPT export (`conversations.json`). It is designed to help developers find high-signal, "noteworthy" conversations for snapshot testing or feature development. 

**Note:** The queries and patterns listed below are representative examples of common high-signal cases and are by no means exhaustive.

## 0. Preparation: Prettifying the Export
The raw `conversations.json` file is typically minified into a single, massive line. While `jq` processes this perfectly, it makes standard CLI tools like `grep`, `head`, or `less` almost useless. 

Before starting, create a formatted version:
```bash
jq . conversations.json > conversations_formatted.json
```
*The commands below work on either file, but using the formatted version allows you to pipe results into `grep` for quick secondary filtering.*

---

## 1. Methodology: The Frugal Flow

When dealing with large exports (e.g., 50MB+), do not load the file into a text editor or an LLM context. Instead, use a **Search -> Peek -> Pin** loop:

1.  **Search**: Use `jq` to aggregate IDs and titles matching specific structural patterns.
2.  **Peek**: Use `jq` to inspect only the `metadata` or specific `parts` of a single candidate ID.
3.  **Pin**: Save the ID to a tracking manifest (like `conversation_list.json`) for automated testing.

---

## 2. Example Queries (Non-Exhaustive)

The following commands serve as a baseline for discovery. Users are encouraged to adapt these patterns as OpenAI introduces new features or internal schema changes.

### General Discovery
**Find all unique recipients (Tools/Agents):**
Useful for identifying new features (like `canmore` or `bio`).
```bash
jq -r '.[] | .mapping[] | select(.message.recipient != null) | .message.recipient' conversations.json | sort -u
```

**Count occurrences of specific content types:**
```bash
jq -r '.[] | .mapping[] | .message.content.content_type' conversations.json | sort | uniq -c | sort -rn
```

---

### Feature-Specific Patterns

#### 🎨 DALL-E (Images)
Finds conversations where the `recipient` was specifically the DALL-E tool.
```bash
jq -r '.[] | select(.mapping | to_entries | any(.value.message.recipient == "dalle.text2im")) | [.id, .title] | @tsv' conversations.json
```

#### 🏗️ Canvas (canmore)
Finds the new "Canvas" document-editing conversations.
```bash
jq -r '.[] | select(.mapping | to_entries | any(.value.message.recipient == "canmore.create_textdoc")) | [.id, .title] | @tsv' conversations.json
```

#### 🧠 AI Reasoning (o1/o3)
Finds conversations using the new reasoning summaries.
```bash
jq -r '.[] | select(.mapping | to_entries | any(.value.message.content.content_type == "reasoning_recap")) | [.id, .title] | @tsv' conversations.json
```

#### 👻 Ghost Citations (The Edge Case)
Finds messages that *performed a search* (`search_result_groups` exists) but *failed to generate citation metadata* (empty `citations` list). This is a critical rendering edge case.
```bash
jq -r '.[] | select(
  .mapping | to_entries | any(
    .value.message.metadata.search_result_groups != null and 
    (.value.message.metadata.citations == null or (.value.message.metadata.citations | length == 0))
  )
) | [.id, .title] | @tsv' conversations.json
```

#### 🌳 Deep Branching
Finds conversations with the highest number of branches (edits/regenerations) at a single point.
```bash
jq -r '.[] | {id: .id, title: .title, max_branches: ([.mapping | to_entries | group_by(.value.parent) | .[] | length] | max)} | select(.max_branches >= 4) | [.id, .max_branches, .title] | @tsv' conversations.json | sort -rn -k2
```

#### 📝 Custom Instructions
Finds conversations where the user's system message (Custom Instructions) was active.
```bash
jq -r '.[] | select(.mapping | to_entries | any(.value.message.metadata.is_user_system_message == true)) | [.id, .title] | @tsv' conversations.json
```

---

## 3. High-Value "Peek" Command
Once you have an ID, use this to see exactly what "junk" or "treasure" is inside without drowning in JSON:

```bash
# Peek at message roles and content types for a specific ID
jq -r '.[] | select(.id == "YOUR_ID_HERE") | .mapping | to_entries | .[] | select(.value.message != null) | [.value.message.author.role, .value.message.content.content_type] | @tsv' conversations.json
```

## 4. Why this matters
OpenAI frequently changes the "internal" schema of these exports without updating documentation. By using structural `jq` queries instead of simple keyword searches, we can detect evolving patterns:
1.  **Protocol Shifts**: e.g., moving from `file-service://` to `sediment://`.
2.  **Tool Noise**: Finding new tool names (like `web.run` or `web.search`) to filter them out of Markdown.
3.  **Metadata Richness**: Spotting new fields like `voice`, `is_starred`, or `reasoning_status`.
