"""Conversation model - pure data class.

Object path: conversations.json -> conversation (one of the list items)
"""

from datetime import datetime, timedelta
from typing import Any

from pydantic import BaseModel, Field

from convoviz.models.message import AuthorRole
from convoviz.models.node import Node, build_node_tree


class Conversation(BaseModel):
    """A single ChatGPT conversation.

    This is a pure data model - rendering and I/O logic are in separate modules.
    """

    title: str
    create_time: datetime
    update_time: datetime
    mapping: dict[str, Node]
    moderation_results: list[Any] = Field(default_factory=list)
    current_node: str
    plugin_ids: list[str] | None = None
    conversation_id: str
    conversation_template_id: str | None = None
    id: str | None = None

    @property
    def node_mapping(self) -> dict[str, Node]:
        """Get the connected node tree."""
        return build_node_tree(self.mapping)

    @property
    def all_message_nodes(self) -> list[Node]:
        """Get all nodes that have messages (including hidden/internal ones)."""
        return [node for node in self.node_mapping.values() if node.has_message]

    @property
    def visible_message_nodes(self) -> list[Node]:
        """Get all nodes that have *visible* (non-hidden) messages."""
        return [
            node
            for node in self.node_mapping.values()
            if node.has_message and node.message is not None and not node.message.is_hidden
        ]

    def nodes_by_author(self, *authors: AuthorRole, include_hidden: bool = False) -> list[Node]:
        """Get nodes with messages from specified authors.

        Args:
            *authors: Author roles to filter by. Defaults to ("user",) if empty.
            include_hidden: Whether to include hidden/internal messages.
        """
        if not authors:
            authors = ("user",)
        nodes = self.all_message_nodes if include_hidden else self.visible_message_nodes
        return [node for node in nodes if node.message and node.message.author.role in authors]

    @property
    def leaf_count(self) -> int:
        """Count the number of leaf nodes (conversation endpoints)."""
        return sum(1 for node in self.all_message_nodes if node.is_leaf)

    @property
    def url(self) -> str:
        """Get the ChatGPT URL for this conversation."""
        return f"https://chat.openai.com/c/{self.conversation_id}"

    @property
    def content_types(self) -> list[str]:
        """Get all unique content types in the conversation (excluding hidden messages)."""
        return list(
            {
                node.message.content.content_type
                for node in self.visible_message_nodes
                if node.message
            }
        )

    def message_count(self, *authors: AuthorRole) -> int:
        """Count messages from specified authors."""
        return len(self.nodes_by_author(*authors))

    @property
    def model(self) -> str | None:
        """Get the ChatGPT model used for this conversation."""
        assistant_nodes = self.nodes_by_author("assistant")
        if not assistant_nodes:
            return None
        message = assistant_nodes[0].message
        return message.metadata.model_slug if message else None

    @property
    def plugins(self) -> list[str]:
        """Get all plugins used in this conversation."""
        return list(
            {
                node.message.metadata.invoked_plugin["namespace"]
                for node in self.nodes_by_author("tool")
                if node.message and node.message.metadata.invoked_plugin
            }
        )

    @property
    def custom_instructions(self) -> dict[str, str]:
        """Get custom instructions used for this conversation."""
        system_nodes = self.nodes_by_author("system")
        for node in system_nodes:
            context_message = node.message
            if context_message and context_message.metadata.is_user_system_message:
                return context_message.metadata.user_context_message_data or {}
        return {}

    def timestamps(self, *authors: AuthorRole) -> list[float]:
        """Get message timestamps from specified authors.

        Useful for generating time-based visualizations.
        """
        if not authors:
            authors = ("user",)
        return [
            node.message.create_time.timestamp()
            for node in self.nodes_by_author(*authors)
            if node.message and node.message.create_time
        ]

    def plaintext(self, *authors: AuthorRole) -> str:
        """Get concatenated plain text from specified authors.

        Useful for word cloud generation.
        """
        if not authors:
            authors = ("user",)
        return "\n".join(
            node.message.text
            for node in self.nodes_by_author(*authors)
            if node.message and node.message.has_content
        )

    @property
    def week_start(self) -> datetime:
        """Get the Monday of the week this conversation was created."""
        start_of_week = self.create_time - timedelta(days=self.create_time.weekday())
        return start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)

    @property
    def month_start(self) -> datetime:
        """Get the first day of the month this conversation was created."""
        return self.create_time.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    @property
    def year_start(self) -> datetime:
        """Get January 1st of the year this conversation was created."""
        return self.create_time.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
