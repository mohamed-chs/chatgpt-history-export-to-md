"""Tests for markdown flavors."""

from datetime import UTC, datetime

from convoviz.config import AuthorHeaders, ConversationConfig, MarkdownConfig
from convoviz.models import Conversation
from convoviz.renderers.markdown import render_conversation, render_obsidian_callout


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


class TestObsidianCallout:
    """Tests for the render_obsidian_callout function."""

    def test_basic_callout(self) -> None:
        """Test basic callout rendering."""
        result = render_obsidian_callout(
            content="This is the content.",
            title="My Title",
        )
        assert result == "> [!NOTE]- My Title\n> This is the content."

    def test_multiline_content(self) -> None:
        """Test callout with multiline content."""
        result = render_obsidian_callout(
            content="Line 1\nLine 2\nLine 3",
            title="Multiline",
        )
        assert "> [!NOTE]- Multiline" in result
        assert "> Line 1" in result
        assert "> Line 2" in result
        assert "> Line 3" in result

    def test_expanded_callout(self) -> None:
        """Test expanded (not collapsed) callout."""
        result = render_obsidian_callout(
            content="Content",
            title="Title",
            collapsed=False,
        )
        assert "> [!NOTE]+ Title" in result

    def test_custom_callout_type(self) -> None:
        """Test callout with custom type."""
        result = render_obsidian_callout(
            content="Warning content",
            title="Be Careful",
            callout_type="WARNING",
        )
        assert "> [!WARNING]- Be Careful" in result


class TestObsidianReasoningContent:
    """Tests for Obsidian-specific rendering of reasoning content types."""

    def _make_conversation_with_reasoning(self, content_type: str, content: str) -> Conversation:
        """Helper to create a conversation with a reasoning message."""
        ts = datetime(2024, 1, 1, tzinfo=UTC).timestamp()

        # Build the content based on the type
        if content_type == "thoughts":
            message_content = {
                "content_type": "thoughts",
                "thoughts": [{"summary": content}],
            }
        else:  # reasoning_recap
            message_content = {
                "content_type": "reasoning_recap",
                "content": content,
            }

        return Conversation(
            title="Test Conversation",
            create_time=ts,
            update_time=ts,
            mapping={
                "root": {
                    "id": "root",
                    "message": None,
                    "parent": None,
                    "children": ["user_node"],
                },
                "user_node": {
                    "id": "user_node",
                    "message": {
                        "id": "user_node",
                        "author": {"role": "user", "metadata": {}},
                        "create_time": ts,
                        "update_time": ts,
                        "content": {"content_type": "text", "parts": ["Hello"]},
                        "status": "finished_successfully",
                        "end_turn": True,
                        "weight": 1.0,
                        "metadata": {},
                        "recipient": "all",
                    },
                    "parent": "root",
                    "children": ["reasoning_node"],
                },
                "reasoning_node": {
                    "id": "reasoning_node",
                    "message": {
                        "id": "reasoning_node",
                        "author": {"role": "assistant", "metadata": {}},
                        "create_time": ts,
                        "update_time": ts,
                        "content": message_content,
                        "status": "finished_successfully",
                        "end_turn": False,
                        "weight": 1.0,
                        "metadata": {},
                        "recipient": "all",
                    },
                    "parent": "user_node",
                    "children": [],
                },
            },
            moderation_results=[],
            current_node="reasoning_node",
            conversation_id="test_conv",
            id="test_conv",
        )

    def test_obsidian_renders_reasoning_recap_as_callout(self) -> None:
        """Test that obsidian flavor renders reasoning_recap as a collapsible callout."""
        conv = self._make_conversation_with_reasoning(
            "reasoning_recap", "I analyzed the problem step by step."
        )
        config = ConversationConfig(markdown=MarkdownConfig(flavor="obsidian"))
        headers = AuthorHeaders()

        markdown = render_conversation(conv, config, headers)

        # Should have the callout syntax
        assert "> [!NOTE]- 🧠 AI Reasoning" in markdown
        assert "> I analyzed the problem step by step." in markdown

    def test_obsidian_renders_thoughts_as_callout(self) -> None:
        """Test that obsidian flavor renders thoughts as a collapsible callout."""
        conv = self._make_conversation_with_reasoning(
            "thoughts", "Let me think about this..."
        )
        config = ConversationConfig(markdown=MarkdownConfig(flavor="obsidian"))
        headers = AuthorHeaders()

        markdown = render_conversation(conv, config, headers)

        # Should have the callout syntax
        assert "> [!NOTE]- 💭 AI Thoughts" in markdown
        assert "> Let me think about this..." in markdown

    def test_standard_hides_reasoning_recap(self) -> None:
        """Test that standard flavor hides reasoning_recap (unchanged behavior)."""
        conv = self._make_conversation_with_reasoning(
            "reasoning_recap", "I analyzed the problem."
        )
        config = ConversationConfig(markdown=MarkdownConfig(flavor="standard"))
        headers = AuthorHeaders()

        markdown = render_conversation(conv, config, headers)

        # Should NOT contain the reasoning content
        assert "I analyzed the problem" not in markdown
        assert "[!NOTE]" not in markdown

    def test_standard_hides_thoughts(self) -> None:
        """Test that standard flavor hides thoughts (unchanged behavior)."""
        conv = self._make_conversation_with_reasoning(
            "thoughts", "Let me think..."
        )
        config = ConversationConfig(markdown=MarkdownConfig(flavor="standard"))
        headers = AuthorHeaders()

        markdown = render_conversation(conv, config, headers)

        # Should NOT contain the thoughts content
        assert "Let me think" not in markdown
        assert "[!NOTE]" not in markdown
