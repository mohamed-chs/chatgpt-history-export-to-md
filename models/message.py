"""Represents a single message in a conversation. It's contained in a Node object.
(it could be written in node.py, but I think it's better to separate them)

object path : conversations.json -> conversation -> mapping -> mapping node -> message
"""

from typing import Any, Dict, Optional


class Message:
    """A single message in a conversation."""

    def __init__(
        self,
        id: str,
        author: Dict[str, Any],
        create_time: Optional[float],
        update_time: Optional[float],
        content: Dict[str, Any],
        status: str,
        end_turn: Optional[bool],
        weight: float,
        metadata: Dict[str, Any],
        recipient: str,
        configuration: Optional[Dict[str, Any]] = None,
    ):
        self.id = id
        self.author = author
        self.create_time = create_time
        self.update_time = update_time
        self.content = content
        self.status = status
        self.end_turn = end_turn
        self.weight = weight
        self.metadata = metadata
        self.recipient = recipient
        self.configuration = configuration if configuration else {}

    @property
    def author_role(self) -> str:
        """The role of the author of the message.

        'user', 'assistant', 'system' or 'tool'."""
        return self.author["role"]

    @property
    def author_header(self) -> str:
        """Get the title header of the message based on the configs."""
        author_config: Dict[str, Any] = self.configuration.get("author_headers", {})
        if self.author_role == "system":
            return author_config.get("system", "### System")
        return author_config.get(self.author_role, f"# {self.author_role.title()}")

    @property
    def content_text(self) -> str:
        """get the text content of the message."""
        if "parts" in self.content:
            return self.content["parts"][0]
        elif "text" in self.content:
            return f"```python\n{self.content['text']}\n```"
        else:
            return ""

    @property
    def content_type(self) -> str:
        """get the content type of the message."""
        return self.content["content_type"]

    @property
    def model_slug(self) -> Optional[str]:
        """get the model used for the message."""
        return self.metadata.get("model_slug", None)
