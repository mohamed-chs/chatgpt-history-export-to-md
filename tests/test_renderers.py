"""Tests for the renderers module."""

from datetime import datetime, timedelta

from convoviz.config import AuthorHeaders, ConversationConfig, YAMLConfig
from convoviz.models import Conversation, Node
from convoviz.renderers import render_conversation
from convoviz.renderers.markdown import (
    close_code_blocks,
    render_message_header,
    render_node,
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

    def test_closes_backtick_with_trailing_space(self) -> None:
        """Test closing fence with trailing whitespace."""
        text = "```python\ncode\n```   "
        assert close_code_blocks(text) == text

    def test_closes_backtick_with_language_on_close(self) -> None:
        """Test closing fence with language tag gets normalized."""
        text = "```python\ncode\n```python"
        assert close_code_blocks(text) == "```python\ncode\n```python\n```"

    def test_unclosed_tilde_block(self) -> None:
        """Test unclosed tilde block gets closed."""
        text = "~~~python\ncode"
        assert close_code_blocks(text) == "~~~python\ncode\n~~~"

    def test_tilde_block_closes_with_whitespace(self) -> None:
        """Test tilde closing fence with trailing whitespace."""
        text = "~~~\ncode\n~~~   "
        assert close_code_blocks(text) == text

    def test_inner_fence_ignored_while_open(self) -> None:
        """Test inner fences are ignored while a block is open."""
        text = "```python\ncode\n~~~js\nmore"
        assert close_code_blocks(text) == "```python\ncode\n~~~js\nmore\n```"


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

    def test_ignores_inline_code(self) -> None:
        """Test that inline code is left untouched."""
        text = r"Inline \(x\) and `\(literal\)`"
        assert replace_latex_delimiters(text) == "Inline $x$ and `\\(literal\\)`"

    def test_ignores_code_fence(self) -> None:
        """Test that fenced code blocks are left untouched."""
        text = '```python\nvalue = r"\\(x\\)"\n```\nOutside \\(y\\)'
        expected = '```python\nvalue = r"\\(x\\)"\n```\nOutside $y$'
        assert replace_latex_delimiters(text) == expected


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
        assert 'title: "conversation 111"' in yaml
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

    def test_tags_enabled(self, mock_conversation: Conversation) -> None:
        """Test YAML header includes tags when enabled."""
        config = YAMLConfig(
            title=False,
            tags=True,
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
        assert "tags:" in yaml
        assert '- "chatgpt"' in yaml

    def test_no_fields(self, mock_conversation: Conversation) -> None:
        """Test YAML header with no fields enabled."""
        config = YAMLConfig(
            title=False,
            aliases=False,
            tags=False,
            chat_link=False,
            create_time=False,
            update_time=False,
            model=False,
            used_plugins=False,
            message_count=False,
            content_types=False,
            custom_instructions=False,
            conversation_id=False,
        )
        yaml = render_yaml_header(mock_conversation, config)
        assert yaml == ""

    def test_title_sanitized_and_alias_added(self) -> None:
        """Test that title is sanitized and original appears in aliases."""
        conv = Conversation(
            title="My @Title: With/Chars",
            create_time=datetime(2026, 2, 3),
            update_time=datetime(2026, 2, 3),
            mapping={},
            current_node="node1",
            conversation_id="conv1",
        )
        config = YAMLConfig(title=True, aliases=True, chat_link=False)
        yaml = render_yaml_header(conv, config)
        assert 'title: "My Title With Chars"' in yaml
        assert "aliases:" in yaml
        assert '- "My @Title: With/Chars"' in yaml


class TestRenderConversation:
    """Tests for the render_conversation function."""

    def test_render_conversation_basic(self, mock_conversation: Conversation) -> None:
        """Test basic conversation rendering."""
        config = ConversationConfig()
        headers = AuthorHeaders()
        markdown = render_conversation(mock_conversation, config, headers)

        assert "***" in markdown
        assert "# Me" in markdown
        assert "user message 111" in markdown
        assert "# ChatGPT" in markdown
        assert "assistant message 111" in markdown

    def test_render_conversation_active_branch(
        self,
        branching_conversation: Conversation,
    ) -> None:
        """Test that active-branch rendering excludes alternate branches."""
        config = ConversationConfig()
        config.markdown.render_order = "active"
        headers = AuthorHeaders()

        markdown = render_conversation(branching_conversation, config, headers)

        assert "Hello, can you help?" in markdown
        assert "Sure thing! What do you need?" in markdown
        assert "Of course! How can I assist you?" not in markdown

    def test_render_conversation_full_branch(
        self,
        branching_conversation: Conversation,
    ) -> None:
        """Test that full DAG rendering includes alternate branches."""
        config = ConversationConfig()
        config.markdown.render_order = "full"
        headers = AuthorHeaders()

        markdown = render_conversation(branching_conversation, config, headers)

        assert "Hello, can you help?" in markdown
        assert "Sure thing! What do you need?" in markdown
        assert "Of course! How can I assist you?" in markdown

    def test_render_conversation_full_includes_orphans(self) -> None:
        """Test full DAG rendering includes disconnected/orphan nodes."""
        conv = Conversation(
            title="Orphan Test",
            create_time=datetime(2024, 1, 1),
            update_time=datetime(2024, 1, 1),
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
                        "create_time": datetime(2024, 1, 1).timestamp(),
                        "update_time": datetime(2024, 1, 1).timestamp(),
                        "content": {"content_type": "text", "parts": ["Hello"]},
                        "status": "finished_successfully",
                        "end_turn": True,
                        "weight": 1.0,
                        "metadata": {},
                        "recipient": "all",
                    },
                    "parent": "root",
                    "children": [],
                },
                "orphan": {
                    "id": "orphan",
                    "message": {
                        "id": "orphan",
                        "author": {"role": "assistant", "metadata": {}},
                        "create_time": datetime(2024, 1, 1).timestamp(),
                        "update_time": datetime(2024, 1, 1).timestamp(),
                        "content": {
                            "content_type": "text",
                            "parts": ["Orphan message"],
                        },
                        "status": "finished_successfully",
                        "end_turn": True,
                        "weight": 1.0,
                        "metadata": {},
                        "recipient": "all",
                    },
                    "parent": None,
                    "children": [],
                },
            },
            current_node="user_node",
            conversation_id="orphan_conv",
        )
        config = ConversationConfig()
        config.markdown.render_order = "full"
        headers = AuthorHeaders()

        markdown = render_conversation(conv, config, headers)

        assert "Orphan message" in markdown

    def test_render_conversation_with_images(
        self,
        mock_conversation: Conversation,
    ) -> None:
        """Test conversation rendering with image assets."""
        config = ConversationConfig()
        headers = AuthorHeaders()

        # Mock an image in the message (use a user node as system nodes are hidden by default)
        user_nodes = mock_conversation.nodes_by_author("user")
        user_nodes[0].message.content.parts = [
            {
                "content_type": "image_asset_pointer",
                "asset_pointer": "file-service://file-123",
            },
        ]

        def mock_resolver(asset_id: str, _name: str | None = None) -> str | None:
            if asset_id == "file-123":
                return "assets/file-123.png"
            return None

        markdown = render_conversation(
            mock_conversation,
            config,
            headers,
            asset_resolver=mock_resolver,
        )

        assert "![Image](assets/file-123.png)" in markdown

    def test_render_conversation_timestamps(
        self,
        mock_conversation: Conversation,
    ) -> None:
        """Test timestamp rendering in conversation."""
        config = ConversationConfig()
        headers = AuthorHeaders()
        markdown = render_conversation(mock_conversation, config, headers)

        # Messages in mock_conversation:
        # 1. System (hidden)
        # 2. User (2023-07-29 08:00:00)
        # 3. Assistant (2023-07-29 08:05:00)

        # First visible message (user) should have full date
        assert "*2023-07-29 08:00:00*" in markdown

        # Second visible message (assistant) on same day should only have time
        assert "*08:05:00*" in markdown
        # It should NOT have the full date again if it's the same day
        # But wait, our current mock has only one assistant message at 08:05:00.
        # Let's verify the string count.
        assert (
            markdown.count("2023-07-29") == 3
        )  # Twice in YAML (create/update), once in User message

    def test_render_conversation_no_timestamps(
        self,
        mock_conversation: Conversation,
    ) -> None:
        """Test that timestamps can be disabled."""
        config = ConversationConfig()
        config.markdown.show_timestamp = False
        headers = AuthorHeaders()
        markdown = render_conversation(mock_conversation, config, headers)

        assert "*2023-07-29 08:00:00*" not in markdown
        assert "*08:05:00*" not in markdown

    def test_render_conversation_date_change(
        self,
        mock_conversation: Conversation,
    ) -> None:
        """Test that full date is shown when it changes between messages."""
        # Modify assistant message to be on the next day
        assistant_node = mock_conversation.mapping["assistant_node_111"]
        original_ts = assistant_node.message.create_time
        next_day_ts = original_ts + timedelta(days=1)
        assistant_node.message.create_time = next_day_ts

        config = ConversationConfig()
        headers = AuthorHeaders()
        markdown = render_conversation(mock_conversation, config, headers)

        # User message
        assert "*2023-07-29 08:00:00*" in markdown
        # Assistant message (next day) should have full date
        expected_date = next_day_ts.strftime("%Y-%m-%d")
        assert f"*{expected_date} 08:05:00*" in markdown


