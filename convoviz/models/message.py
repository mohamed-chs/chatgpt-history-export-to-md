"""Message model - pure data class.

Object path: conversations.json -> conversation -> mapping -> mapping node -> message
"""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from convoviz.exceptions import MessageContentError
from convoviz.message_logic import (
    extract_canvas_document,
    extract_internal_citation_map,
    extract_message_images,
    extract_message_text,
    is_message_hidden,
)

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
        return extract_message_images(self)

    @property
    def text(self) -> str:
        """Extract the text content of the message."""
        return extract_message_text(self)

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
        return extract_canvas_document(self)

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
        return is_message_hidden(self)

    @property
    def internal_citation_map(self) -> dict[str, dict[str, str | None]]:
        """Extract a map of citation IDs to metadata from content parts.

        Used for resolving embedded citations (e.g. citeturn0search18).
        Key format: "turn{turn_index}search{ref_index}"
        """
        return extract_internal_citation_map(self)
