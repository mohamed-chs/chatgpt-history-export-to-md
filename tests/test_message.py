"""Tests for the Message class."""

from __future__ import annotations

from typing import Literal

import pytest

from models.message import Message

from .mocks import DATETIME_1, MESSAGE_1


def test_message_initialization() -> None:
    """Test initialization of Message object."""
    message = Message(message=MESSAGE_1)

    assert message.id == "sample_id"
    assert message.author == {"role": "user"}
    assert message.create_time == DATETIME_1.timestamp()
    assert message.update_time == DATETIME_1.timestamp()
    assert message.content == {"content_type": "text", "parts": ["Hello World"]}
    assert message.status == "finished_successfully"
    assert message.end_turn is True
    assert message.weight == 1
    assert message.metadata == {"model_slug": "gpt-4"}
    assert message.recipient == "all"


def test_author_role() -> None:
    """Test author_role method."""
    message = Message(message=MESSAGE_1)
    assert message.author_role() == "user"


@pytest.mark.parametrize(
    ("role", "header"),
    [
        ("user", "# User"),
        ("assistant", "# Assistant"),
        ("system", "### System"),
        ("tool", "### Tool output"),
    ],
)
def test_author_header(
    role: Literal["user", "assistant", "system", "tool"],
    header: Literal[
        "# User",
        "# Assistant",
        "### System",
        "### Tool output",
    ],
) -> None:
    """Test author_header method."""
    Message.configuration = {"author_headers": {}}
    message = Message(message={"author": {"role": role}})
    assert message.author_header() == header


def test_content_text() -> None:
    """Test content_text method."""
    message = Message(message={"content": {"parts": ["Hello World"]}})
    assert message.content_text() == "Hello World"

    message = Message(message={"content": {"text": "print('Hello World')"}})
    assert message.content_text() == "```python\nprint('Hello World')\n```"


def test_content_type() -> None:
    """Test content_type method."""
    message = Message(message=MESSAGE_1)
    assert message.content_type() == "text"


def test_model_slug() -> None:
    """Test model_slug method."""
    message = Message(message=MESSAGE_1)
    assert message.model_slug() == "gpt-4"
