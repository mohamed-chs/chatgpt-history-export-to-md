"""Tests for markdown flavors and Obsidian block IDs."""

from convoviz.config import AuthorHeaders, ConversationConfig, MarkdownConfig
from convoviz.models import Conversation
from convoviz.renderers.markdown import render_conversation, shorten_id


def test_shorten_id_with_uuid() -> None:
    """Test that UUIDs are shortened to 8 characters."""
    uuid = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
    assert shorten_id(uuid) == "a1b2c3d4"


def test_shorten_id_with_short_id() -> None:
    """Test that short IDs are returned as-is (truncated)."""
    short_id = "abc"
    assert shorten_id(short_id) == "abc"


def test_obsidian_flavor_rendering(mock_conversation: Conversation) -> None:
    """Test rendering with obsidian flavor."""
    # Force obsidian flavor
    config = ConversationConfig(markdown=MarkdownConfig(flavor="obsidian"))
    headers = AuthorHeaders()

    markdown = render_conversation(mock_conversation, config, headers)

    # Check for Obsidian block IDs (IDs are shortened to 8 chars)
    # In mock_conversation, nodes have IDs like "user_node_111" -> shortened to "user_nod"

    # Check for parent link in second node (if it has parent)
    # The format should be [⬆️](#^shortened-id)
    assert "[⬆️](#^" in markdown

    # Check for block ID at end of header (shortened)
    # The format should be # Me ^shortened-id
    assert "# Me ^" in markdown
    assert "# ChatGPT ^" in markdown

    # Verify IDs are shortened (original IDs are longer than 8 chars)
    # e.g., "user_node_111" becomes "user_nod"
    assert "^user_nod" in markdown  # Shortened from "user_node_111"
    assert "^assistan" in markdown  # Shortened from "assistant_node_111"

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
