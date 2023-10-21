"""Mocks for testing."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

DATETIME_1: datetime = datetime(
    year=2023,
    month=7,
    day=29,
    hour=8,
    minute=0,
    second=0,
    tzinfo=timezone.utc,
)

DATETIME_2: datetime = DATETIME_1 + timedelta(minutes=5)


MESSAGE_1: dict[str, Any] = {
    "id": "sample_id",
    "author": {"role": "user"},
    "create_time": DATETIME_1.timestamp(),
    "update_time": DATETIME_1.timestamp(),
    "content": {"content_type": "text", "parts": ["Hello World"]},
    "status": "finished_successfully",
    "end_turn": True,
    "weight": 1.0,
    "metadata": {"model_slug": "gpt-4"},
    "recipient": "all",
}


CONVERSATION_1: dict[str, Any] = {
    "title": "Sample Conversation",
    "create_time": DATETIME_1.timestamp(),
    "update_time": DATETIME_2.timestamp(),
    "mapping": {
        "node1": {
            "message": {
                "id": "msg1",
                "author": {"role": "user"},
                "create_time": DATETIME_1.timestamp(),
                "update_time": DATETIME_1.timestamp(),
                "content": {"content_type": "text", "parts": ["Hello!"]},
                "metadata": {"model_slug": "gpt-4"},
            },
            "children": ["node2"],
        },
        "node2": {
            "message": {
                "id": "msg2",
                "author": {"role": "assistant"},
                "create_time": DATETIME_2.timestamp(),
                "update_time": DATETIME_2.timestamp(),
                "content": {"content_type": "text", "parts": ["Hi there!"]},
                "metadata": {"model_slug": "gpt-4"},
            },
            "children": [],
        },
    },
    "current_node": "node2",
    "plugin_ids": [],
    "conversation_id": "conv_id_123",
    "conversation_template_id": "template_id_123",
    "id": "id_123",
}
