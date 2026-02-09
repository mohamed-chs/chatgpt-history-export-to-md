"""Message interpretation utilities.

Keeps complex extraction and visibility rules outside of pure data models.
"""

from __future__ import annotations

import json
from typing import Any

from convoviz.exceptions import MessageContentError


def extract_message_images(message: Any) -> list[str]:
    """Extract image asset pointers from the message content."""
    image_ids: list[str] = []
    image_id_set: set[str] = set()

    if message.content.parts:
        for part in message.content.parts:
            if isinstance(part, dict) and part.get("content_type") == "image_asset_pointer":
                pointer = part.get("asset_pointer", "")
                # Strip prefixes like "file-service://" or "sediment://"
                if pointer.startswith("file-service://"):
                    pointer = pointer[len("file-service://") :]
                elif pointer.startswith("sediment://"):
                    pointer = pointer[len("sediment://") :]

                if pointer and pointer not in image_id_set:
                    image_ids.append(pointer)
                    image_id_set.add(pointer)

    # Also check metadata.attachments for images/files that should be rendered
    if message.metadata.attachments:
        for att in message.metadata.attachments:
            if not isinstance(att, dict):
                continue
            att_id = att.get("id")
            if not att_id or att_id in image_id_set:
                continue
            if _is_image_attachment(att):
                image_ids.append(att_id)
                image_id_set.add(att_id)

    return image_ids


def _render_thoughts(thoughts: list[dict[str, Any]] | None) -> str:
    """Render thoughts content (list of thought objects with summary/content)."""
    if not thoughts:
        return ""
    summaries = []
    for thought in thoughts:
        if isinstance(thought, dict) and (summary := thought.get("summary")):
            summaries.append(summary)
    return "\n".join(summaries) if summaries else ""


def _render_tether_quote(content: Any) -> str:
    """Render tether_quote content as a blockquote."""
    quote_text = content.text or ""
    if not quote_text.strip():
        return ""
    # Format as blockquote with source
    lines = [f"> {line}" for line in quote_text.strip().split("\n")]
    blockquote = "\n".join(lines)
    # Add attribution if we have title/domain/url
    if content.title and content.url:
        blockquote += f"\n> — [{content.title}]({content.url})"
    elif content.domain and content.url:
        blockquote += f"\n> — [{content.domain}]({content.url})"
    elif content.url:
        blockquote += f"\n> — <{content.url}>"
    return blockquote


def _render_canvas(name: str, content: str) -> str:
    """Format a Canvas/canmore document as markdown."""
    return f"### Canvas: {name}\n\n{content}"


def extract_message_text(message: Any) -> str:
    """Extract the text content of the message."""
    content = message.content

    # 1. Handle multimodal parts
    if content.parts is not None:
        text_parts = []
        for part in content.parts:
            match part:
                case str():
                    # Check if this string is a JSON Canvas document
                    if message.recipient == "canmore.create_textdoc":
                        try:
                            data = json.loads(part)
                            if isinstance(data, dict) and "content" in data and "name" in data:
                                text_parts.append(_render_canvas(data["name"], data["content"]))
                                continue
                        except (json.JSONDecodeError, TypeError):
                            pass
                    text_parts.append(part)
                case {"content": str(c), "name": str(n)} if message.recipient == "canmore.create_textdoc":
                    text_parts.append(_render_canvas(n, c))
                case {"text": str(t)}:
                    text_parts.append(t)

        if text_parts:
            return "".join(text_parts)
        if content.parts:  # If we had non-text parts (like images)
            return ""

    # 2. Handle specific content types via match
    match content.content_type:
        case "tether_quote":
            return _render_tether_quote(content)
        case "reasoning_recap" if content.content is not None:
            return content.content
        case "thoughts" if content.thoughts is not None:
            return _render_thoughts(content.thoughts)

    # 3. Fallback to standard text/result fields
    if content.text is not None:
        if message.recipient == "canmore.create_textdoc":
            try:
                data = json.loads(content.text)
                if isinstance(data, dict) and "content" in data and "name" in data:
                    return _render_canvas(data["name"], data["content"])
            except (json.JSONDecodeError, TypeError):
                pass
        return content.text

    if content.result is not None:
        return content.result

    raise MessageContentError(message.id)


