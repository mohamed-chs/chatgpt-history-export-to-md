"""ConversationList class to model the entire list of conversations.

gonna be useful for updating the data in the future"""

from typing import Any, Dict, List

from .conversation import Conversation


class ConversationList:
    """Stores a list of conversations."""

    def __init__(self, conversations: List[Dict[str, Any]]):
        conversation_list: List[Conversation] = [
            Conversation(**conversation) for conversation in conversations
        ]
        self.conversations = conversation_list

    @property
    def last_updated(self) -> float:
        """Returns the last updated timestamp."""
        return max(conversation.update_time for conversation in self.conversations)
