"""Tests for the Message class."""

from typing import Any, Literal

import pytest

from models.message import Message


def test_message_initialization() -> None:
    """Test initialization of Message object."""
    # Sample message dictionary
    message_dict: dict[str, Any] = {
        "id": "sample_id",
        "author": {"role": "user"},
        "create_time": 123456.789,
        "update_time": 123457.789,
        "content": {"content_type": "text", "parts": ["Hello World"]},
        "status": "finished_successfully",
        "end_turn": True,
        "weight": 1.0,
        "metadata": {"model_slug": "gpt-4"},
        "recipient": "all",
    }

    # Initialize Message object
    message = Message(message=message_dict)

    # Assert attributes
    assert message.id == "sample_id"
    assert message.author == {"role": "user"}
    assert message.create_time == 123456.789
    assert message.update_time == 123457.789
    assert message.content == {"content_type": "text", "parts": ["Hello World"]}
    assert message.status == "finished_successfully"
    assert message.end_turn is True
    assert message.weight == 1.0
    assert message.metadata == {"model_slug": "gpt-4"}
    assert message.recipient == "all"


def test_author_role() -> None:
    """Test author_role method."""
    message = Message(message={"author": {"role": "user"}})
    assert message.author_role() == "user"


@pytest.mark.parametrize(
    "role, header",
    [
        ("user", "# User"),
        ("assistant", "# Assistant"),
        ("system", "### System"),
        ("tool", "### Tool output"),
        ("unknown", ""),
    ],
)
def test_author_header(
    role: Literal["user", "assistant", "system", "tool", "unknown"],
    header: Literal["# User", "# Assistant", "### System", "### Tool output", ""],
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
    message = Message(message={"content": {"content_type": "text"}})
    assert message.content_type() == "text"


def test_model_slug() -> None:
    """Test model_slug method."""
    message = Message(message={"metadata": {"model_slug": "gpt-4"}})
    assert message.model_slug() == "gpt-4"
