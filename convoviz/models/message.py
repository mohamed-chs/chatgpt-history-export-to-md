"""Message model - pure data class.

Object path: conversations.json -> conversation -> mapping -> mapping node -> message
"""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict

from convoviz.exceptions import MessageContentError

AuthorRole = Literal["user", "assistant", "system", "tool"]


class MessageAuthor(BaseModel):
    """Author information for a message."""

    role: AuthorRole
    name: str | None = None
    metadata: dict[str, Any] = {}


class MessageContent(BaseModel):
    """Content of a message."""

    content_type: str
    parts: list[str] | None = None
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
    metadata: MessageMetadata
    recipient: str

    @property
    def text(self) -> str:
        """Extract the text content of the message."""
        if self.content.parts is not None:
            return str(self.content.parts[0]) if self.content.parts else ""
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
