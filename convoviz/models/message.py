"""Message model - pure data class.

Object path: conversations.json -> conversation -> mapping -> mapping node -> message
"""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from convoviz.exceptions import MessageContentError

AuthorRole = Literal["user", "assistant", "system", "tool", "function"]


class MessageAuthor(BaseModel):
    """Author information for a message."""

    role: AuthorRole
    name: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class MessageContent(BaseModel):
    """Content of a message."""

    content_type: str
    parts: list[str | dict[str, Any]] | None = None
    text: str | None = None
    result: str | None = None
    name: str | None = None  # For Canvas/canmore
    content: str | Any | None = None  # for reasoning_recap or Canvas
    thoughts: list[dict[str, Any]] | None = None  # for o1/o3 reasoning
    url: str | None = None
    domain: str | None = None
    title: str | None = None


class MessageMetadata(BaseModel):
    """Metadata for a message."""

    model_slug: str | None = None
    invoked_plugin: dict[str, Any] | None = None
    is_user_system_message: bool | None = None
    is_visually_hidden_from_conversation: bool | None = None
    user_context_message_data: dict[str, Any] | None = None
    citations: list[dict[str, Any]] | None = None
    search_result_groups: list[dict[str, Any]] | None = None
    content_references: list[dict[str, Any]] | None = None
    attachments: list[dict[str, Any]] | None = None

    model_config = ConfigDict(protected_namespaces=())


