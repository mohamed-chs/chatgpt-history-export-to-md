"""Tests for the Message class."""

from __future__ import annotations

from convoviz.models import Message

from .mocks import ASSISTANT_MESSAGE_111, USER_MESSAGE_111


def test_author_role() -> None:
    """Test author_role method."""
    message = Message(USER_MESSAGE_111)
    assert message.author_role == "user"


def test_author_header() -> None:
    """Test author_header method."""
    user_message = Message(USER_MESSAGE_111)
    assert user_message.author_header == "# Me"

    assistant_message = Message(ASSISTANT_MESSAGE_111)
    assert assistant_message.author_header == "# ChatGPT"


def test_content_text() -> None:
    """Test content_text method."""
    user_message = Message(USER_MESSAGE_111)
    assert user_message.content_text == "user message 111"

    assistant_message = Message(ASSISTANT_MESSAGE_111)
    assert assistant_message.content_text == "assistant message 111"


def test_content_type() -> None:
    """Test content_type method."""
    message = Message(USER_MESSAGE_111)
    assert message.content_type == "text"


def test_model_slug() -> None:
    """Test model_slug method."""
    message = Message(ASSISTANT_MESSAGE_111)
    assert message.model_slug == "gpt-4"
