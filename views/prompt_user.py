"""Module for the questionary user interface."""

from typing import Any, Dict

import questionary

from utils.utils import get_colormap_names, get_font_names, validate_zip_file

CUSTOM_STYLE = questionary.Style(
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


# --------------------- validators ---------------------


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

    font_names = get_font_names()

    user_configs["wordcloud"]["font"] = questionary.select(
        "Select the font you want to use for the word clouds :",
        choices=font_names,
        default=default_configs["wordcloud"]["font"]
        if default_configs["wordcloud"]["font"]
        else None,
        style=CUSTOM_STYLE,
    ).ask()

    colormaps_list = get_colormap_names()

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
