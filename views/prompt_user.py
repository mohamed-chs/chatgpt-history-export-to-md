"""Module for the questionary user interface."""

from pathlib import Path
from typing import Any, Dict
from zipfile import ZipFile

import questionary

CUSTOM_STYLE = questionary.Style(
    [
        ("qmark", "fg:#1565C0"),  # Bright blue question mark
        ("question", "bold fg:#1E88E5"),  # Bold, even brighter blue question text
        ("answer", "fg:#BBDEFB"),  # Soft blue answer
        ("pointer", "fg:#0D47A1 bold"),  # Deep blue bold pointer for select
        (
            "selected",
            "bg:#0D47A1 fg:white",
        ),  # Deep blue background with white text for selected items
    ]
)

# --------------------- validators ---------------------


def validate_zip_file(path: str) -> bool:
    """Returns True if the given path is a zip file with a 'conversations.json' file."""

    if not Path(path).is_file() or Path(path).suffix != ".zip":
        return False
    with ZipFile(path) as zip_ref:
        if "conversations.json" not in zip_ref.namelist():
            return False
    return True


def validate_text(text: str) -> bool:
    """Returns True if the given text is not empty."""
    return len(text) > 0


def validate_header(text: str) -> bool:
    """Returns True if the given text is a valid markdown header."""
    return text.startswith("#")


def prompt_user(default_configs: Dict[str, Any]) -> Dict[str, Any]:
    """Prompts the user for input and returns the choices as a dictionary."""

    user_configs: Dict[str, Any] = {}

    # ------------------------ zip file and output folder ------------------------

    user_configs["zip_file"] = questionary.path(
        "Enter the path to the zip file :",
        default=default_configs["zip_file"],
        validate=validate_zip_file,
        style=CUSTOM_STYLE,
    ).ask()

    user_configs["output_folder"] = questionary.path(
        "Enter the path to the output folder :",
        default=default_configs["output_folder"],
        style=CUSTOM_STYLE,
    ).ask()

    # --------------------- message -----------------------

    user_configs["message"] = {}

    # ------------------------ author headers ------------------------

    user_configs["message"]["author_headers"] = {}

    for author_role in default_configs["message"]["author_headers"].keys():
        user_configs["message"]["author_headers"][author_role] = questionary.text(
            f"Enter the message header (#) for messages from '{author_role}' :",
            default=default_configs["message"]["author_headers"][author_role],
            validate=validate_header,
            style=CUSTOM_STYLE,
        ).ask()

    # ------------------ conversation ---------------------

    user_configs["conversation"] = {}

    # ------------------------ markdown ------------------------

    user_configs["conversation"]["markdown"] = {}

    user_configs["conversation"]["markdown"]["latex_delimiters"] = questionary.select(
        "Select the LaTeX math delimiters you want to use :",
        choices=["default", "dollar sign"],
        default=default_configs["conversation"]["markdown"]["latex_delimiters"],
        style=CUSTOM_STYLE,
    ).ask()

    # ------------------------ yaml header ------------------------

    user_configs["conversation"]["yaml"] = {}

    yaml_choices = [
        questionary.Choice(header, checked=value)
        for header, value in default_configs["conversation"]["yaml"].items()
    ]

    selected_headers = questionary.checkbox(
        "Select the YAML metadata headers you want to include :",
        choices=yaml_choices,
        style=CUSTOM_STYLE,
    ).ask()

    for header in default_configs["conversation"]["yaml"].keys():
        user_configs["conversation"]["yaml"][header] = header in selected_headers

    # ------------------------ word clouds ------------------------

    user_configs["wordcloud"] = {}

    fonts_path = Path("assets/fonts")

    fonts_list = [font.stem for font in fonts_path.iterdir() if font.is_file()]

    user_configs["wordcloud"]["font"] = questionary.select(
        "Select the font you want to use for the word clouds :",
        choices=fonts_list,
        default=default_configs["wordcloud"]["font"]
        if default_configs["wordcloud"]["font"]
        else None,
        style=CUSTOM_STYLE,
    ).ask()

    colormaps_path = Path("assets/colormaps.txt")

    with open(colormaps_path, "r", encoding="utf-8") as file2:
        colormaps_list = file2.read().splitlines()

    user_configs["wordcloud"]["colormap"] = questionary.select(
        "Select the color theme you want to use for the word clouds :",
        choices=colormaps_list,
        default=default_configs["wordcloud"]["colormap"]
        if default_configs["wordcloud"]["colormap"]
        else None,
        style=CUSTOM_STYLE,
    ).ask()

    # ------------------ node ---------------------

    user_configs["node"] = {}

    # -------------------- conversation list --------------------

    user_configs["conversation_list"] = {}

    # ------------- return -----------------

    return user_configs