class Message(BaseModel):
    """A single message in a conversation.

    This is a pure data model - rendering logic is in the renderers module.
    """

    id: str
    author: MessageAuthor
    create_time: datetime | None = None
    update_time: datetime | None = None
    content: MessageContent
    status: str
    end_turn: bool | None = None
    weight: float
    metadata: MessageMetadata = Field(default_factory=MessageMetadata)
    recipient: str | None = None

    @property
    def images(self) -> list[str]:
        """Extract image asset pointers from the message content."""
        image_ids = []

        if self.content.parts:
            for part in self.content.parts:
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
        if self.metadata.attachments:
            for att in self.metadata.attachments:
                if (att_id := att.get("id")) and att_id not in image_ids:
                    image_ids.append(att_id)

        return image_ids

    @property
    def text(self) -> str:
        """Extract the text content of the message."""
        if self.content.parts is not None:
            # Handle multimodal content where parts can be mixed strings and dicts
            text_parts = []
            for part in self.content.parts:
                if isinstance(part, str):
                    # Check if this string is actually a JSON-encoded Canvas document
                    if self.recipient == "canmore.create_textdoc":
                        import json

                        try:
                            data = json.loads(part)
                            if isinstance(data, dict) and "content" in data and "name" in data:
                                text_parts.append(
                                    f"### Canvas: {data['name']}\n\n{data['content']}"
                                )
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

            if self.content.parts:
                return ""

        # tether_quote: render as a blockquote with attribution (check before .text)
        if self.content.content_type == "tether_quote":
            return self._render_tether_quote()

        # Check if text itself is a JSON-encoded Canvas document
        if self.content.text is not None:
            if self.recipient == "canmore.create_textdoc":
                import json

                try:
                    data = json.loads(self.content.text)
                    if isinstance(data, dict) and "content" in data and "name" in data:
                        return f"### Canvas: {data['name']}\n\n{data['content']}"
                except (json.JSONDecodeError, TypeError):
                    pass
            return self.content.text

        if self.content.result is not None:
            return self.content.result
        # reasoning_recap content type uses 'content' field
        if self.content.content is not None:
            return self.content.content
        # thoughts content type uses 'thoughts' field (list of thought objects)
        if self.content.thoughts is not None:
            return self._render_thoughts()
        raise MessageContentError(self.id)

    def _render_thoughts(self) -> str:
        """Render thoughts content (list of thought objects with summary/content)."""
        if not self.content.thoughts:
            return ""
        summaries = []
        for thought in self.content.thoughts:
            if isinstance(thought, dict) and (summary := thought.get("summary")):
                summaries.append(summary)
        return "\n".join(summaries) if summaries else ""

    def _render_tether_quote(self) -> str:
        """Render tether_quote content as a blockquote."""
        quote_text = self.content.text or ""
        if not quote_text.strip():
            return ""
        # Format as blockquote with source
        lines = [f"> {line}" for line in quote_text.strip().split("\n")]
        blockquote = "\n".join(lines)
        # Add attribution if we have title/domain/url
        if self.content.title and self.content.url:
            blockquote += f"\n> — [{self.content.title}]({self.content.url})"
        elif self.content.domain and self.content.url:
            blockquote += f"\n> — [{self.content.domain}]({self.content.url})"
        elif self.content.url:
            blockquote += f"\n> — <{self.content.url}>"
        return blockquote

    @property
    def has_content(self) -> bool:
        """Check if the message has extractable content."""
        return bool(
            self.content.parts
            or self.content.text is not None
            or self.content.result is not None
            or self.content.content is not None  # reasoning_recap
            or self.content.thoughts is not None  # o1/o3 thoughts
        )

    @property
    def is_empty(self) -> bool:
        """Check if the message is effectively empty (no text, no images)."""
        try:
            return not self.text.strip() and not self.images
        except MessageContentError:
            return True

    @property
    def canvas_document(self) -> dict[str, Any] | None:
        """Extract Canvas document if this message created one."""
        if self.recipient != "canmore.create_textdoc":
            return None

        import json

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
        if self.content.parts:
            doc = try_parse_canvas(self.content.parts[0])
            if doc:
                return doc

        # Try content.text
        if self.content.text:
            doc = try_parse_canvas(self.content.text)
            if doc:
                return doc

        return None

    @property
    def is_hidden(self) -> bool:
        """Check if message should be hidden in export.

        Hidden if:
        1. It is empty (no text, no images).
        2. Explicitly marked as visually hidden.
        3. It is an internal system message (not custom instructions).
        4. It is a tool output (unless explicitly requested).
        5. It is a redundant DALL-E textual status update.
        6. It is from internal bio (memory) or web.run orchestration tools.
        7. It is code interpreter input (content_type="code").
        8. It is browsing status, internal reasoning (o1/o3), or massive web scraps (sonic_webpage).
        """
        if self.is_empty:
            return True

        # Explicitly marked as hidden by OpenAI
        if self.metadata.is_visually_hidden_from_conversation:
            return True

        # Hide internal system messages
        if self.author.role == "system":
            # Only show if explicitly marked as user system message (Custom Instructions)
            return not self.metadata.is_user_system_message

        # Hide sonic_webpage (massive scraped text) and system_error
        if self.content.content_type in ("sonic_webpage", "system_error"):
            return True

        if self.author.role == "tool":
            # Hide memory updates (bio) and internal search orchestration (web.run)
            if self.author.name in ("bio", "web.run"):
                return True

            # Hide browser tool outputs (intermediate search steps)
            # EXCEPTION: tether_quote (citations) should remain visible
            if self.author.name == "browser":
                return self.content.content_type != "tether_quote"

            # Hide DALL-E textual status ("DALL·E displayed 1 images...")
            if (
                self.author.name == "dalle.text2im"
                and self.content.content_type == "text"
                # Check if it doesn't have images (just in case they attach images to text logic)
                and not self.images
            ):
                return True

        # Hide assistant messages targeting tools (e.g., search(...), code input)
        # recipient="all" or None means it's for the user; anything else is internal
        # recipient="python" : code interpreter code
        if self.author.role == "assistant" and self.recipient not in ("all", "python", None):
            return True

        # Hide code interpreter input (content_type="code")
        if self.author.role == "assistant" and self.content.content_type == "code":
            return True

        # Hide browsing status and internal reasoning steps (o1/o3 models)
        return self.content.content_type in (
            "tether_browsing_display",
            "thoughts",
            "reasoning_recap",
        )

    @property
    def internal_citation_map(self) -> dict[str, dict[str, str | None]]:
        """Extract a map of citation IDs to metadata from content parts.

        Used for resolving embedded citations (e.g. citeturn0search18).
        Key format: "turn{turn_index}search{ref_index}"
        """
        if not self.content.parts:
            return {}

        citation_mapping = {}

        # Helper to process a single search result entry
        def process_entry(entry: dict[str, Any]) -> None:
            ref_id = entry.get("ref_id")
            if not ref_id:
                return
            # Only care about search results for now
            if ref_id.get("ref_type") != "search":
                return

            turn_idx = ref_id.get("turn_index")
            ref_idx = ref_id.get("ref_index")

            if turn_idx is not None and ref_idx is not None:
                # turn_idx is int, ref_idx is int
                key = f"turn{turn_idx}search{ref_idx}"
                citation_mapping[key] = {
                    "title": entry.get("title"),
                    "url": entry.get("url"),
                }

        # 1. Extract from self.content.parts
        if self.content and self.content.parts:
            for part in self.content.parts:
                if isinstance(part, dict):
                    if part.get("type") == "search_result":
                        process_entry(part)
                    elif part.get("type") == "search_result_group":
                        for entry in part.get("entries", []):
                            process_entry(entry)

        # 2. Extract from metadata.search_result_groups (if present)
        if self.metadata and self.metadata.search_result_groups:
            for group in self.metadata.search_result_groups:
                if isinstance(group, dict):
                    # Groups might have 'entries' or be flat?
                    # Based on name 'groups', likely similar to part structure
                    for entry in group.get("entries", []):
                        process_entry(entry)

        return citation_mapping
