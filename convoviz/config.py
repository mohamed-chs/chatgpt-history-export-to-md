"""Configuration models using Pydantic v2."""

from __future__ import annotations

import tomllib
from enum import StrEnum
from functools import lru_cache
from importlib import resources
from pathlib import Path
from typing import Annotated, Any, Literal

from platformdirs import user_config_path
from pydantic import BaseModel, BeforeValidator, Field, field_validator

from convoviz.exceptions import ConfigurationError
from convoviz.utils import deep_merge_dicts, normalize_optional_path


def _coerce_none(v: Any) -> Any:
    if isinstance(v, str) and not v.strip():
        return None
    return v


# Annotated types for reusable validation
NormalizedPath = Annotated[Path | None, BeforeValidator(normalize_optional_path)]
OptionalString = Annotated[str | None, BeforeValidator(_coerce_none)]
OptionalInt = Annotated[int | None, BeforeValidator(_coerce_none)]

DEFAULT_CONFIG_RESOURCE = "assets/default_config.toml"


class FolderOrganization(StrEnum):
    """How to organize markdown output files in folders."""

    FLAT = "flat"  # All files in one directory
    DATE = "date"  # Nested by year/month (default)


class OutputKind(StrEnum):
    """Types of outputs that can be generated."""

    MARKDOWN = "markdown"  # Conversation markdown files
    GRAPHS = "graphs"  # Usage analytics graphs
    WORDCLOUDS = "wordclouds"  # Word cloud visualizations


# Default: generate all outputs
ALL_OUTPUTS: frozenset[OutputKind] = frozenset(OutputKind)


class AuthorHeaders(BaseModel):
    """Headers for different message authors in markdown output."""

    system: str = "### System"
    user: str = "# Me"
    assistant: str = "# ChatGPT"
    tool: str = "### Tool output"


class MarkdownConfig(BaseModel):
    """Configuration for markdown output."""

    latex_delimiters: Literal["default", "dollars"] = "dollars"
    flavor: Literal["standard", "obsidian"] = "standard"
    show_timestamp: bool = True
    render_order: Literal["active", "full"] = "active"


class YAMLConfig(BaseModel):
    """Configuration for YAML frontmatter in markdown files."""

    title: bool = True
    aliases: bool = True
    tags: bool = False
    chat_link: bool = True
    create_time: bool = True
    update_time: bool = True
    custom_instructions: bool = False
    model: bool = True
    used_plugins: bool = False
    message_count: bool = True
    content_types: bool = False
    is_starred: bool = False
    voice: bool = False
    conversation_id: bool = True


class ConversationConfig(BaseModel):
    """Configuration for conversation rendering."""

    markdown: MarkdownConfig = Field(default_factory=MarkdownConfig)
    yaml: YAMLConfig = Field(default_factory=YAMLConfig)


class MessageConfig(BaseModel):
    """Configuration for message rendering."""

    author_headers: AuthorHeaders = Field(default_factory=AuthorHeaders)


class WordCloudConfig(BaseModel):
    """Configuration for word cloud generation."""

    font_path: NormalizedPath = None
    colormap: str = "RdYlBu"
    custom_stopwords: str = "use, file"
    exclude_programming_keywords: bool = True
    include_assistant_text: bool = True
    background_color: OptionalString = None
    mode: Literal["RGB", "RGBA"] = "RGBA"
    include_numbers: bool = False
    width: int = 600
    height: int = 600
    max_workers: OptionalInt = None  # None = use half CPU count
    random_state: OptionalInt = 42  # None = non-deterministic layouts


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

    input_path: NormalizedPath = None
    bookmarklet_path: NormalizedPath = None
    output_folder: Path = Field(
        default_factory=lambda: Path.home() / "Documents" / "ChatGPT-Data"
    )
    quiet: bool = False
    folder_organization: FolderOrganization = FolderOrganization.DATE
    outputs: set[OutputKind] = Field(default_factory=lambda: set(ALL_OUTPUTS))
    prepend_timestamp_to_filename: bool = False

    # Export flags
    export_canvas: bool = True
    export_custom_instructions: bool = True

    message: MessageConfig = Field(default_factory=MessageConfig)
    conversation: ConversationConfig = Field(default_factory=ConversationConfig)
    wordcloud: WordCloudConfig = Field(default_factory=WordCloudConfig)
    graph: GraphConfig = Field(default_factory=GraphConfig)

    model_config = {"validate_default": True}

    @field_validator("output_folder", mode="before")
    @classmethod
    def _validate_output_folder(cls, v: Any) -> Path:
        norm = normalize_optional_path(v)
        if norm is None:
            # Fallback to default if somehow set to empty
            return Path.home() / "Documents" / "ChatGPT-Data"
        return norm


def _read_default_config_text() -> str:
    resource = resources.files("convoviz").joinpath(DEFAULT_CONFIG_RESOURCE)
    with resources.as_file(resource) as path:
        return path.read_text(encoding="utf-8")


def _load_toml_bytes(data: bytes) -> dict[str, Any]:
    try:
        return tomllib.loads(data.decode("utf-8"))
    except (tomllib.TOMLDecodeError, UnicodeDecodeError) as exc:
        raise ConfigurationError("Failed to parse TOML configuration.") from exc


def _load_toml_path(path: Path) -> dict[str, Any]:
    try:
        with path.open("rb") as handle:
            return tomllib.load(handle)
    except FileNotFoundError as exc:
        msg = f"Configuration file not found: {path}"
        raise ConfigurationError(msg) from exc
    except tomllib.TOMLDecodeError as exc:
        msg = f"Failed to parse TOML configuration: {path}"
        raise ConfigurationError(msg) from exc


@lru_cache(maxsize=1)
def get_default_config_text() -> str:
    """Return the default TOML configuration text bundled with the package."""
    return _read_default_config_text()


@lru_cache(maxsize=1)
def get_default_config_data() -> dict[str, Any]:
    """Return the default configuration data loaded from TOML."""
    return _load_toml_bytes(get_default_config_text().encode("utf-8"))


def get_default_config() -> ConvovizConfig:
    """Get a fresh default configuration instance."""
    return ConvovizConfig.model_validate(get_default_config_data())


def get_user_config_path() -> Path:
    """Return the OS-native user configuration path for convoviz."""
    return user_config_path("convoviz", ensure_exists=False) / "config.toml"


def load_config_from_path(path: Path) -> ConvovizConfig:
    """Load configuration from a TOML file, merged over defaults."""
    default_data = get_default_config_data()
    user_data = _load_toml_path(path)
    merged = deep_merge_dicts(default_data, user_data)
    return ConvovizConfig.model_validate(merged)


def load_config(config_path: Path | None = None) -> ConvovizConfig:
    """Load configuration from a path or the user config if it exists."""
    if config_path is not None:
        return load_config_from_path(config_path)

    user_path = get_user_config_path()
    if user_path.exists():
        return load_config_from_path(user_path)

    return get_default_config()


def write_default_config(path: Path, overwrite: bool = False) -> Path:
    """Write the bundled default configuration to the provided path."""
    if path.exists() and not overwrite:
        msg = f"Configuration file already exists: {path}"
        raise ConfigurationError(msg)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(get_default_config_text(), encoding="utf-8")
    return path
