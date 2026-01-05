"""Configuration models using Pydantic v2."""

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field


class AuthorHeaders(BaseModel):
    """Headers for different message authors in markdown output."""

    system: str = "### System"
    user: str = "# Me"
    assistant: str = "# ChatGPT"
    tool: str = "### Tool output"


class MarkdownConfig(BaseModel):
    """Configuration for markdown output."""

    latex_delimiters: Literal["default", "dollars"] = "default"


class YAMLConfig(BaseModel):
    """Configuration for YAML frontmatter in markdown files."""

    title: bool = True
    tags: bool = False
    chat_link: bool = True
    create_time: bool = True
    update_time: bool = True
    model: bool = True
    used_plugins: bool = True
    message_count: bool = True
    content_types: bool = True
    custom_instructions: bool = True


class ConversationConfig(BaseModel):
    """Configuration for conversation rendering."""

    markdown: MarkdownConfig = Field(default_factory=MarkdownConfig)
    yaml: YAMLConfig = Field(default_factory=YAMLConfig)


class MessageConfig(BaseModel):
    """Configuration for message rendering."""

    author_headers: AuthorHeaders = Field(default_factory=AuthorHeaders)


class WordCloudConfig(BaseModel):
    """Configuration for word cloud generation."""

    font_path: Path | None = None
    colormap: str = "magma"
    custom_stopwords: str = "use, file, "
    background_color: str | None = None
    mode: Literal["RGB", "RGBA"] = "RGBA"
    include_numbers: bool = False
    width: int = 1000
    height: int = 1000


class GraphConfig(BaseModel):
    """Configuration for graph generation."""

    # Extensible for future graph options
    pass


class ConvovizConfig(BaseModel):
    """Main configuration for convoviz."""

    zip_filepath: Path | None = None
    output_folder: Path = Field(default_factory=lambda: Path.home() / "Documents" / "ChatGPT Data")
    message: MessageConfig = Field(default_factory=MessageConfig)
    conversation: ConversationConfig = Field(default_factory=ConversationConfig)
    wordcloud: WordCloudConfig = Field(default_factory=WordCloudConfig)
    graph: GraphConfig = Field(default_factory=GraphConfig)

    model_config = {"validate_default": True}


# Default configuration instance
def get_default_config() -> ConvovizConfig:
    """Get a fresh default configuration instance."""
    return ConvovizConfig()