def test_render_node_respects_explicit_empty_citation_map() -> None:
    """Passing an explicit empty citation map should disable embedded replacements."""
    marker = "\ue200cite\ue202turn0search0\ue201"
    node = Node(
        id="n1",
        message={
            "id": "m1",
            "author": {"role": "assistant", "metadata": {}},
            "create_time": datetime(2024, 1, 1).timestamp(),
            "update_time": datetime(2024, 1, 1).timestamp(),
            "content": {
                "content_type": "text",
                "parts": [
                    f"With marker {marker}",
                    {
                        "type": "search_result",
                        "ref_id": {
                            "ref_type": "search",
                            "turn_index": 0,
                            "ref_index": 0,
                        },
                        "title": "Source",
                        "url": "https://example.com",
                    },
                ],
            },
            "status": "finished_successfully",
            "end_turn": True,
            "weight": 1.0,
            "metadata": {},
            "recipient": "all",
        },
        parent=None,
        children=[],
    )

    rendered = render_node(node, AuthorHeaders(), citation_map={})
    assert marker in rendered
    assert "[Source](https://example.com)" not in rendered


def test_render_node_puts_citation_footnotes_at_message_bottom() -> None:
    """Citation references should render as footnotes below message content."""
    node = Node(
        id="n1",
        message={
            "id": "m1",
            "author": {"role": "assistant", "metadata": {}},
            "create_time": datetime(2024, 1, 1).timestamp(),
            "update_time": datetime(2024, 1, 1).timestamp(),
            "content": {
                "content_type": "text",
                "parts": ["Claim 【1†source】."],
            },
            "status": "finished_successfully",
            "end_turn": True,
            "weight": 1.0,
            "metadata": {
                "citations": [
                    {
                        "start_ix": 6,
                        "end_ix": 16,
                        "metadata": {
                            "title": "Source 1",
                            "url": "https://example.com/1",
                        },
                    }
                ]
            },
            "recipient": "all",
        },
        parent=None,
        children=[],
    )

    rendered = render_node(node, AuthorHeaders())
    assert "Claim [^1]." in rendered
    assert "[^1]: [Source 1](https://example.com/1)" in rendered
    assert rendered.index("[^1]: [Source 1](https://example.com/1)") > rendered.index(
        "Claim [^1]."
    )
