"""ConversationSet class to model a set of conversations.

Can be the set of all conversations, or a set of conversations in a week, month, or year.

gonna be useful for updating the data in the future"""

from datetime import datetime
from time import ctime
from typing import Any, Dict, List

from .conversation import Conversation


class ConversationSet:
    """Stores a list of conversations."""

    configuration: Dict[str, Any] = {}

    def __init__(self, conversations: List[Dict[str, Any]]):
        conversation_set: List[Conversation] = [
            Conversation(**conversation) for conversation in conversations
        ]
        self.conversations = conversation_set

    def add_conversation(self, conversation: Conversation) -> None:
        """Add a conversation to the list."""
        self.conversations.append(conversation)

    def last_updated(self) -> float:
        """Returns the timestamp of the last updated conversation in the list."""
        return max(conversation.update_time for conversation in self.conversations)

    def grouped_by_week(self) -> Dict[datetime, "ConversationSet"]:
        """Get a dictionary of conversations in the list grouped by the start of the week."""
        grouped: Dict[datetime, "ConversationSet"] = {}
        for conversation in self.conversations:
            week_start = conversation.start_of_week()
            if week_start not in grouped:
                grouped[week_start] = ConversationSet([])
            grouped[week_start].add_conversation(conversation)
        return grouped

    def grouped_by_month(self) -> Dict[datetime, "ConversationSet"]:
        """Get a dictionary of conversations in the list grouped by the start of the month."""
        grouped: Dict[datetime, "ConversationSet"] = {}
        for conversation in self.conversations:
            month_start = conversation.start_of_month()
            if month_start not in grouped:
                grouped[month_start] = ConversationSet([])
            grouped[month_start].add_conversation(conversation)
        return grouped

    def grouped_by_year(self) -> Dict[datetime, "ConversationSet"]:
        """Get a dictionary of conversations in the list grouped by the start of the year."""
        grouped: Dict[datetime, "ConversationSet"] = {}
        for conversation in self.conversations:
            year_start = conversation.start_of_year()
            if year_start not in grouped:
                grouped[year_start] = ConversationSet([])
            grouped[year_start].add_conversation(conversation)
        return grouped

    def all_custom_instructions(self) -> List[Dict[str, Any]]:
        """Get a list of all custom instructions, in all conversations in the list."""
        custom_instructions: List[Dict[str, Any]] = []

        for conversation in self.conversations:
            if not conversation.custom_instructions():
                continue

            instructions_info = {
                "chat_title": conversation.title,
                "chat_link": conversation.chat_link(),
                "time": ctime(conversation.create_time),
                "custom_instructions": conversation.custom_instructions(),
            }

            custom_instructions.append(instructions_info)

        return custom_instructions

    def all_message_timestamps(self) -> List[float]:
        """Get a list of all message timestamps, in all conversations in the list."""
        timestamps: List[float] = []

        for conversation in self.conversations:
            timestamps.extend(conversation.message_timestamps())

        return timestamps

    def all_user_text(self) -> str:
        """Get a string of all user text, in all conversations in the list."""
        return "\n".join(
            conversation.entire_user_text() for conversation in self.conversations
        )

    def all_assistant_text(self) -> str:
        """Get a string of all assistant text, in all conversations in the list."""
        return "\n".join(
            conversation.entire_assistant_text() for conversation in self.conversations
        )
