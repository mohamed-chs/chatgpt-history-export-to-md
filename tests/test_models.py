"""Tests for the models."""

from convoviz.models import Conversation


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


def test_plaintext(mock_conversation: Conversation) -> None:
    """Test plaintext method."""
    assert mock_conversation.plaintext("user") == "user message 111"
    assert mock_conversation.plaintext("assistant") == "assistant message 111"


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


def test_all_message_nodes(mock_conversation: Conversation) -> None:
    """Test all_message_nodes property."""
    nodes = mock_conversation.all_message_nodes
    assert len(nodes) == 3  # system, user, assistant
