"""Tests for the models."""

from __future__ import annotations

from convoviz.models import Conversation


def test_leaf_count(mock_conversation: Conversation) -> None:
    """Test leaf_count method."""
    assert mock_conversation.leaf_count == 1


def test_chat_link(mock_conversation: Conversation) -> None:
    """Test chat_link method."""
    assert mock_conversation.url == "https://chat.openai.com/c/conversation_111"


def test_content_types(mock_conversation: Conversation) -> None:
    """Test content_types method."""
    assert set(mock_conversation.content_types) == {"text"}


def test_message_count(mock_conversation: Conversation) -> None:
    """Test message_count method."""
    assert mock_conversation.message_count("user", "assistant") == 2


def test_entire_author_text(mock_conversation: Conversation) -> None:
    """Test entire_author_text method."""
    assert mock_conversation.plaintext("user") == "user message 111"
    assert mock_conversation.plaintext("assistant") == "assistant message 111"


def test_model_slug(mock_conversation: Conversation) -> None:
    """Test model_slug method."""
    assert mock_conversation.model == "gpt-4"


def test_used_plugins(mock_conversation: Conversation) -> None:
    """Test used_plugins method."""
    assert len(mock_conversation.plugins) == 0


def test_yaml_header(mock_conversation: Conversation) -> None:
    """Test yaml_header method."""
    yaml_header = mock_conversation.yaml
    assert "---" in yaml_header
    assert "title: conversation 111" in yaml_header


def test_markdown(mock_conversation: Conversation) -> None:
    """Test markdown method."""
    markdown = mock_conversation.markdown
    assert "---" in markdown
    assert "# Me" in markdown
    assert "user message 111" in markdown
    assert "# ChatGPT" in markdown
    assert "assistant message 111" in markdown
