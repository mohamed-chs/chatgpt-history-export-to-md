"""Mocks for testing."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from convoviz.models import ConversationJSON, MessageJSON, NodeJSON

DATETIME_111 = datetime(
    year=2023,
    month=7,
    day=29,
    hour=8,
    minute=0,
    second=0,
    tzinfo=timezone.utc,
)

DATETIME_112: datetime = DATETIME_111 + timedelta(minutes=5)

SYSTEM_MESSAGE_111: MessageJSON = {
    "id": "system_node_111",
    "author": {"role": "system", "metadata": {}},
    "create_time": DATETIME_111.timestamp(),
    "update_time": DATETIME_111.timestamp(),
    "content": {"content_type": "text", "parts": ["system message 111"]},
    "status": "finished_successfully",
    "end_turn": True,
    "weight": 1.0,
    "metadata": {"model_slug": "gpt-4"},
    "recipient": "all",
}

USER_MESSAGE_TEXT_111 = "user message 111"

USER_MESSAGE_111: MessageJSON = {
    "id": "user_node_111",
    "author": {"role": "user", "metadata": {}},
    "create_time": DATETIME_111.timestamp(),
    "update_time": DATETIME_111.timestamp(),
    "content": {"content_type": "text", "parts": [USER_MESSAGE_TEXT_111]},
    "status": "finished_successfully",
    "end_turn": True,
    "weight": 1.0,
    "metadata": {"model_slug": "gpt-4"},
    "recipient": "all",
}

ASSISTANT_MESSAGE_TEXT_111 = "assistant message 111"

ASSISTANT_MESSAGE_111: MessageJSON = {
    "id": "assistant_node_111",
    "author": {"role": "assistant", "metadata": {}},
    "create_time": DATETIME_112.timestamp(),
    "update_time": DATETIME_112.timestamp(),
    "content": {"content_type": "text", "parts": [ASSISTANT_MESSAGE_TEXT_111]},
    "status": "finished_successfully",
    "end_turn": True,
    "weight": 1.0,
    "metadata": {"model_slug": "gpt-4"},
    "recipient": "all",
}


ROOT_NODE_111: NodeJSON = {
    "id": "root_node_111",
    "message": None,
    "parent": None,
    "children": ["system_node_111"],
}

SYSTEM_NODE_111: NodeJSON = {
    "id": "system_node_111",
    "message": SYSTEM_MESSAGE_111,
    "parent": None,
    "children": ["user_node_111"],
}

USER_NODE_111: NodeJSON = {
    "id": "user_node_111",
    "message": USER_MESSAGE_111,
    "parent": None,
    "children": ["assistant_node_111"],
}

ASSISTANT_NODE_111: NodeJSON = {
    "id": "assistant_node_111",
    "message": ASSISTANT_MESSAGE_111,
    "parent": None,
    "children": [],
}

MAPPING_111: dict[str, NodeJSON] = {
    "root_node_111": ROOT_NODE_111,
    "system_node_111": SYSTEM_NODE_111,
    "user_node_111": USER_NODE_111,
    "assistant_node_111": ASSISTANT_NODE_111,
}

TITLE_111 = "conversation 111"
CONVERSATION_ID_111 = "conversation_111"
TEMPLATE_ID_111 = "template_111"
PLUGIN_IDS_111: list[str] = []
MODERATION_RESULTS_111: list[Any] = []

CONVERSATION_111: ConversationJSON = {
    "title": TITLE_111,
    "create_time": DATETIME_111.timestamp(),
    "update_time": DATETIME_112.timestamp(),
    "mapping": MAPPING_111,
    "moderation_results": MODERATION_RESULTS_111,
    "current_node": ASSISTANT_NODE_111["id"],
    "plugin_ids": PLUGIN_IDS_111,
    "conversation_id": CONVERSATION_ID_111,
    "conversation_template_id": TEMPLATE_ID_111,
    "id": CONVERSATION_ID_111,
}

# based on the above
MESSAGE_COUNT_111 = 2
