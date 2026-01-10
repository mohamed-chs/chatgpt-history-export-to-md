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
    parts: list[Any] | None = None
    text: str | None = None
    result: str | None = None


class MessageMetadata(BaseModel):
    """Metadata for a message."""

    model_slug: str | None = None
    invoked_plugin: dict[str, Any] | None = None
    is_user_system_message: bool | None = None
    user_context_message_data: dict[str, Any] | None = None

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
        if not self.content.parts:
            return []

        image_ids = []
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
        return image_ids

    @property
    def text(self) -> str:
        """Extract the text content of the message."""
        if self.content.parts is not None:
            # Handle multimodal content where parts can be mixed strings and dicts
            text_parts = []
            for part in self.content.parts:
                if isinstance(part, str):
                    text_parts.append(part)
                elif isinstance(part, dict) and "text" in part:
                    # Some parts might be dicts wrapping text (e.g. code interpreter?)
                    # But based on spec, usually text is just a string in the list.
                    # We'll stick to string extraction for now.
                    pass

            # If we found string parts, join them.
            # If parts existed but no strings (e.g. only images), return empty string?
            # Or should we return a placeholder? For now, let's return joined text.
            if text_parts:
                return "".join(text_parts)

            # If parts list is not empty but contains no strings, we might want to fall through
            # or return empty string if we consider it "handled".
            # The original code returned "" if parts was empty list.
            if self.content.parts:
                return ""

        if self.content.text is not None:
            return self.content.text
        if self.content.result is not None:
            return self.content.result
        raise MessageContentError(self.id)

    @property
    def has_content(self) -> bool:
        """Check if the message has extractable content."""
        return bool(
            self.content.parts or self.content.text is not None or self.content.result is not None
        )

    @property
    def is_empty(self) -> bool:
        """Check if the message is effectively empty (no text, no images)."""
        try:
            return not self.text.strip() and not self.images
        except MessageContentError:
            return True

    @property
    def is_hidden(self) -> bool:
        """Check if message should be hidden in export.

        Hidden if:
        1. It is empty (no text, no images).
        2. It is an internal system message (not custom instructions).
        3. It is a browser tool output (intermediate search steps).
        """
        if self.is_empty:
            return True

        # Hide internal system messages
        if self.author.role == "system":
            # Only show if explicitly marked as user system message (Custom Instructions)
            return not self.metadata.is_user_system_message

        # Hide browser tool outputs (usually intermediate search steps)
        if self.author.role == "tool" and self.author.name == "browser":
            return True

        # Hide assistant calls to browser tool (e.g. "search(...)") or code interpreter
        if self.author.role == "assistant" and (
            self.recipient == "browser" or self.content.content_type == "code"
        ):
            return True

        # Hide browsing status messages
        return self.content.content_type == "tether_browsing_display"
