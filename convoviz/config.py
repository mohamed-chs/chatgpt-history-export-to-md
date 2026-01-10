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
    flavor: Literal["obsidian", "standard"] = "standard"


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
    colormap: str = "RdYlBu"
    custom_stopwords: str = "use, file, "
    exclude_programming_keywords: bool = True
    background_color: str | None = None
    mode: Literal["RGB", "RGBA"] = "RGBA"
    include_numbers: bool = False
    width: int = 600
    height: int = 600


class GraphConfig(BaseModel):
    """Configuration for graph generation."""

    color: str = "#4A90E2"
    grid: bool = True
    show_counts: bool = True
    font_name: str = "Montserrat-Regular.ttf"
    figsize: tuple[int, int] = (10, 6)
    dpi: int = 300
    timezone: Literal["utc", "local"] = "local"
    generate_monthly_breakdowns: bool = False
    generate_yearly_breakdowns: bool = False


class ConvovizConfig(BaseModel):
    """Main configuration for convoviz."""

    input_path: Path | None = None
    output_folder: Path = Field(default_factory=lambda: Path.home() / "Documents" / "ChatGPT-Data")
    message: MessageConfig = Field(default_factory=MessageConfig)
    conversation: ConversationConfig = Field(default_factory=ConversationConfig)
    wordcloud: WordCloudConfig = Field(default_factory=WordCloudConfig)
    graph: GraphConfig = Field(default_factory=GraphConfig)

    model_config = {"validate_default": True}


# Default configuration instance
def get_default_config() -> ConvovizConfig:
    """Get a fresh default configuration instance."""
    return ConvovizConfig()
