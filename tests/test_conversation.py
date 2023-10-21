"""Tests for the Conversation class."""

from __future__ import annotations

from typing import Any

from models.conversation import Conversation
from models.node import Node

from .mocks import CONVERSATION_1, DATETIME_1, DATETIME_2


def test_conversation_initialization() -> None:
    """Test initialization of Conversation object."""
    data: dict[str, Any] = CONVERSATION_1
    conversation = Conversation(conversation=data)

    assert conversation.title == "Sample Conversation"
    assert conversation.create_time == DATETIME_1.timestamp()
    assert conversation.update_time == DATETIME_2.timestamp()
    assert isinstance(conversation.mapping, dict)
    assert isinstance(conversation.current_node, Node)


def test_leaf_count() -> None:
    """Test leaf_count method."""
    data: dict[str, Any] = CONVERSATION_1
    conversation = Conversation(conversation=data)

    assert conversation.leaf_count() == 1


def test_has_multiple_branches() -> None:
    """Test has_multiple_branches method."""
    data: dict[str, Any] = CONVERSATION_1
    conversation = Conversation(conversation=data)

    assert not conversation.has_multiple_branches()


def test_chat_link() -> None:
    """Test chat_link method."""
    data: dict[str, Any] = CONVERSATION_1
    conversation = Conversation(conversation=data)

    assert conversation.chat_link() == "https://chat.openai.com/c/conv_id_123"


def test_content_types() -> None:
    """Test content_types method."""
    data: dict[str, Any] = CONVERSATION_1
    conversation = Conversation(conversation=data)

    assert set(conversation.content_types()) == {"text"}


def test_message_count() -> None:
    """Test message_count method."""
    data: dict[str, Any] = CONVERSATION_1
    conversation = Conversation(conversation=data)

    assert conversation.message_count() == 2


def test_entire_author_text() -> None:
    """Test entire_author_text method."""
    data: dict[str, Any] = CONVERSATION_1
    conversation = Conversation(conversation=data)

    assert conversation.entire_author_text(author="user") == "Hello!"
    assert conversation.entire_author_text(author="assistant") == "Hi there!"


def test_author_message_timestamps() -> None:
    """Test author_message_timestamps method."""
    data: dict[str, Any] = CONVERSATION_1
    conversation = Conversation(conversation=data)

    assert conversation.author_message_timestamps(author="user") == [
        DATETIME_1.timestamp(),
    ]


def test_model_slug() -> None:
    """Test model_slug method."""
    data: dict[str, Any] = CONVERSATION_1
    conversation = Conversation(conversation=data)

    assert conversation.model_slug() == "gpt-4"


def test_used_plugins() -> None:
    """Test used_plugins method."""
    data: dict[str, Any] = CONVERSATION_1
    conversation = Conversation(conversation=data)

    assert len(conversation.used_plugins()) == 0


def test_sanitized_title() -> None:
    """Test sanitized_title method."""
    data: dict[str, Any] = CONVERSATION_1
    conversation = Conversation(conversation=data)

    assert conversation.sanitized_title() == "Sample Conversation"


def test_yaml_header() -> None:
    """Test yaml_header method."""
    data: dict[str, Any] = CONVERSATION_1
    conversation = Conversation(conversation=data)

    yaml_header: str = conversation.yaml_header()
    assert "---" in yaml_header
    assert "title: Sample Conversation" in yaml_header


def test_to_markdown() -> None:
    """Test to_markdown method."""
    data: dict[str, Any] = CONVERSATION_1
    conversation = Conversation(conversation=data)

    markdown: str = conversation.markdown_text()
    assert "---" in markdown
    assert "# User" in markdown
    assert "Hello!" in markdown
    assert "# Assistant" in markdown
    assert "Hi there!" in markdown


def test_start_of_year() -> None:
    """Test start_of_year method."""
    data: dict[str, Any] = CONVERSATION_1
    conversation = Conversation(conversation=data)

    assert conversation.start_of_year().year == DATETIME_1.year
    assert conversation.start_of_year().month == 1
    assert conversation.start_of_year().day == 1


def test_start_of_month() -> None:
    """Test start_of_month method."""
    data: dict[str, Any] = CONVERSATION_1
    conversation = Conversation(conversation=data)

    assert conversation.start_of_month().year == DATETIME_1.year
    assert conversation.start_of_month().month == DATETIME_1.month
    assert conversation.start_of_month().day == 1


def test_start_of_week() -> None:
    """Test start_of_week method."""
    data: dict[str, Any] = CONVERSATION_1
    conversation = Conversation(conversation=data)

    assert conversation.start_of_week().year == DATETIME_1.year
    assert conversation.start_of_week().month == DATETIME_1.month
    assert conversation.start_of_week().day == DATETIME_1.day - DATETIME_1.weekday()
