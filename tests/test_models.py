"""Tests for the models."""

import copy
from datetime import datetime

from convoviz.models import Conversation
from convoviz.models.collection import ConversationCollection
from convoviz.models.message import Message, MessageAuthor, MessageContent, MessageMetadata


def test_leaf_count(mock_conversation: Conversation) -> None:
    """Test leaf_count property."""
    assert mock_conversation.leaf_count == 1


def test_url(mock_conversation: Conversation) -> None:
    """Test url property."""
    assert mock_conversation.url == "https://chat.openai.com/c/conversation_111"


def test_content_types(mock_conversation: Conversation) -> None:
    """Test content_types property."""
    assert set(mock_conversation.content_types) == {"text"}


def test_message_count(mock_conversation: Conversation) -> None:
    """Test message_count method."""
    assert mock_conversation.message_count("user", "assistant") == 2
    assert mock_conversation.message_count("user") == 1
    assert mock_conversation.message_count("assistant") == 1
    # Internal system messages are hidden by default and should not be counted.
    assert mock_conversation.message_count("system") == 0


def test_plaintext(mock_conversation: Conversation) -> None:
    """Test plaintext method."""
    assert mock_conversation.plaintext("user") == "user message 111"
    assert mock_conversation.plaintext("assistant") == "assistant message 111"
    # Internal system messages are hidden by default and should not contribute plaintext.
    assert mock_conversation.plaintext("system") == ""


def test_model(mock_conversation: Conversation) -> None:
    """Test model property."""
    assert mock_conversation.model == "gpt-4"


def test_plugins(mock_conversation: Conversation) -> None:
    """Test plugins property."""
    assert len(mock_conversation.plugins) == 0


def test_timestamps(mock_conversation: Conversation) -> None:
    """Test timestamps method."""
    timestamps = mock_conversation.timestamps("user")
    assert len(timestamps) == 1


def test_nodes_by_author(mock_conversation: Conversation) -> None:
    """Test nodes_by_author method."""
    user_nodes = mock_conversation.nodes_by_author("user")
    assert len(user_nodes) == 1
    assert user_nodes[0].message is not None
    assert user_nodes[0].message.author.role == "user"
    # Internal system messages are hidden by default.
    assert mock_conversation.nodes_by_author("system") == []


def test_all_message_nodes(mock_conversation: Conversation) -> None:
    """Test all_message_nodes property."""
    nodes = mock_conversation.all_message_nodes
    assert len(nodes) == 3  # system, user, assistant


def test_message_visibility() -> None:
    """Test message is_empty and is_hidden properties."""
    base_data = {
        "id": "msg_id",
        "create_time": datetime.now(),
        "update_time": datetime.now(),
        "status": "finished_successfully",
        "end_turn": True,
        "weight": 1.0,
        "recipient": "all",
    }

    # Case 1: Empty message
    msg = Message(
        author=MessageAuthor(role="user"),
        content=MessageContent(content_type="text", parts=[""]),
        metadata=MessageMetadata(),
        **base_data,
    )
    assert msg.is_empty
    assert msg.is_hidden

    # Case 2: Visible user message
    msg = Message(
        author=MessageAuthor(role="user"),
        content=MessageContent(content_type="text", parts=["Hello"]),
        metadata=MessageMetadata(),
        **base_data,
    )
    assert not msg.is_empty
    assert not msg.is_hidden

    # Case 3: Internal System message (hidden)
    msg = Message(
        author=MessageAuthor(role="system"),
        content=MessageContent(content_type="text", parts=["You are ChatGPT"]),
        metadata=MessageMetadata(),
        **base_data,
    )
    assert not msg.is_empty
    assert msg.is_hidden

    # Case 4: User System message (visible)
    msg = Message(
        author=MessageAuthor(role="system"),
        content=MessageContent(content_type="text", parts=["My instructions"]),
        metadata=MessageMetadata(is_user_system_message=True),
        **base_data,
    )
    assert not msg.is_hidden

    # Case 5: Browser tool (hidden)
    msg = Message(
        author=MessageAuthor(role="tool", name="browser"),
        content=MessageContent(content_type="text", parts=["search query"]),
        metadata=MessageMetadata(),
        **base_data,
    )
    assert msg.is_hidden

    # Case 6: Browsing status (hidden)
    msg = Message(
        author=MessageAuthor(role="assistant"),
        content=MessageContent(content_type="tether_browsing_display", parts=["Browsing..."]),
        metadata=MessageMetadata(),
        **base_data,
    )
    assert msg.is_hidden

    # Case 7: Assistant tool call to browser (hidden)
    msg = Message(
        author=MessageAuthor(role="assistant"),
        content=MessageContent(content_type="code", parts=["search('foo')"]),
        metadata=MessageMetadata(),
        **{**base_data, "recipient": "browser"},
    )
    assert msg.is_hidden

    # Case 8: Assistant tool call with recipient=all (hidden due to content_type=code)
    msg = Message(
        author=MessageAuthor(role="assistant"),
        content=MessageContent(content_type="code", parts=["search('foo')"]),
        metadata=MessageMetadata(),
        **{**base_data, "recipient": "all"},
    )
    assert msg.is_hidden


def test_collection_update_merges_new_conversations_even_if_older(
    mock_conversation: Conversation, mock_conversation_data: dict
) -> None:
    """A new conversation should not be skipped just because it's older than last_updated."""
    base = ConversationCollection(conversations=[mock_conversation])

    older_new_data = copy.deepcopy(mock_conversation_data)
    older_new_data["title"] = "conversation 222"
    older_new_data["conversation_id"] = "conversation_222"
    older_new_data["id"] = "conversation_222"
    # Deliberately set update_time earlier than base.last_updated
    older_new_data["update_time"] = older_new_data["create_time"]

    other = ConversationCollection(conversations=[Conversation(**older_new_data)])
    base.update(other)

    ids = {c.conversation_id for c in base.conversations}
    assert "conversation_111" in ids
    assert "conversation_222" in ids


def test_collection_update_keeps_newest_when_ids_collide(mock_conversation: Conversation) -> None:
    """When IDs collide, the newest update_time should win."""
    base = ConversationCollection(conversations=[mock_conversation])

    updated = mock_conversation.model_copy(deep=True)
    updated.update_time = updated.update_time.replace(year=updated.update_time.year + 1)

    base.update(ConversationCollection(conversations=[updated]))
    assert base.index[mock_conversation.conversation_id].update_time == updated.update_time
