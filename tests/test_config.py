"""Tests for the config module."""

from pathlib import Path

from convoviz.config import (
    ALL_OUTPUTS,
    AuthorHeaders,
    ConversationConfig,
    ConvovizConfig,
    GraphConfig,
    MarkdownConfig,
    MessageConfig,
    OutputKind,
    PandocPdfConfig,
    WordCloudConfig,
    YAMLConfig,
    get_default_config,
    load_config_from_path,
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
    assert yaml.aliases is True
    assert yaml.tags is False
    assert yaml.chat_link is True


def test_markdown_config_defaults() -> None:
    """Test MarkdownConfig default values."""
    md = MarkdownConfig()
    assert md.latex_delimiters == "dollars"


def test_pandoc_pdf_config_defaults() -> None:
    """Test PandocPdfConfig default values."""
    pdf = PandocPdfConfig()
    assert pdf.enabled is True


def test_wordcloud_config_defaults() -> None:
    """Test WordCloudConfig default values."""
    wc = WordCloudConfig()
    assert wc.colormap == "RdYlBu"
    assert wc.width == 600
    assert wc.height == 600
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
    assert config2.wordcloud.colormap == "RdYlBu"


def test_output_kind_enum() -> None:
    """Test OutputKind enum values."""
    assert OutputKind.MARKDOWN.value == "markdown"
    assert OutputKind.GRAPHS.value == "graphs"
    assert OutputKind.WORDCLOUDS.value == "wordclouds"


def test_all_outputs_constant() -> None:
    """Test ALL_OUTPUTS contains all output kinds."""
    assert frozenset({OutputKind.MARKDOWN, OutputKind.GRAPHS, OutputKind.WORDCLOUDS}) == ALL_OUTPUTS


def test_default_outputs() -> None:
    """Test that default config includes all outputs."""
    config = get_default_config()
    assert config.outputs == {OutputKind.MARKDOWN, OutputKind.GRAPHS, OutputKind.WORDCLOUDS}


def test_outputs_can_be_modified() -> None:
    """Test that outputs can be modified."""
    config = get_default_config()
    config.outputs = {OutputKind.MARKDOWN}
    assert config.outputs == {OutputKind.MARKDOWN}


def test_load_config_from_path_overrides_defaults(tmp_path: Path) -> None:
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        """
folder_organization = "flat"
outputs = ["markdown"]

[wordcloud]
colormap = "viridis"
font_path = ""
""".strip(),
        encoding="utf-8",
    )

    config = load_config_from_path(config_path)
    assert config.folder_organization.value == "flat"
    assert config.outputs == {OutputKind.MARKDOWN}
    assert config.wordcloud.colormap == "viridis"
    assert config.wordcloud.font_path is None
