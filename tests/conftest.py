"""Fixtures for testing."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from zipfile import ZipFile

import pytest

from convoviz.models import Conversation

DATETIME_111 = datetime(
    year=2023,
    month=7,
    day=29,
    hour=8,
    minute=0,
    second=0,
    tzinfo=timezone.utc,
)

DATETIME_112 = DATETIME_111 + timedelta(minutes=5)

@pytest.fixture
def mock_conversation_data():
    """Return a dictionary representing a raw conversation."""
    return {
        "title": "conversation 111",
        "create_time": DATETIME_111.timestamp(),
        "update_time": DATETIME_112.timestamp(),
        "mapping": {
            "root_node_111": {
                "id": "root_node_111",
                "message": None,
                "parent": None,
                "children": ["system_node_111"],
            },
            "system_node_111": {
                "id": "system_node_111",
                "message": {
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
                },
                "parent": None,
                "children": ["user_node_111"],
            },
            "user_node_111": {
                "id": "user_node_111",
                "message": {
                    "id": "user_node_111",
                    "author": {"role": "user", "metadata": {}},
                    "create_time": DATETIME_111.timestamp(),
                    "update_time": DATETIME_111.timestamp(),
                    "content": {"content_type": "text", "parts": ["user message 111"]},
                    "status": "finished_successfully",
                    "end_turn": True,
                    "weight": 1.0,
                    "metadata": {"model_slug": "gpt-4"},
                    "recipient": "all",
                },
                "parent": None,
                "children": ["assistant_node_111"],
            },
            "assistant_node_111": {
                "id": "assistant_node_111",
                "message": {
                    "id": "assistant_node_111",
                    "author": {"role": "assistant", "metadata": {}},
                    "create_time": DATETIME_112.timestamp(),
                    "update_time": DATETIME_112.timestamp(),
                    "content": {"content_type": "text", "parts": ["assistant message 111"]},
                    "status": "finished_successfully",
                    "end_turn": True,
                    "weight": 1.0,
                    "metadata": {"model_slug": "gpt-4"},
                    "recipient": "all",
                },
                "parent": None,
                "children": [],
            },
        },
        "moderation_results": [],
        "current_node": "assistant_node_111",
        "plugin_ids": [],
        "conversation_id": "conversation_111",
        "conversation_template_id": "template_111",
        "id": "conversation_111",
    }

@pytest.fixture
def mock_conversation(mock_conversation_data):
    """Return a Conversation object."""
    return Conversation(**mock_conversation_data)

@pytest.fixture
def mock_conversations_json(mock_conversation_data, tmp_path):
    """Create a temporary conversations.json file."""
    # Create a list of conversations (just one for now)
    data = [mock_conversation_data]
    file_path = tmp_path / "conversations.json"
    with open(file_path, "w") as f:
        json.dump(data, f)
    return file_path

@pytest.fixture
def mock_zip_file(mock_conversations_json, tmp_path):
    """Create a temporary zip file containing conversations.json."""
    zip_path = tmp_path / "test_export.zip"
    with ZipFile(zip_path, "w") as zf:
        zf.write(mock_conversations_json, "conversations.json")
    return zip_path
