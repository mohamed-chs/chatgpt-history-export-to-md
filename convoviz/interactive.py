"""Module for handling interactive user configuration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from questionary import (
    Choice,
    Style,
    checkbox,
    select,
)
from questionary import (
    path as qst_path,
)
from questionary import (
    text as qst_text,
)

from .config import DEFAULT_USER_CONFIGS, AllConfigs
from .utils import (
    colormaps,
    font_names,
    font_path,
    stem,
    validate_header,
    validate_zip,
)

if TYPE_CHECKING:
    pass

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
    ],
)


def run_interactive_config(current_configs: AllConfigs | None = None) -> AllConfigs:
    """Prompt the user for input and return updated configs."""
    # Start with defaults or provided configs
    if current_configs is None:
        # We need a deep copy of defaults to avoid mutating the original
        # Since AllConfigs is a TypedDict (dict), simple copy might be shallow for nested dicts
        # constructing it explicitly is safer or using deepcopy
        from copy import deepcopy
        configs = deepcopy(DEFAULT_USER_CONFIGS)
    else:
        from copy import deepcopy
        configs = deepcopy(current_configs)

    # Note: DEFAULT_USER_CONFIGS has empty strings for paths in config.py
    # We should probably set sensible defaults here if they are empty,
    # or let the prompt show empty.
    # The original utils had dynamic defaults.

    from .utils import latest_zip, default_font_path

    if not configs["zip_filepath"]:
         try:
             configs["zip_filepath"] = str(latest_zip())
         except FileNotFoundError:
             pass 
    
    if not configs["wordcloud"]["font_path"]:
        configs["wordcloud"]["font_path"] = str(default_font_path())


    configs["zip_filepath"] = qst_path(
        "Enter the path to the zip file :",
        configs["zip_filepath"],
        validate=validate_zip,
        style=CUSTOM_STYLE,
    ).ask()

    configs["output_folder"] = qst_path(
        "Enter the path to the output folder :",
        configs["output_folder"],
        style=CUSTOM_STYLE,
    ).ask()

    for author_role in configs["message"]["author_headers"]:
        configs["message"]["author_headers"][author_role] = qst_text(  # type: ignore[literal-required]
            f"Enter the message header (#) for messages from '{author_role}' :",
            configs["message"]["author_headers"][author_role],  # type: ignore[literal-required]
            validate=validate_header,
            style=CUSTOM_STYLE,
        ).ask()

    configs["conversation"]["markdown"]["latex_delimiters"] = select(
        "Select the LaTeX math delimiters you want to use :",
        ["default", "dollars"],
        configs["conversation"]["markdown"]["latex_delimiters"],
        style=CUSTOM_STYLE,
    ).ask()

    yaml_choices = [
        Choice(title=header, checked=bool(value))
        for header, value in configs["conversation"]["yaml"].items()
    ]

    selected_headers = checkbox(
        "Select the YAML metadata headers you want to include :",
        yaml_choices,
        style=CUSTOM_STYLE,
    ).ask()

    for header in configs["conversation"]["yaml"]:
        configs["conversation"]["yaml"][header] = header in selected_headers  # type: ignore[literal-required]

    current_font_stem = stem(configs["wordcloud"].get("font_path") or "")
    # handle case where font path might be empty or invalid
    if not current_font_stem:
        current_font_stem = stem(str(default_font_path()))

    font_name: str = select(
        "Select the font you want to use for the word clouds :",
        font_names(),
        current_font_stem,
        style=CUSTOM_STYLE,
    ).ask()

    configs["wordcloud"]["font_path"] = str(font_path(font_name))

    configs["wordcloud"]["colormap"] = select(
        "Select the color theme you want to use for the word clouds :",
        colormaps(),
        configs["wordcloud"].get("colormap"),
        style=CUSTOM_STYLE,
    ).ask()

    configs["wordcloud"]["custom_stopwords"] = qst_text(
        "Enter custom stopwords (separated by commas) :",
        configs["wordcloud"].get("custom_stopwords", ""),
        style=CUSTOM_STYLE,
    ).ask()

    return configs
