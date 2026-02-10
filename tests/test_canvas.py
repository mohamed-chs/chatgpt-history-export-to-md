"""Tests for Canvas (canmore) support."""

from datetime import UTC, datetime
from pathlib import Path

from convoviz.io.canvas import get_extension, save_canvas_documents
from convoviz.models import Conversation, ConversationCollection
from convoviz.models.message import (
    Message,
    MessageAuthor,
    MessageContent,
    MessageMetadata,
)


def test_canvas_document_extraction() -> None:
    """Test extracting Canvas document from a message."""
    ts = datetime(2025, 1, 1, tzinfo=UTC)

    # Create a mock Canvas message
    canvas_data = {
        "name": "breakout_game",
        "type": "code/html",
        "content": "<!DOCTYPE html><html>...</html>",
    }

    msg = Message(
        id="msg_canvas",
        author=MessageAuthor(role="assistant"),
        content=MessageContent(content_type="text", parts=[canvas_data]),
        metadata=MessageMetadata(),
        create_time=ts,
        update_time=ts,
        status="finished_successfully",
        end_turn=True,
        weight=1.0,
        recipient="canmore.create_textdoc",
    )

    doc = msg.canvas_document
    assert doc is not None
    assert doc["name"] == "breakout_game"
    assert doc["type"] == "code/html"
    assert doc["content"] == "<!DOCTYPE html><html>...</html>"

    # Verify Message.text extraction
    assert "### Canvas: breakout_game" in msg.text


def test_conversation_canvas_documents() -> None:
    """Test aggregating Canvas documents in a conversation."""
    ts = datetime(2025, 1, 1, tzinfo=UTC)

    canvas_data = {"name": "test_doc", "type": "text/plain", "content": "hello"}

    conv = Conversation(
        title="Canvas Conv",
        create_time=ts,
        update_time=ts,
        mapping={
            "root": {
                "id": "root",
                "message": None,
                "parent": None,
                "children": ["msg_1"],
            },
            "msg_1": {
                "id": "msg_1",
                "message": {
                    "id": "msg_1",
                    "author": {"role": "assistant"},
                    "content": {"content_type": "text", "parts": [canvas_data]},
                    "metadata": {},
                    "create_time": ts,
                    "update_time": ts,
                    "status": "finished_successfully",
                    "end_turn": True,
                    "weight": 1.0,
                    "recipient": "canmore.create_textdoc",
                },
                "parent": "root",
                "children": [],
            },
        },
        current_node="msg_1",
        conversation_id="conv_123",
    )

    docs = conv.canvas_documents
    assert len(docs) == 1
    assert docs[0]["name"] == "test_doc"
    assert docs[0]["conversation_id"] == "conv_123"


def test_save_canvas_documents(tmp_path: Path) -> None:
    """Test saving Canvas documents to files."""
    ts = datetime(2025, 1, 1, tzinfo=UTC)
    canvas_data = {"name": "script", "type": "code/python", "content": "print('hi')"}

    conv = Conversation(
        title="Test",
        create_time=ts,
        update_time=ts,
        mapping={
            "root": {
                "id": "root",
                "message": None,
                "parent": None,
                "children": ["msg_1"],
            },
            "msg_1": {
                "id": "msg_1",
                "message": {
                    "id": "msg_1",
                    "author": {"role": "assistant"},
                    "content": {"content_type": "text", "parts": [canvas_data]},
                    "metadata": {},
                    "create_time": ts,
                    "update_time": ts,
                    "status": "finished_successfully",
                    "end_turn": True,
                    "weight": 1.0,
                    "recipient": "canmore.create_textdoc",
                },
                "parent": "root",
                "children": [],
            },
        },
        current_node="msg_1",
        conversation_id="conv_abcdefghijk",
    )

    collection = ConversationCollection(conversations=[conv])
    save_canvas_documents(collection, tmp_path)

    # Check for expected file
    canvas_dir = tmp_path / "canvas"
    assert canvas_dir.exists()

    # Filename should be "[conv_abc] script.py" (short ID is first 8 chars)
    expected_name = "[conv_abc] script.py"
    expected_path = canvas_dir / expected_name
    assert expected_path.exists()
    assert expected_path.read_text() == "print('hi')"


def test_canvas_json_string_in_parts() -> None:
    """Test extracting Canvas document from a JSON string in parts."""
    ts = datetime(2025, 1, 1, tzinfo=UTC)
    canvas_json = (
        '{"name": "string_part", "type": "code/python", "content": "print(123)"}'
    )

    msg = Message(
        id="msg_json_parts",
        author=MessageAuthor(role="assistant"),
        content=MessageContent(content_type="text", parts=[canvas_json]),
        metadata=MessageMetadata(),
        create_time=ts,
        update_time=ts,
        status="finished_successfully",
        end_turn=True,
        weight=1.0,
        recipient="canmore.create_textdoc",
    )

    doc = msg.canvas_document
    assert doc is not None
    assert doc["name"] == "string_part"
    assert doc["content"] == "print(123)"
    assert "### Canvas: string_part" in msg.text


def test_canvas_document_in_non_first_part() -> None:
    """Test extracting Canvas document when it is not the first part."""
    ts = datetime(2025, 1, 1, tzinfo=UTC)
    canvas_data = {
        "name": "later_part",
        "type": "code/html",
        "content": "<div>ok</div>",
    }

    msg = Message(
        id="msg_late_part",
        author=MessageAuthor(role="assistant"),
        content=MessageContent(
            content_type="text",
            parts=[{"text": "prefix"}, canvas_data],
        ),
        metadata=MessageMetadata(),
        create_time=ts,
        update_time=ts,
        status="finished_successfully",
        end_turn=True,
        weight=1.0,
        recipient="canmore.create_textdoc",
    )

    doc = msg.canvas_document
    assert doc is not None
    assert doc["name"] == "later_part"


def test_get_extension_defaults() -> None:
    assert get_extension(None) == ".txt"
    assert get_extension("unknown/type") == ".txt"


def test_canvas_json_string_in_text() -> None:
    """Test extracting Canvas document from a JSON string in content.text."""
    ts = datetime(2025, 1, 1, tzinfo=UTC)
    canvas_json = '{"name": "string_text", "type": "code/javascript", "content": "console.log(1)"}'

    msg = Message(
        id="msg_json_text",
        author=MessageAuthor(role="assistant"),
        content=MessageContent(content_type="code", text=canvas_json),
        metadata=MessageMetadata(),
        create_time=ts,
        update_time=ts,
        status="finished_successfully",
        end_turn=True,
        weight=1.0,
        recipient="canmore.create_textdoc",
    )

    doc = msg.canvas_document
    assert doc is not None
    assert doc["name"] == "string_text"
    assert doc["content"] == "console.log(1)"
    assert "### Canvas: string_text" in msg.text
