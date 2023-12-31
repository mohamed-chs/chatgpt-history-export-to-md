"""Tests for the Conversation class."""

# pyright: reportUnknownVariableType=false
# pyright: reportGeneralTypeIssues=false

from __future__ import annotations

from convoviz.models import Conversation

from .mocks import (
    ASSISTANT_MESSAGE_TEXT_111,
    CONVERSATION_111,
    CONVERSATION_ID_111,
    DATETIME_111,
    MESSAGE_COUNT_111,
    TITLE_111,
    USER_MESSAGE_TEXT_111,
)

conversation = Conversation(**CONVERSATION_111)


def test_leaf_count() -> None:
    """Test leaf_count method."""
    assert conversation.leaf_count == 1


def test_chat_link() -> None:
    """Test chat_link method."""
    assert conversation.url == f"https://chat.openai.com/c/{CONVERSATION_ID_111}"


def test_content_types() -> None:
    """Test content_types method."""
    assert set(conversation.content_types) == {"text"}


def test_message_count() -> None:
    """Test message_count method."""
    assert conversation.message_count("user", "assistant") == MESSAGE_COUNT_111


def test_entire_author_text() -> None:
    """Test entire_author_text method."""
    assert conversation.plaintext("user") == USER_MESSAGE_TEXT_111
    assert conversation.plaintext("assistant") == ASSISTANT_MESSAGE_TEXT_111


def test_author_message_timestamps() -> None:
    """Test author_message_timestamps method."""
    assert conversation.timestamps("user") == [
        DATETIME_111.timestamp(),
    ]


def test_model_slug() -> None:
    """Test model_slug method."""
    assert conversation.model == "gpt-4"


def test_used_plugins() -> None:
    """Test used_plugins method."""
    assert len(conversation.plugins) == 0


def test_yaml_header() -> None:
    """Test yaml_header method."""
    yaml_header = conversation.yaml
    assert "---" in yaml_header
    assert f"title: {TITLE_111}" in yaml_header


def test_to_markdown() -> None:
    """Test to_markdown method."""
    markdown = conversation.markdown
    assert "---" in markdown
    assert "# Me" in markdown
    assert USER_MESSAGE_TEXT_111 in markdown
    assert "# ChatGPT" in markdown
    assert ASSISTANT_MESSAGE_TEXT_111 in markdown


def test_start_of_year() -> None:
    """Test start_of_year method."""
    assert conversation.year_start.year == DATETIME_111.year
    assert conversation.year_start.month == 1
    assert conversation.year_start.day == 1


def test_start_of_month() -> None:
    """Test start_of_month method."""
    assert conversation.month_start.year == DATETIME_111.year
    assert conversation.month_start.month == DATETIME_111.month
    assert conversation.month_start.day == 1


def test_start_of_week() -> None:
    """Test start_of_week method."""
    assert conversation.week_start.year == DATETIME_111.year
    assert conversation.week_start.month == DATETIME_111.month
    assert conversation.week_start.day == DATETIME_111.day - DATETIME_111.weekday()
