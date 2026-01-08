"""Tests for the renderers module."""

from convoviz.config import AuthorHeaders, ConversationConfig, YAMLConfig
from convoviz.models import Conversation
from convoviz.renderers import render_conversation
from convoviz.renderers.markdown import (
    close_code_blocks,
    code_block,
    render_message_header,
    replace_latex_delimiters,
)
from convoviz.renderers.yaml import render_yaml_header


class TestCloseCodeBlocks:
    """Tests for the close_code_blocks function."""

    def test_closed_code_block(self) -> None:
        """Test already closed code block."""
        text = "```python\ncode\n```"
        assert close_code_blocks(text) == text

    def test_unclosed_code_block(self) -> None:
        """Test unclosed code block gets closed."""
        text = "```python\ncode"
        assert close_code_blocks(text) == "```python\ncode\n```"

    def test_multiple_closed_blocks(self) -> None:
        """Test multiple closed blocks."""
        text = "```python\ncode\n```\n```js\nmore\n```"
        assert close_code_blocks(text) == text


class TestReplaceLatexDelimiters:
    """Tests for the replace_latex_delimiters function."""

    def test_block_delimiters(self) -> None:
        """Test replacing block delimiters."""
        text = r"\[x^2\]"
        assert replace_latex_delimiters(text) == "$$x^2$$"

    def test_inline_delimiters(self) -> None:
        """Test replacing inline delimiters."""
        text = r"\(x^2\)"
        assert replace_latex_delimiters(text) == "$x^2$"

    def test_mixed_delimiters(self) -> None:
        """Test replacing mixed delimiters."""
        text = r"Inline \(x\) and block \[y\]"
        assert replace_latex_delimiters(text) == "Inline $x$ and block $$y$$"


class TestCodeBlock:
    """Tests for the code_block function."""

    def test_default_language(self) -> None:
        """Test code block with default language."""
        result = code_block("print('hello')")
        assert result == "```python\nprint('hello')\n```"

    def test_custom_language(self) -> None:
        """Test code block with custom language."""
        result = code_block("console.log('hi')", "javascript")
        assert result == "```javascript\nconsole.log('hi')\n```"


class TestRenderMessageHeader:
    """Tests for the render_message_header function."""

    def test_user_header(self) -> None:
        """Test rendering user header."""
        headers = AuthorHeaders()
        assert render_message_header("user", headers) == "# Me"

    def test_assistant_header(self) -> None:
        """Test rendering assistant header."""
        headers = AuthorHeaders()
        assert render_message_header("assistant", headers) == "# ChatGPT"

    def test_custom_header(self) -> None:
        """Test rendering with custom headers."""
        headers = AuthorHeaders(user="## Human")
        assert render_message_header("user", headers) == "## Human"


class TestRenderYamlHeader:
    """Tests for the render_yaml_header function."""

    def test_all_fields_enabled(self, mock_conversation: Conversation) -> None:
        """Test YAML header with all fields enabled."""
        config = YAMLConfig()
        yaml = render_yaml_header(mock_conversation, config)
        assert "---" in yaml
        assert "title: conversation 111" in yaml
        assert "chat_link:" in yaml

    def test_minimal_fields(self, mock_conversation: Conversation) -> None:
        """Test YAML header with minimal fields."""
        config = YAMLConfig(
            title=True,
            tags=False,
            chat_link=False,
            create_time=False,
            update_time=False,
            model=False,
            used_plugins=False,
            message_count=False,
            content_types=False,
            custom_instructions=False,
        )
        yaml = render_yaml_header(mock_conversation, config)
        assert "title:" in yaml
        assert "chat_link:" not in yaml

    def test_no_fields(self, mock_conversation: Conversation) -> None:
        """Test YAML header with no fields enabled."""
        config = YAMLConfig(
            title=False,
            tags=False,
            chat_link=False,
            create_time=False,
            update_time=False,
            model=False,
            used_plugins=False,
            message_count=False,
            content_types=False,
            custom_instructions=False,
        )
        yaml = render_yaml_header(mock_conversation, config)
        assert yaml == ""


class TestRenderConversation:
    """Tests for the render_conversation function."""

    def test_render_conversation_basic(self, mock_conversation: Conversation) -> None:
        """Test basic conversation rendering."""
        config = ConversationConfig()
        headers = AuthorHeaders()
        markdown = render_conversation(mock_conversation, config, headers)

        assert "---" in markdown
        assert "# Me" in markdown
        assert "user message 111" in markdown
        assert "# ChatGPT" in markdown
        assert "assistant message 111" in markdown

    def test_render_conversation_with_images(self, mock_conversation: Conversation) -> None:
        """Test conversation rendering with image assets."""
        config = ConversationConfig()
        headers = AuthorHeaders()

        # Mock an image in the message
        mock_conversation.all_message_nodes[0].message.content.parts = [
            {"content_type": "image_asset_pointer", "asset_pointer": "file-service://file-123"}
        ]

        def mock_resolver(asset_id: str) -> str | None:
            if asset_id == "file-123":
                return "assets/file-123.png"
            return None

        markdown = render_conversation(
            mock_conversation, config, headers, asset_resolver=mock_resolver
        )

        assert "![Image](assets/file-123.png)" in markdown
