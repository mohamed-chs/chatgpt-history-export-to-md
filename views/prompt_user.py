"""Module for the questionary user interface."""

from typing import Any

from questionary import Choice, Style, checkbox, path, select, text

from utils.utils import get_colormap_names, get_font_names, validate_zip_file


def validate_header(string: str) -> bool:
    """Returns True if the given text is a valid markdown header."""
    return (
        1 <= string.count(x="#") <= 6
        and string.startswith("#")
        and string[len(string.split()[0])] == " "
    )


def prompt_user(default_configs: dict[str, Any]) -> dict[str, Any]:
    """Prompts the user for input and returns the choices as a dictionary."""
    custom_style = Style(
        style_rules=[
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

    user_configs: dict[str, Any] = {}

    # ------------------------ zip file and output folder ------------------------

    user_configs["zip_file"] = path(
        message="Enter the path to the zip file :",
        default=default_configs["zip_file"],
        validate=validate_zip_file,
        style=custom_style,
    ).ask()

    user_configs["output_folder"] = path(
        message="Enter the path to the output folder :",
        default=default_configs["output_folder"],
        style=custom_style,
    ).ask()

    # --------------------- message -----------------------

    user_configs["message"] = {}

    # ------------------------ author headers ------------------------

    user_configs["message"]["author_headers"] = {}

    for author_role in default_configs["message"]["author_headers"].keys():
        user_configs["message"]["author_headers"][author_role] = text(
            message=f"Enter the message header (#) for messages from '{author_role}' :",
            default=default_configs["message"]["author_headers"][author_role],
            validate=validate_header,
            style=custom_style,
        ).ask()

    # ------------------ conversation ---------------------

    user_configs["conversation"] = {}

    # ------------------------ markdown ------------------------

    user_configs["conversation"]["markdown"] = {}

    user_configs["conversation"]["markdown"]["latex_delimiters"] = select(
        message="Select the LaTeX math delimiters you want to use :",
        choices=["default", "dollar sign"],
        default=default_configs["conversation"]["markdown"]["latex_delimiters"],
        style=custom_style,
    ).ask()

    # ------------------------ yaml header ------------------------

    user_configs["conversation"]["yaml"] = {}

    yaml_choices: list[Choice] = [
        Choice(title=header, checked=value)
        for header, value in default_configs["conversation"]["yaml"].items()
    ]

    selected_headers = checkbox(
        message="Select the YAML metadata headers you want to include :",
        choices=yaml_choices,
        style=custom_style,
    ).ask()

    for header in default_configs["conversation"]["yaml"].keys():
        user_configs["conversation"]["yaml"][header] = header in selected_headers

    # ------------------------ word clouds ------------------------

    user_configs["wordcloud"] = {}

    font_names: list[str] = get_font_names()

    user_configs["wordcloud"]["font"] = select(
        message="Select the font you want to use for the word clouds :",
        choices=font_names,
        default=default_configs["wordcloud"]["font"]
        if default_configs["wordcloud"]["font"]
        else None,
        style=custom_style,
    ).ask()

    colormaps_list: list[str] = get_colormap_names()

    user_configs["wordcloud"]["colormap"] = select(
        message="Select the color theme you want to use for the word clouds :",
        choices=colormaps_list,
        default=default_configs["wordcloud"]["colormap"]
        if default_configs["wordcloud"]["colormap"]
        else None,
        style=custom_style,
    ).ask()

    # ------------------ node ---------------------

    user_configs["node"] = {}

    # -------------------- conversation set --------------------

    user_configs["conversation_set"] = {}

    # ------------- return -----------------

    return user_configs
