"""Tests for markdown flavors and Obsidian block IDs."""

from convoviz.config import AuthorHeaders, ConversationConfig, MarkdownConfig
from convoviz.models import Conversation
from convoviz.renderers.markdown import render_conversation


def test_obsidian_flavor_rendering(mock_conversation: Conversation) -> None:
    """Test rendering with obsidian flavor."""
    # Force obsidian flavor
    config = ConversationConfig(markdown=MarkdownConfig(flavor="obsidian"))
    headers = AuthorHeaders()

    markdown = render_conversation(mock_conversation, config, headers)

    # Check for Obsidian block IDs
    # In mock_conversation (from conftest.py usually), nodes have IDs like "1", "2" etc.
    # The first node is usually user, second is assistant.

    # Check for parent link in second node (if it has parent)
    # The format should be [⬆️](#^parent-id)
    assert "[⬆️](#^" in markdown

    # Check for block ID at end of header
    # The format should be # Me ^id
    assert "# Me ^" in markdown
    assert "# ChatGPT ^" in markdown

    # Check that "parent" and "child" words are omitted
    assert "parent ⬆️" not in markdown
    assert "child ⬇️" not in markdown
    assert "⬇️" in markdown


def test_standard_flavor_rendering(mock_conversation: Conversation) -> None:
    """Test rendering with standard flavor."""
    config = ConversationConfig(markdown=MarkdownConfig(flavor="standard"))
    headers = AuthorHeaders()

    markdown = render_conversation(mock_conversation, config, headers)

    # Should NOT have block IDs or links
    assert "^" not in markdown
    assert "[⬆️]" not in markdown
    assert "[⬇️]" not in markdown
    assert "[parent ⬆️]" not in markdown

    # Should still have author headers
    assert "# Me" in markdown
    assert "# ChatGPT" in markdown
