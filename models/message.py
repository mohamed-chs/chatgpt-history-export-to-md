"""Represents a single message in a conversation. It's contained in a Node object.

object path : conversations.json -> conversation -> mapping -> mapping node -> message
"""

from __future__ import annotations

from typing import Any, ClassVar, Literal


class Message:
    """A single message in a conversation."""

    configuration: ClassVar[dict[str, Any]] = {}

    def __init__(self, message: dict[str, Any]) -> None:
        """Initialize Message object."""
        self.id: str = message.get("id", None)
        self.author: dict[str, Any] = message.get("author", None)
        self.create_time: float = message.get("create_time", None)
        self.update_time: float = message.get("update_time", None)
        self.content: dict[str, Any] = message.get("content", None)
        self.status: str = message.get("status", None)
        self.end_turn: bool = message.get("end_turn", None)
        self.weight: float = message.get("weight", None)
        self.metadata: dict[str, Any] = message.get("metadata", None)
        self.recipient: str = message.get("recipient", None)

    def author_role(self) -> Literal["user", "assistant", "system", "tool"]:
        """Return the role of the author of the message."""
        return self.author["role"]

    def author_header(self) -> str:
        """Get the title header of the message based on the configs."""
        author_config: dict[str, Any] = self.configuration.get("author_headers", {})
        match self.author_role():
            case "user":
                return author_config.get("user", "# User")
            case "assistant":
                return author_config.get("assistant", "# Assistant")
            case "system":
                return author_config.get("system", "### System")
            case "tool":
                return author_config.get("tool", "### Tool output")
            case _:
                return "### unknown-message-author"

    def content_text(self) -> str:
        """Get the text content of the message."""
        if "parts" in self.content:
            return str(object=self.content["parts"][0])
        if "text" in self.content:
            return f"```python\n{self.content['text']}\n```"
        return ""

    def content_type(self) -> str:
        """Get the content type of the message."""
        return self.content["content_type"]

    def model_slug(self) -> str:
        """Get the model used for the message."""
        return self.metadata.get("model_slug", "")
