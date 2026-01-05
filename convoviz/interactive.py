"""Interactive configuration prompts using questionary."""

from pathlib import Path

from questionary import Choice, Style, checkbox, select
from questionary import path as qst_path
from questionary import text as qst_text

from convoviz.config import ConvovizConfig, get_default_config
from convoviz.io.loaders import find_latest_zip, validate_zip
from convoviz.utils import colormaps, default_font_path, font_names, font_path, validate_header

CUSTOM_STYLE = Style(
    [
        ("qmark", "fg:#34eb9b bold"),
        ("question", "bold fg:#e0e0e0"),
        ("answer", "fg:#34ebeb bold"),
        ("pointer", "fg:#e834eb bold"),
        ("highlighted", "fg:#349ceb bold"),
        ("selected", "fg:#34ebeb"),
        ("separator", "fg:#eb3434"),
        ("instruction", "fg:#eb9434"),
        ("text", "fg:#b2eb34"),
        ("disabled", "fg:#858585 italic"),
    ]
)


def run_interactive_config(initial_config: ConvovizConfig | None = None) -> ConvovizConfig:
    """Run interactive prompts to configure convoviz.

    Args:
        initial_config: Optional starting configuration (uses defaults if None)

    Returns:
        Updated configuration based on user input
    """
    config = initial_config or get_default_config()

    # Set sensible defaults if not already set
    if not config.zip_filepath:
        latest = find_latest_zip()
        if latest:
            config.zip_filepath = latest

    if not config.wordcloud.font_path:
        config.wordcloud.font_path = default_font_path()

    # Prompt for zip file path
    zip_default = str(config.zip_filepath) if config.zip_filepath else ""
    zip_result = qst_path(
        "Enter the path to the zip file:",
        default=zip_default,
        validate=lambda p: validate_zip(Path(p))
        or "Invalid zip file (must contain conversations.json)",
        style=CUSTOM_STYLE,
    ).ask()

    if zip_result:
        config.zip_filepath = Path(zip_result)

    # Prompt for output folder
    output_result = qst_path(
        "Enter the path to the output folder:",
        default=str(config.output_folder),
        style=CUSTOM_STYLE,
    ).ask()

    if output_result:
        config.output_folder = Path(output_result)

    # Prompt for author headers
    headers = config.message.author_headers
    for role in ["system", "user", "assistant", "tool"]:
        current = getattr(headers, role)
        result = qst_text(
            f"Enter the message header for '{role}':",
            default=current,
            validate=lambda t: validate_header(t)
            or "Must be a valid markdown header (e.g., # Title)",
            style=CUSTOM_STYLE,
        ).ask()
        if result:
            setattr(headers, role, result)

    # Prompt for LaTeX delimiters
    latex_result = select(
        "Select the LaTeX math delimiters:",
        choices=["default", "dollars"],
        default=config.conversation.markdown.latex_delimiters,
        style=CUSTOM_STYLE,
    ).ask()

    if latex_result:
        config.conversation.markdown.latex_delimiters = latex_result

    # Prompt for YAML headers
    yaml_config = config.conversation.yaml
    yaml_choices = [
        Choice(title=field, checked=getattr(yaml_config, field))
        for field in [
            "title",
            "tags",
            "chat_link",
            "create_time",
            "update_time",
            "model",
            "used_plugins",
            "message_count",
            "content_types",
            "custom_instructions",
        ]
    ]

    selected = checkbox(
        "Select YAML metadata headers to include:",
        choices=yaml_choices,
        style=CUSTOM_STYLE,
    ).ask()

    if selected is not None:
        selected_set = set(selected)
        for field_name in [
            "title",
            "tags",
            "chat_link",
            "create_time",
            "update_time",
            "model",
            "used_plugins",
            "message_count",
            "content_types",
            "custom_instructions",
        ]:
            setattr(yaml_config, field_name, field_name in selected_set)

    # Prompt for font
    available_fonts = font_names()
    if available_fonts:
        current_font = (
            config.wordcloud.font_path.stem if config.wordcloud.font_path else available_fonts[0]
        )
        font_result = select(
            "Select the font for word clouds:",
            choices=available_fonts,
            default=current_font if current_font in available_fonts else available_fonts[0],
            style=CUSTOM_STYLE,
        ).ask()

        if font_result:
            config.wordcloud.font_path = font_path(font_result)

    # Prompt for colormap
    available_colormaps = colormaps()
    if available_colormaps:
        colormap_result = select(
            "Select the color theme for word clouds:",
            choices=available_colormaps,
            default=config.wordcloud.colormap
            if config.wordcloud.colormap in available_colormaps
            else available_colormaps[0],
            style=CUSTOM_STYLE,
        ).ask()

        if colormap_result:
            config.wordcloud.colormap = colormap_result

    # Prompt for custom stopwords
    stopwords_result = qst_text(
        "Enter custom stopwords (comma-separated):",
        default=config.wordcloud.custom_stopwords,
        style=CUSTOM_STYLE,
    ).ask()

    if stopwords_result is not None:
        config.wordcloud.custom_stopwords = stopwords_result

    return config
