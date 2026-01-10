"""ConversationCollection model - manages a set of conversations.

This is a pure data model - I/O and visualization logic are in separate modules.
"""

from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from convoviz.models.conversation import Conversation
from convoviz.models.message import AuthorRole


class ConversationCollection(BaseModel):
    """A collection of ChatGPT conversations.

    Provides grouping and aggregation operations over conversations.
    """

    conversations: list[Conversation] = Field(default_factory=list)
    source_path: Path | None = None

    @property
    def index(self) -> dict[str, Conversation]:
        """Get conversations indexed by conversation_id."""
        return {conv.conversation_id: conv for conv in self.conversations}

    @property
    def last_updated(self) -> datetime:
        """Get the most recent update time across all conversations."""
        if not self.conversations:
            return datetime.min
        return max(conv.update_time for conv in self.conversations)

    def update(self, other: "ConversationCollection") -> None:
        """Merge another collection into this one.

        Merges per-conversation, keeping the newest version when IDs collide.

        Note: We intentionally do *not* gate on ``other.last_updated`` because
        "new" conversations can still have older timestamps than the most recent
        conversation in this collection (e.g. bookmarklet downloads).
        """
        merged: dict[str, Conversation] = dict(self.index)

        for conv_id, incoming in other.index.items():
            existing = merged.get(conv_id)
            if existing is None or incoming.update_time > existing.update_time:
                merged[conv_id] = incoming

        self.conversations = list(merged.values())

    def add(self, conversation: Conversation) -> None:
        """Add a conversation to the collection."""
        self.conversations.append(conversation)

    @property
    def custom_instructions(self) -> list[dict[str, Any]]:
        """Get all custom instructions from all conversations."""
        instructions: list[dict[str, Any]] = []
        for conv in self.conversations:
            if not conv.custom_instructions:
                continue
            instructions.append(
                {
                    "chat_title": conv.title,
                    "chat_link": conv.url,
                    "time": conv.create_time,
                    "custom_instructions": conv.custom_instructions,
                }
            )
        return instructions

    def timestamps(self, *authors: AuthorRole) -> list[float]:
        """Get all message timestamps from specified authors."""
        result: list[float] = []
        for conv in self.conversations:
            result.extend(conv.timestamps(*authors))
        return result

    def plaintext(self, *authors: AuthorRole) -> str:
        """Get concatenated plain text from all conversations."""
        return "\n".join(conv.plaintext(*authors) for conv in self.conversations)

    def group_by_week(self) -> dict[datetime, "ConversationCollection"]:
        """Group conversations by the week they were created."""
        groups: dict[datetime, ConversationCollection] = {}
        for conv in self.conversations:
            week_start = conv.week_start
            if week_start not in groups:
                groups[week_start] = ConversationCollection()
            groups[week_start].add(conv)
        return groups

    def group_by_month(self) -> dict[datetime, "ConversationCollection"]:
        """Group conversations by the month they were created."""
        groups: dict[datetime, ConversationCollection] = {}
        for conv in self.conversations:
            month_start = conv.month_start
            if month_start not in groups:
                groups[month_start] = ConversationCollection()
            groups[month_start].add(conv)
        return groups

    def group_by_year(self) -> dict[datetime, "ConversationCollection"]:
        """Group conversations by the year they were created."""
        groups: dict[datetime, ConversationCollection] = {}
        for conv in self.conversations:
            year_start = conv.year_start
            if year_start not in groups:
                groups[year_start] = ConversationCollection()
            groups[year_start].add(conv)
        return groups
