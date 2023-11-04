"""Conversation model. Represents a single ChatGPT chat.

object path : conversations.json -> conversation (one of the list items)
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from json import load as json_load
from os import utime as os_utime
from pathlib import Path
from time import ctime
from typing import TYPE_CHECKING, TypedDict

from convoviz.data_analysis import generate_wordcloud
from convoviz.utils import (
    DEFAULT_CONVERSATION_CONFIGS,
    close_code_blocks,
    replace_latex_delimiters,
    sanitize,
)

from ._node import Node

if TYPE_CHECKING:
    from typing import Any

    from PIL.Image import Image
    from typing_extensions import Self, Unpack

    from convoviz.utils import ConversationConfigs, WordCloudKwargs

    from ._message import AuthorRole
    from ._node import NodeJSON


class ConversationJSON(TypedDict):
    """Type of a `conversation` in _a_ `json` file."""

    title: str
    create_time: float
    update_time: float
    mapping: dict[str, NodeJSON]
    moderation_results: list[Any]  # I'm yet to see this field populated :(
    current_node: str
    plugin_ids: list[str]
    conversation_id: str
    conversation_template_id: str
    id: str


class Conversation:
    """Wrapper class for a `conversation` in _a_ `json` file.

    see `ConversationJSON` for more details
    """

    __configs = DEFAULT_CONVERSATION_CONFIGS

    def __init__(self, conversation: ConversationJSON) -> None:
        """Initialize Conversation object."""
        self.__data = conversation

    @classmethod
    def update_configs(cls, configs: ConversationConfigs) -> None:
        """Set the configuration for all conversations."""
        cls.__configs.update(configs)

    @classmethod
    def from_json(cls, filepath: Path | str) -> Self:
        """Load the conversation from a JSON file."""
        filepath = Path(filepath)

        with filepath.open(encoding="utf-8") as file:
            return cls(json_load(file))

    @property
    def title(self) -> str:
        """Get the title of the conversation."""
        return self.__data["title"]

    @property
    def create_time(self) -> float:
        """Get the creation time of the conversation."""
        return self.__data["create_time"]

    @property
    def create_datetime(self) -> datetime:
        """Get the creation datetime of the conversation."""
        return datetime.fromtimestamp(self.create_time, timezone.utc)

    @property
    def update_time(self) -> float:
        """Get the update time of the conversation."""
        return self.__data["update_time"]

    @property
    def update_datetime(self) -> datetime:
        """Get the update datetime of the conversation."""
        return datetime.fromtimestamp(self.update_time, timezone.utc)

    @property
    def mapping(self) -> dict[str, Node]:
        """Get the mapping of the conversation."""
        return Node.mapping(self.__data["mapping"])

    @property
    def moderation_results(self) -> list[Any]:
        """Get the moderation results of the conversation."""
        return self.__data["moderation_results"]

    @property
    def current_node(self) -> Node:
        """Get the current node of the conversation."""
        return self.mapping[self.__data["current_node"]]

    @property
    def plugin_ids(self) -> list[str]:
        """Get the plugin ids of the conversation."""
        return self.__data["plugin_ids"]

    @property
    def conversation_id(self) -> str:
        """Get the conversation id of the conversation."""
        return self.__data["conversation_id"]

    @property
    def conversation_template_id(self) -> str:
        """Get the conversation template id of the conversation."""
        return self.__data["conversation_template_id"]

    @property
    def _all_message_nodes(self) -> list[Node]:
        """List of all nodes that have a message, including all branches."""
        return [node for node in self.mapping.values() if node.message]

    def _author_nodes(
        self,
        *authors: AuthorRole,
    ) -> list[Node]:
        """List of all nodes with the given author role (all branches)."""
        if len(authors) == 0:
            authors = ("user",)
        return [
            node
            for node in self._all_message_nodes
            if node.message and node.message.author_role in authors
        ]

    @property
    def leaf_count(self) -> int:
        """Return the number of leaves in the conversation."""
        return sum(1 for node in self._all_message_nodes if not node.children)

    @property
    def chat_link(self) -> str:
        """Chat URL."""
        return f"https://chat.openai.com/c/{self.conversation_id}"

    @property
    def content_types(self) -> list[str]:
        """List of all content types in the conversation (all branches)."""
        return list(
            {
                node.message.content_type
                for node in self._all_message_nodes
                if node.message
            },
        )

    def message_count(
        self,
        *authors: AuthorRole,
    ) -> int:
        """Return the number of 'user' and 'assistant' messages (all branches)."""
        if len(authors) == 0:
            authors = ("user",)
        return len(self._author_nodes(*authors))

    @property
    def model_slug(self) -> str | None:
        """ChatGPT model used for the conversation."""
        assistant_nodes: list[Node] = self._author_nodes("assistant")
        if not assistant_nodes:
            return None

        message = assistant_nodes[0].message

        return message.model_slug if message else None

    @property
    def used_plugins(self) -> list[str]:
        """List of all ChatGPT plugins used in the conversation."""
        return list(
            {
                node.message.metadata["invoked_plugin"]["namespace"]
                for node in self._author_nodes("tool")
                if node.message and "invoked_plugin" in node.message.metadata
            },
        )

    @property
    def custom_instructions(self) -> dict[str, str] | None:
        """Return custom instructions used for the conversation."""
        system_nodes = self._author_nodes("system")
        if len(system_nodes) < 2:
            return None

        context_message = system_nodes[1].message
        if context_message and context_message.metadata.get("is_user_system_message"):
            return context_message.metadata.get("user_context_message_data")

        return None

        # TODO: check if this is the same for conversations from the bookmarklet

    @property
    def yaml(self) -> str:
        """YAML metadata header for the conversation."""
        yaml_config = self.__configs["yaml"]

        yaml_map = {
            "title": self.title,
            "chat_link": self.chat_link,
            "create_time": ctime(self.create_time),
            "update_time": ctime(self.update_time),
            "model": self.model_slug,
            "used_plugins": self.used_plugins,
            "message_count": self.message_count("user", "assistant"),
            "content_types": self.content_types,
            "custom_instructions": self.custom_instructions,
        }

        yaml = ""

        for key, value in yaml_map.items():
            if yaml_config.get(key, True):
                yaml += f"{key}: {value}\n"

        if not yaml:
            return ""

        return f"---\n{yaml}---\n"

    @property
    def markdown(self) -> str:
        """Return the full markdown text content of the conversation."""
        markdown_config = self.__configs["markdown"]
        latex_delimiters = markdown_config["latex_delimiters"]

        markdown = self.yaml

        for node in self._all_message_nodes:
            if node.message:
                content = close_code_blocks(node.message.content_text)
                # prevent empty messages from taking up white space
                content = f"\n{content}\n" if content else ""
                if latex_delimiters == "dollars":
                    content = replace_latex_delimiters(content)
                markdown += f"\n{node.header}{content}{node.footer}\n---\n"

        return markdown

    def save(self, filepath: Path | str) -> None:
        """Save the conversation to the file, with added modification time."""
        filepath = Path(filepath)
        base_file_name = sanitize(filepath.stem)

        counter = 0
        while filepath.exists():
            counter += 1
            filepath = filepath.with_name(
                f"{base_file_name} ({counter}){filepath.suffix}",
            )

        with filepath.open("w", encoding="utf-8") as file:
            file.write(self.markdown)

        os_utime(filepath, (self.update_time, self.update_time))

    def timestamps(
        self,
        *authors: AuthorRole,
    ) -> list[float]:
        """List of all message timestamps from the given author role (all branches).

        Useful for generating time graphs.
        """
        if len(authors) == 0:
            authors = ("user",)
        return [
            node.message.create_time
            for node in self._author_nodes(*authors)
            if node.message and node.message.create_time
        ]

    def plaintext(
        self,
        *authors: AuthorRole,
    ) -> str:
        """Entire plain text from the given author role (all branches).

        Useful for generating word clouds.
        """
        if len(authors) == 0:
            authors = ("user",)
        return "\n".join(
            node.message.content_text
            for node in self._author_nodes(*authors)
            if node.message
        )

    def wordcloud(
        self,
        *authors: AuthorRole,
        **kwargs: Unpack[WordCloudKwargs],
    ) -> Image:
        """Generate a wordcloud from the conversation."""
        if len(authors) == 0:
            authors = ("user",)
        text = self.plaintext(*authors)
        return generate_wordcloud(text, **kwargs)

    @property
    def week_start(self) -> datetime:
        """Return the monday of the week the conversation was created in."""
        start_of_week = self.create_datetime - timedelta(
            days=self.create_datetime.weekday(),
        )

        return start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)

    @property
    def month_start(self) -> datetime:
        """Return the first of the month the conversation was created in."""
        return datetime(
            self.create_datetime.year,
            self.create_datetime.month,
            1,
            tzinfo=timezone.utc,
        )

    @property
    def year_start(self) -> datetime:
        """Return the first of January of the year the conversation was created in."""
        return datetime(self.create_datetime.year, 1, 1, tzinfo=timezone.utc)
