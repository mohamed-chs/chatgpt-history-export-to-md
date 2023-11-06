"""Conversation model. Represents a single ChatGPT chat.

object path : conversations.json -> conversation (one of the list items)
"""

from __future__ import annotations

from datetime import datetime, timedelta
from os import utime as os_utime
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar, Unpack

from orjson import loads
from pydantic import BaseModel

from convoviz.data_analysis import generate_wordcloud
from convoviz.utils import (
    DEFAULT_CONVERSATION_CONFIGS,
    ConversationConfigs,
    WordCloudKwargs,
    close_code_blocks,
    replace_latex_delimiters,
    sanitize,
)

from ._node import Node

if TYPE_CHECKING:
    from PIL.Image import Image

    from ._message import AuthorRole


class Conversation(BaseModel):
    """Wrapper class for a `conversation` in _a_ `json` file."""

    __configs: ClassVar[ConversationConfigs] = DEFAULT_CONVERSATION_CONFIGS

    title: str
    create_time: datetime
    update_time: datetime
    mapping: dict[str, Node]
    moderation_results: list[Any]
    current_node: str
    plugin_ids: list[str] | None = None
    conversation_id: str
    conversation_template_id: str | None = None
    id: str | None = None  # noqa: A003

    @classmethod
    def update_configs(cls, configs: ConversationConfigs) -> None:
        """Set the configuration for all conversations."""
        cls.__configs.update(configs)

    @classmethod
    def from_json(cls, filepath: Path | str) -> Conversation:
        """Load the conversation from a JSON file."""
        filepath = Path(filepath)

        with filepath.open(encoding="utf-8") as file:
            return cls(**loads(file.read()))

    @property
    def node_mapping(self) -> dict[str, Node]:
        """Return a dictionary of connected Node objects, based on the mapping."""
        return Node.mapping(self.mapping)

    @property
    def _all_message_nodes(self) -> list[Node]:
        """List of all nodes that have a message, including all branches."""
        return [node for node in self.node_mapping.values() if node.message]

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
            if node.message and node.message.author.role in authors
        ]

    @property
    def leaf_count(self) -> int:
        """Return the number of leaves in the conversation."""
        return sum(1 for node in self._all_message_nodes if not node.children_nodes)

    @property
    def url(self) -> str:
        """Chat URL."""
        return f"https://chat.openai.com/c/{self.conversation_id}"

    @property
    def content_types(self) -> list[str]:
        """List of all content types in the conversation (all branches)."""
        return list(
            {
                node.message.content.content_type
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
    def model(self) -> str | None:
        """ChatGPT model used for the conversation."""
        assistant_nodes: list[Node] = self._author_nodes("assistant")
        if not assistant_nodes:
            return None

        message = assistant_nodes[0].message

        return message.metadata.model_slug if message else None

    @property
    def plugins(self) -> list[str]:
        """List of all ChatGPT plugins used in the conversation."""
        return list(
            {
                node.message.metadata.invoked_plugin["namespace"]
                for node in self._author_nodes("tool")
                if node.message and node.message.metadata.invoked_plugin
            },
        )

    @property
    def custom_instructions(self) -> dict[str, str]:
        """Return custom instructions used for the conversation."""
        system_nodes = self._author_nodes("system")
        if len(system_nodes) < 2:
            return {}

        context_message = system_nodes[1].message
        if context_message and context_message.metadata.is_user_system_message:
            return context_message.metadata.user_context_message_data or {}

        return {}

        # TODO: check if this is the same for conversations from the bookmarklet

    @property
    def yaml(self) -> str:
        """YAML metadata header for the conversation."""
        yaml_config = self.__configs["yaml"]

        yaml_map = {
            "title": self.title,
            "chat_link": self.url,
            "create_time": self.create_time,
            "update_time": self.update_time,
            "model": self.model,
            "used_plugins": self.plugins,
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
                content = close_code_blocks(node.message.text)
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

        os_utime(filepath, (self.update_time.timestamp(), self.update_time.timestamp()))

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
            node.message.create_time.timestamp()
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
            node.message.text for node in self._author_nodes(*authors) if node.message
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
        start_of_week = self.create_time - timedelta(
            days=self.create_time.weekday(),
        )

        return start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)

    @property
    def month_start(self) -> datetime:
        """Return the first of the month the conversation was created in."""
        return self.create_time.replace(
            day=1,
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )

    @property
    def year_start(self) -> datetime:
        """Return the first of January of the year the conversation was created in."""
        return self.create_time.replace(
            month=1,
            day=1,
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )
