"""Conversation model. Represents a single ChatGPT chat.

object path : conversations.json -> conversation (one of the list items)
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from re import Pattern
from re import compile as re_compile
from time import ctime
from typing import TYPE_CHECKING, Any, ClassVar, Literal

from utils.utils import ensure_closed_code_blocks, replace_latex_delimiters

from .node import Node

if TYPE_CHECKING:
    from .message import Message


class Conversation:
    """Stores the conversation object from the conversations.json file."""

    configuration: ClassVar[dict[str, Any]] = {}

    def __init__(self, conversation: dict[str, Any]) -> None:
        """Initialize Conversation object."""
        self.title: str = conversation.get("title", None)
        self.create_time: float = conversation.get("create_time", None)
        self.update_time: float = conversation.get("update_time", None)
        self.mapping: dict[str, Node] = Node.nodes_from_mapping(
            mapping=conversation.get("mapping", None),
        )
        self.moderation_results: list[Any] = conversation.get(
            "moderation_results",
            None,
        )
        self.current_node: Node = self.mapping[conversation.get("current_node", None)]
        self.plugin_ids: list[str] = conversation.get("plugin_ids", None)
        self.conversation_id: str = conversation.get("conversation_id", None)
        self.conversation_template_id: str = conversation.get(
            "conversation_template_id",
            None,
        )
        self.id: str = conversation.get("id", None)

    def _main_branch_nodes(self) -> list[Node]:
        """List of all nodes that have a message in the current 'main' branch.

        the 'current_node' represents the last node in the main branch.
        """
        nodes: list[Node] = []
        curr_node: Node = self.current_node
        curr_parent: Node | None = curr_node.parent

        while curr_parent:
            if curr_node.message:
                nodes.append(curr_node)
            curr_node = curr_parent
            curr_parent = curr_node.parent

        nodes.reverse()

        return nodes

    def _all_message_nodes(self) -> list[Node]:
        """List of all nodes that have a message, including all branches."""
        return [node for node in self.mapping.values() if node.message]

    def _author_nodes(
        self,
        author: Literal["user", "assistant", "system", "tool"],
    ) -> list[Node]:
        """List of all nodes with the given author role (all branches)."""
        return [
            node
            for node in self._all_message_nodes()
            if node.message and node.message.author_role() == author
        ]

    def _branch_indicator(self, node: Node) -> str:
        """Get the branch indicator for the given node.

        (yet to be implemented ...)
        """
        if node in self._main_branch_nodes():
            return "(main branch ⎇)"
        return "(other branch ⎇)"

    def leaf_count(self) -> int:
        """Return the number of leaves in the conversation."""
        return sum(1 for node in self._all_message_nodes() if not node.children)

    def has_multiple_branches(self) -> bool:
        """Check if the conversation has multiple branches."""
        return self.leaf_count() > 1

    def chat_link(self) -> str:
        """Chat URL."""
        return f"https://chat.openai.com/c/{self.conversation_id}"

    def content_types(self) -> list[str]:
        """List of all content types in the conversation (all branches)."""
        return list(
            {
                node.message.content_type()
                for node in self._all_message_nodes()
                if node.message
            },
        )

    def message_count(self) -> int:
        """Return the number of 'user' and 'assistant' messages (all branches)."""
        return sum(
            1
            for node in self._all_message_nodes()
            if node.message and node.message.author_role() in ("user", "assistant")
        )

    def entire_author_text(
        self,
        author: Literal["user", "assistant", "system", "tool"],
    ) -> str:
        """Entire raw text from the given author role (all branches).

        Useful for generating word clouds.
        """
        return "\n".join(
            node.message.content_text()
            for node in self._author_nodes(author=author)
            if node.message
        )

    def author_message_timestamps(
        self,
        author: Literal["user", "assistant", "system", "tool"],
    ) -> list[float]:
        """List of all message timestamps from the given author role (all branches).

        Useful for generating time graphs.
        """
        return [
            node.message.create_time
            for node in self._author_nodes(author=author)
            if node.message
        ]

    def model_slug(self) -> str:
        """ChatGPT model used for the conversation."""
        assistant_nodes: list[Node] = self._author_nodes(author="assistant")
        if not assistant_nodes:
            return ""

        message: Message | None = assistant_nodes[0].message
        if not message:
            return ""

        return message.model_slug()

    def used_plugins(self) -> list[str]:
        """List of all ChatGPT plugins used in the conversation."""
        return list(
            {
                node.message.metadata["invoked_plugin"]["namespace"]
                for node in self._author_nodes(author="tool")
                if node.message and node.message.metadata.get("invoked_plugin")
            },
        )

    def custom_instructions(self) -> dict[str, str]:
        """Return custom instructions used for the conversation."""
        system_nodes: list[Node] = self._author_nodes(author="system")
        if len(system_nodes) < 2:
            return {}
        context_message: Message | None = system_nodes[1].message
        if context_message and context_message.metadata.get(
            "is_user_system_message",
            None,
        ):
            return context_message.metadata.get("user_context_message_data", {})
        return {}

        # TODO: check if this is the same for conversations from the bookmarklet

    def yaml_header(self) -> str:
        """YAML metadata header for the conversation."""
        yaml_config = self.configuration.get("yaml", {})

        yaml_map: dict[str, Any] = {
            "title": self.title,
            "chat_link": self.chat_link(),
            "create_time": ctime(self.create_time),
            "update_time": ctime(self.update_time),
            "model": self.model_slug(),
            "used_plugins": self.used_plugins(),
            "message_count": self.message_count(),
            "content_types": self.content_types(),
            "custom_instructions": self.custom_instructions(),
        }

        yaml = "---\n"

        for key, value in yaml_map.items():
            if yaml_config.get(key, True):
                yaml += f"{key}: {value}\n"

        yaml += "---\n"

        return yaml

    def markdown_text(self) -> str:
        """Return the full markdown text content of the conversation."""
        markdown_config = self.configuration.get("markdown", {})
        latex_delimiters = markdown_config.get("latex_delimiters", "default")

        markdown: str = self.yaml_header()

        for node in self._all_message_nodes():
            if node.message:
                content: str = ensure_closed_code_blocks(
                    string=node.message.content_text(),
                )
                # prevent empty messages from taking up white space
                content = f"\n{content}\n" if content else ""
                if latex_delimiters == "dollar sign":
                    content = replace_latex_delimiters(string=content)
                markdown += f"\n{node.header()}{content}{node.footer()}\n---\n"
        return markdown

    def sanitized_title(self) -> str:
        """Sanitized title of the conversation, compatible with file names."""
        file_anti_pattern: Pattern[str] = re_compile(
            pattern=r'[<>:"/\\|?*\n\r\t\f\v]',
        )
        return (
            file_anti_pattern.sub(repl="_", string=self.title)
            if self.title
            else "untitled"
        )

    def stats(self) -> dict[str, Any]:
        """Get diverse insightful stats on the conversation."""
        return {}

    def start_of_year(self) -> datetime:
        """Return the first of January of the year the conversation was created in."""
        return datetime(
            year=datetime.fromtimestamp(self.create_time, tz=timezone.utc).year,
            month=1,
            day=1,
            tzinfo=timezone.utc,
        )

    def start_of_month(self) -> datetime:
        """Return the first of the month the conversation was created in."""
        return datetime(
            year=datetime.fromtimestamp(self.create_time, tz=timezone.utc).year,
            month=datetime.fromtimestamp(self.create_time, tz=timezone.utc).month,
            day=1,
            tzinfo=timezone.utc,
        )

    def start_of_week(self) -> datetime:
        """Return the monday of the week the conversation was created in."""
        start_of_week: datetime = datetime.fromtimestamp(
            self.create_time,
            tz=timezone.utc,
        ) - timedelta(
            days=datetime.fromtimestamp(self.create_time, tz=timezone.utc).weekday(),
        )
        return start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
