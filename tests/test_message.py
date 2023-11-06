"""Tests for the Message class."""

# pyright: reportGeneralTypeIssues=false
# pyright: reportUnknownVariableType=false

from __future__ import annotations

from convoviz.models import Message

from .mocks import ASSISTANT_MESSAGE_111, USER_MESSAGE_111

user_message = Message(**USER_MESSAGE_111)
assistant_message = Message(**ASSISTANT_MESSAGE_111)


def test_author_role() -> None:
    """Test author_role method."""
    assert user_message.author.role == "user"


def test_author_header() -> None:
    """Test author_header method."""
    assert user_message.header == "# Me"

    assert assistant_message.header == "# ChatGPT"


def test_content_text() -> None:
    """Test content_text method."""
    assert user_message.text == "user message 111"

    assert assistant_message.text == "assistant message 111"


def test_content_type() -> None:
    """Test content_type method."""
    assert user_message.content.content_type == "text"


def test_model_slug() -> None:
    """Test model_slug method."""
    assert assistant_message.metadata.model_slug == "gpt-4"
