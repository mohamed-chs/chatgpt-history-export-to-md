"""ConversationList class to model the entire list of conversations.

gonna be useful for updating the data in the future"""

from collections import defaultdict
from datetime import datetime
from time import ctime
from typing import Any, Dict, List

from .conversation import Conversation


class ConversationList:
    """Stores a list of conversations."""

    def __init__(self, conversations: List[Dict[str, Any]]):
        conversation_list: List[Conversation] = [
            Conversation(**conversation) for conversation in conversations
        ]
        self.conversations = conversation_list
        self.configuration: Dict[str, Any] = {}

    @property
    def last_updated(self) -> float:
        """Returns the last updated timestamp."""
        return max(conversation.update_time for conversation in self.conversations)

    @property
    def grouped_by_week(self) -> Dict[datetime, List[Conversation]]:
        """Get a dictionary of conversations grouped by the start of the week."""
        grouped: defaultdict[datetime, List[Conversation]] = defaultdict(list)
        for conversation in self.conversations:
            grouped[conversation.start_of_week].append(conversation)
        return dict(grouped)

    @property
    def grouped_by_month(self) -> Dict[datetime, List[Conversation]]:
        """Get a dictionary of conversations grouped by the start of the month."""
        grouped: defaultdict[datetime, List[Conversation]] = defaultdict(list)
        for conversation in self.conversations:
            grouped[conversation.start_of_month].append(conversation)
        return dict(grouped)

    @property
    def grouped_by_year(self) -> Dict[datetime, List[Conversation]]:
        """Get a dictionary of conversations grouped by the start of the year."""
        grouped: defaultdict[datetime, List[Conversation]] = defaultdict(list)
        for conversation in self.conversations:
            grouped[conversation.start_of_year].append(conversation)
        return dict(grouped)

    @property
    def all_custom_instructions(self) -> List[Dict[str, Any]]:
        """Get a list of all custom instructions."""
        custom_instructions: List[Dict[str, Any]] = []

        for conversation in self.conversations:
            if not conversation.custom_instructions:
                continue

            instructions_info = {
                "chat_title": conversation.title,
                "chat_link": conversation.chat_link,
                "time": ctime(conversation.create_time),
                "custom_instructions": conversation.custom_instructions,
            }

            custom_instructions.append(instructions_info)

        return custom_instructions
