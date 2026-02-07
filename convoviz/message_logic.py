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

    if message.content.parts:
        for part in message.content.parts:
            if isinstance(part, dict) and part.get("content_type") == "image_asset_pointer":
                pointer = part.get("asset_pointer", "")
                # Strip prefixes like "file-service://" or "sediment://"
                if pointer.startswith("file-service://"):
                    pointer = pointer[len("file-service://") :]
                elif pointer.startswith("sediment://"):
                    pointer = pointer[len("sediment://") :]

                if pointer:
                    image_ids.append(pointer)

    # Also check metadata.attachments for images/files that should be rendered
    if message.metadata.attachments:
        for att in message.metadata.attachments:
            if (att_id := att.get("id")) and att_id not in image_ids:
                image_ids.append(att_id)

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


def extract_message_text(message: Any) -> str:
    """Extract the text content of the message."""
    if message.content.parts is not None:
        # Handle multimodal content where parts can be mixed strings and dicts
        text_parts = []
        for part in message.content.parts:
            if isinstance(part, str):
                # Check if this string is actually a JSON-encoded Canvas document
                if message.recipient == "canmore.create_textdoc":
                    try:
                        data = json.loads(part)
                        if isinstance(data, dict) and "content" in data and "name" in data:
                            text_parts.append(f"### Canvas: {data['name']}\n\n{data['content']}")
                            continue
                    except (json.JSONDecodeError, TypeError):
                        pass
                text_parts.append(part)
            elif isinstance(part, dict):
                # Handle Canvas/canmore documents embedded in parts
                if part.get("content") and part.get("name"):
                    text_parts.append(f"### Canvas: {part['name']}\n\n{part['content']}")
                elif "text" in part:
                    # Some parts might be dicts wrapping text
                    text_parts.append(str(part["text"]))

        # If we found string parts, join them.
        if text_parts:
            return "".join(text_parts)

        if message.content.parts:
            return ""

    # tether_quote: render as a blockquote with attribution (check before .text)
    if message.content.content_type == "tether_quote":
        return _render_tether_quote(message.content)

    # Check if text itself is a JSON-encoded Canvas document
    if message.content.text is not None:
        if message.recipient == "canmore.create_textdoc":
            try:
                data = json.loads(message.content.text)
                if isinstance(data, dict) and "content" in data and "name" in data:
                    return f"### Canvas: {data['name']}\n\n{data['content']}"
            except (json.JSONDecodeError, TypeError):
                pass
        return message.content.text

    if message.content.result is not None:
        return message.content.result
    # reasoning_recap content type uses 'content' field
    if message.content.content is not None:
        return message.content.content
    # thoughts content type uses 'thoughts' field (list of thought objects)
    if message.content.thoughts is not None:
        return _render_thoughts(message.content.thoughts)
    raise MessageContentError(message.id)


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

    # Try parts[0]
    if message.content.parts:
        doc = try_parse_canvas(message.content.parts[0])
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
    if message.is_empty:
        return True

    # Explicitly marked as hidden by OpenAI
    if message.metadata.is_visually_hidden_from_conversation:
        return True

    # Hide internal system messages
    if message.author.role == "system":
        # Only show if explicitly marked as user system message (Custom Instructions)
        return not message.metadata.is_user_system_message

    # Hide sonic_webpage (massive scraped text) and system_error
    if message.content.content_type in ("sonic_webpage", "system_error"):
        return True

    if message.author.role == "tool":
        # Hide memory updates (bio) and internal search orchestration (web.run)
        if message.author.name in ("bio", "web.run"):
            return True

        # Hide browser tool outputs (intermediate search steps)
        # EXCEPTION: tether_quote (citations) should remain visible
        if message.author.name == "browser":
            return message.content.content_type != "tether_quote"

        # Hide DALL-E textual status ("DALL·E displayed 1 images...")
        if (
            message.author.name == "dalle.text2im"
            and message.content.content_type == "text"
            and not message.images
        ):
            return True

    # Hide assistant messages targeting tools (e.g., search(...), code input)
    # recipient="all" or None means it's for the user; anything else is internal
    # recipient="python" : code interpreter code (still hidden via content_type="code")
    if message.author.role == "assistant" and message.recipient not in ("all", "python", None):
        return True

    # Hide code interpreter input (content_type="code")
    if message.author.role == "assistant" and message.content.content_type == "code":
        return True

    # Hide browsing status and internal reasoning steps (o1/o3 models)
    return message.content.content_type in (
        "tether_browsing_display",
        "thoughts",
        "reasoning_recap",
    )


def extract_internal_citation_map(message: Any) -> dict[str, dict[str, str | None]]:
    """Extract a map of citation IDs to metadata from content parts."""
    if not message.content.parts:
        return {}

    citation_mapping: dict[str, dict[str, str | None]] = {}

    def process_entry(entry: dict[str, Any]) -> None:
        ref_id = entry.get("ref_id")
        if not ref_id:
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

    for part in message.content.parts:
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
