"""Represents a single message in a conversation. It's contained in a Node object.

object path : conversations.json -> conversation -> mapping -> mapping node -> message
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal, TypedDict

from convoviz.utils import DEFAULT_MESSAGE_CONFIGS, code_block

if TYPE_CHECKING:
    from typing import Any

    from typing_extensions import NotRequired

    from convoviz.utils import MessageConfigs


AuthorRole = Literal["user", "assistant", "system", "tool"]


class AuthorJSON(TypedDict):
    """Type of the `author` field in a `message`."""

    role: AuthorRole
    name: NotRequired[str | None]
    metadata: dict[str, Any]


class ContentJSON(TypedDict):
    """Type of the `content` field in a `message`."""

    content_type: str
    parts: NotRequired[list[str]]
    text: NotRequired[str]
    result: NotRequired[str]


class MetadataJSON(TypedDict):
    """Type of the `metadata` field in a `message`."""

    model_slug: NotRequired[str]
    invoked_plugin: NotRequired[dict[str, Any]]
    user_context_message_data: NotRequired[dict[str, Any]]


class MessageJSON(TypedDict):
    """Type of the `message` field in a `node`."""

    id: str
    author: AuthorJSON
    create_time: NotRequired[float | None]
    update_time: NotRequired[float | None]
    content: ContentJSON
    status: str
    end_turn: NotRequired[bool]
    weight: float
    metadata: MetadataJSON
    recipient: str


class Message:
    """Wrapper class for the `message` field in a `node`.

    see `MessageJSON` and `models.Node` for more details
    """

    __configs = DEFAULT_MESSAGE_CONFIGS

    def __init__(self, message: MessageJSON) -> None:
        """Initialize Message object."""
        self.__data = message

    @classmethod
    def update_configs(cls, configs: MessageConfigs) -> None:
        """Set the configuration for all messages."""
        cls.__configs.update(configs)

    @property
    def m_id(self) -> str:
        """Get the id of the message."""
        return self.__data["id"]

    @property
    def author(self) -> AuthorJSON:
        """Get the author of the message."""
        return self.__data["author"]

    @property
    def create_time(self) -> float | None:
        """Get the creation time of the message."""
        return self.__data.get("create_time")

    @property
    def update_time(self) -> float | None:
        """Get the update time of the message."""
        return self.__data.get("update_time")

    @property
    def content(self) -> ContentJSON:
        """Get the content of the message."""
        return self.__data["content"]

    @property
    def status(self) -> str:
        """Get the status of the message."""
        return self.__data["status"]

    @property
    def end_turn(self) -> bool | None:
        """Get the end_turn of the message."""
        return self.__data.get("end_turn")

    @property
    def weight(self) -> float:
        """Get the weight of the message."""
        return self.__data["weight"]

    @property
    def metadata(self) -> MetadataJSON:
        """Get the metadata of the message."""
        return self.__data["metadata"]

    @property
    def recipient(self) -> str:
        """Get the recipient of the message."""
        return self.__data["recipient"]

    @property
    def author_role(self) -> AuthorRole:
        """Return the role of the author of the message."""
        return self.author["role"]

    @property
    def author_header(self) -> str:
        """Get the title header of the message based on the configs."""
        return self.__configs["author_headers"][self.author_role]

    @property
    def content_text(self) -> str:
        """Get the text content of the message."""
        if "parts" in self.content:
            return str(self.content["parts"][0])
        if "text" in self.content:
            return code_block(self.content["text"])
        if "result" in self.content:
            return self.content["result"]

        # this error caught a very hidden bug in the data
        # I need more of these
        err_msg = f"No valid content found in message {self.m_id}"
        raise ValueError(err_msg)

    @property
    def content_type(self) -> str:
        """Get the content type of the message."""
        return self.content["content_type"]

    @property
    def model_slug(self) -> str | None:
        """Get the model used for the message."""
        return self.metadata.get("model_slug")
