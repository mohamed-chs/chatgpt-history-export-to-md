"""ConversationSet class to model a set of conversations.

Can be the set of all conversations, or a set of conversations in a week, month, or year.

gonna be useful for updating the data in the future

TODO: turn the conversations list into a dict, with the id as the key
"""

from datetime import datetime
from time import ctime
from typing import Any

from .conversation import Conversation


class ConversationSet:
    """Stores a set of conversations."""

    configuration: dict[str, Any] = {}

    def __init__(self, conversations: list[dict[str, Any]]) -> None:
        conversation_dict: dict[str, Conversation] = {
            conversation["conversation_id"]: Conversation(conversation=conversation)
            for conversation in conversations
        }

        self.conversation_dict: dict[str, Conversation] = conversation_dict

        self.conversation_list = list(self.conversation_dict.values())

    def add_conversation(self, conv: Conversation) -> None:
        """Add a conversation to the dictionary and list."""
        self.conversation_dict[conv.conversation_id] = conv
        self.conversation_list.append(conv)

    def last_updated(self) -> float:
        """Returns the timestamp of the last updated conversation in the list."""
        return max(conversation.update_time for conversation in self.conversation_list)

    def update(self, conv_set: "ConversationSet") -> None:
        """Update the conversation set with the new one."""
        if conv_set.last_updated() <= self.last_updated():
            return
        self.conversation_dict.update(conv_set.conversation_dict)
        self.conversation_list = list(self.conversation_dict.values())

    def grouped_by_week(self) -> dict[datetime, "ConversationSet"]:
        """Get a dictionary of conversations in the list grouped by the start of the week."""
        grouped: dict[datetime, "ConversationSet"] = {}
        for conversation in self.conversation_list:
            week_start: datetime = conversation.start_of_week()
            if week_start not in grouped:
                grouped[week_start] = ConversationSet(conversations=[])
            grouped[week_start].add_conversation(conv=conversation)
        return grouped

    def grouped_by_month(self) -> dict[datetime, "ConversationSet"]:
        """Get a dictionary of conversations in the list grouped by the start of the month."""
        grouped: dict[datetime, "ConversationSet"] = {}
        for conversation in self.conversation_list:
            month_start: datetime = conversation.start_of_month()
            if month_start not in grouped:
                grouped[month_start] = ConversationSet(conversations=[])
            grouped[month_start].add_conversation(conv=conversation)
        return grouped

    def grouped_by_year(self) -> dict[datetime, "ConversationSet"]:
        """Get a dictionary of conversations in the list grouped by the start of the year."""
        grouped: dict[datetime, "ConversationSet"] = {}
        for conversation in self.conversation_list:
            year_start: datetime = conversation.start_of_year()
            if year_start not in grouped:
                grouped[year_start] = ConversationSet(conversations=[])
            grouped[year_start].add_conversation(conv=conversation)
        return grouped

    def all_custom_instructions(self) -> list[dict[str, Any]]:
        """Get a list of all custom instructions, in all conversations in the set."""
        custom_instructions: list[dict[str, Any]] = []

        for conversation in self.conversation_list:
            if not conversation.custom_instructions():
                continue

            instructions_info: dict[str, str | dict[str, str]] = {
                "chat_title": conversation.title,
                "chat_link": conversation.chat_link(),
                "time": ctime(conversation.create_time),
                "custom_instructions": conversation.custom_instructions(),
            }

            custom_instructions.append(instructions_info)

        return custom_instructions

    def all_author_message_timestamps(self, author: str) -> list[float]:
        """Get a list of all message timestamps, in all conversations in the list."""
        timestamps: list[float] = []

        for conversation in self.conversation_list:
            timestamps.extend(conversation.author_message_timestamps(author=author))

        return timestamps

    def all_author_text(self, author: str) -> str:
        """Get a string of all text, in all conversations in the list."""
        return "\n".join(
            conversation.entire_author_text(author=author)
            for conversation in self.conversation_list
        )
