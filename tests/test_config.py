"""Tests for the config module."""

from pathlib import Path

from convoviz.config import (
    AuthorHeaders,
    ConversationConfig,
    ConvovizConfig,
    GraphConfig,
    MarkdownConfig,
    MessageConfig,
    WordCloudConfig,
    YAMLConfig,
    get_default_config,
)


def test_get_default_config() -> None:
    """Test that get_default_config returns a valid config."""
    config = get_default_config()
    assert isinstance(config, ConvovizConfig)
    assert config.input_path is None
    assert isinstance(config.output_folder, Path)


def test_author_headers_defaults() -> None:
    """Test AuthorHeaders default values."""
    headers = AuthorHeaders()
    assert headers.system == "### System"
    assert headers.user == "# Me"
    assert headers.assistant == "# ChatGPT"
    assert headers.tool == "### Tool output"


def test_author_headers_custom() -> None:
    """Test AuthorHeaders with custom values."""
    headers = AuthorHeaders(user="## User", assistant="## AI")
    assert headers.user == "## User"
    assert headers.assistant == "## AI"


def test_yaml_config_defaults() -> None:
    """Test YAMLConfig default values."""
    yaml = YAMLConfig()
    assert yaml.title is True
    assert yaml.tags is False
    assert yaml.chat_link is True


def test_markdown_config_defaults() -> None:
    """Test MarkdownConfig default values."""
    md = MarkdownConfig()
    assert md.latex_delimiters == "default"


def test_wordcloud_config_defaults() -> None:
    """Test WordCloudConfig default values."""
    wc = WordCloudConfig()
    assert wc.colormap == "magma"
    assert wc.width == 1000
    assert wc.height == 1000
    assert wc.mode == "RGBA"


def test_convoviz_config_nested() -> None:
    """Test that ConvovizConfig properly nests configs."""
    config = ConvovizConfig()
    assert isinstance(config.message, MessageConfig)
    assert isinstance(config.conversation, ConversationConfig)
    assert isinstance(config.wordcloud, WordCloudConfig)
    assert isinstance(config.graph, GraphConfig)


def test_config_is_mutable() -> None:
    """Test that config values can be changed."""
    config = get_default_config()
    config.wordcloud.colormap = "viridis"
    assert config.wordcloud.colormap == "viridis"


def test_config_independence() -> None:
    """Test that get_default_config returns independent instances."""
    config1 = get_default_config()
    config2 = get_default_config()
    config1.wordcloud.colormap = "plasma"
    assert config2.wordcloud.colormap == "magma"
