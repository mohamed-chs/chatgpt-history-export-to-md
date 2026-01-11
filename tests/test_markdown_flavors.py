"""Tests for markdown flavors."""

from convoviz.config import AuthorHeaders, ConversationConfig, MarkdownConfig
from convoviz.models import Conversation
from convoviz.renderers.markdown import render_conversation


def test_obsidian_flavor_rendering(mock_conversation: Conversation) -> None:
    """Test rendering with obsidian flavor produces same output as standard for now.

    The obsidian flavor option is preserved for future obsidian-specific features,
    but currently both flavors produce identical output.
    """
    config = ConversationConfig(markdown=MarkdownConfig(flavor="obsidian"))
    headers = AuthorHeaders()

    markdown = render_conversation(mock_conversation, config, headers)

    # Should have author headers (same as standard)
    assert "# Me" in markdown
    assert "# ChatGPT" in markdown

    # Should NOT have block IDs or navigation links (removed feature)
    assert "^" not in markdown
    assert "[⬆️]" not in markdown
    assert "[⬇️]" not in markdown


def test_standard_flavor_rendering(mock_conversation: Conversation) -> None:
    """Test rendering with standard flavor."""
    config = ConversationConfig(markdown=MarkdownConfig(flavor="standard"))
    headers = AuthorHeaders()

    markdown = render_conversation(mock_conversation, config, headers)

    # Should NOT have block IDs or links
    assert "^" not in markdown
    assert "[⬆️]" not in markdown
    assert "[⬇️]" not in markdown

    # Should still have author headers
    assert "# Me" in markdown
    assert "# ChatGPT" in markdown


def test_flavor_default_is_standard() -> None:
    """Test that standard is the default flavor."""
    config = MarkdownConfig()
    assert config.flavor == "standard"