_IMAGE_EXTS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".bmp",
    ".tiff",
    ".svg",
}


def _is_image_attachment(att: dict[str, Any]) -> bool:
    """Return True if attachment metadata looks like an image."""
    mime = att.get("mime_type") or att.get("content_type") or att.get("file_type")
    if isinstance(mime, str) and mime.lower().startswith("image/"):
        return True
    name = att.get("name")
    if isinstance(name, str):
        lower = name.lower()
        return any(lower.endswith(ext) for ext in _IMAGE_EXTS)
    return False


def extract_canvas_document(message: Any) -> dict[str, Any] | None:
    """Extract Canvas document if this message created one."""
    if message.recipient != "canmore.create_textdoc":
        return None

    def try_parse_canvas(val: Any) -> dict[str, Any] | None:
        data = None
        if isinstance(val, dict):
            data = val
        elif isinstance(val, str):
            try:
                data = json.loads(val)
            except (json.JSONDecodeError, TypeError):
                return None

        if isinstance(data, dict) and "content" in data and "name" in data:
            return {
                "name": data["name"],
                "type": data.get("type", "unknown"),
                "content": data["content"],
            }
        return None

    # Try all parts in order
    if message.content.parts:
        for part in message.content.parts:
            doc = try_parse_canvas(part)
            if doc:
                return doc

    # Try content.text
    if message.content.text:
        doc = try_parse_canvas(message.content.text)
        if doc:
            return doc

    return None


def is_message_hidden(message: Any) -> bool:
    """Check if message should be hidden in export."""
    if message.is_empty or message.metadata.is_visually_hidden_from_conversation:
        return True

    match message.author.role:
        case "system":
            return not message.metadata.is_user_system_message

        case "tool":
            match message.author.name:
                case "bio" | "web.run" | "web.search":
                    return True
                case "browser":
                    return message.content.content_type != "tether_quote"
                case "dalle.text2im" if message.content.content_type == "text" and not message.images:
                    return True

        case "assistant":
            # Hide code interpreter input and internal tool calls
            if message.content.content_type == "code":
                return True
            if message.recipient not in ("all", "python", None):
                return True

    # Generic content type filters
    return message.content.content_type in (
        "sonic_webpage",
        "system_error",
        "tether_browsing_display",
        "thoughts",
        "reasoning_recap",
    )


def extract_internal_citation_map(message: Any) -> dict[str, dict[str, str | None]]:
    """Extract a map of citation IDs to metadata from content parts."""
    citation_mapping: dict[str, dict[str, str | None]] = {}
    parts = message.content.parts or []

    def process_entry(entry: Any) -> None:
        if not isinstance(entry, dict):
            return
        ref_id = entry.get("ref_id")
        if not isinstance(ref_id, dict):
            return
        if ref_id.get("ref_type") != "search":
            return

        turn_idx = ref_id.get("turn_index")
        ref_idx = ref_id.get("ref_index")

        if turn_idx is not None and ref_idx is not None:
            key = f"turn{turn_idx}search{ref_idx}"
            citation_mapping[key] = {
                "title": entry.get("title"),
                "url": entry.get("url"),
            }

    for part in parts:
        if isinstance(part, dict):
            if part.get("type") == "search_result":
                process_entry(part)
            elif part.get("type") == "search_result_group":
                for entry in part.get("entries", []):
                    process_entry(entry)

    if message.metadata and message.metadata.search_result_groups:
        for group in message.metadata.search_result_groups:
            if isinstance(group, dict):
                for entry in group.get("entries", []):
                    process_entry(entry)

    return citation_mapping
