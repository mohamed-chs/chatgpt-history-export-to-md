"""Module for the questionary user interface."""


from pathlib import Path
from typing import Any, Dict
from zipfile import ZipFile

import questionary
from questionary import Style

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
    return len(text) > 0


def validate_header(text: str) -> bool:
    return text.startswith("#")


# --------------------- styles ---------------------

midnight_blue_style = Style(
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

sunset_glow_style = Style(
    [
        ("qmark", "fg:#D32F2F"),  # Fiery red question mark
        ("question", "bold fg:#F57C00"),  # Bold orange question text
        ("answer", "fg:#FFEB3B"),  # Bright yellow answer
        ("pointer", "fg:#C2185B bold"),  # Deep pink bold pointer for select
        (
            "selected",
            "bg:#C2185B fg:white",
        ),  # Deep pink background with white text for selected items
    ]
)

forest_walk_style = Style(
    [
        ("qmark", "fg:#2E7D32"),  # Dark green question mark
        ("question", "bold fg:#43A047"),  # Bold medium-green question text
        ("answer", "fg:#81C784"),  # Light green answer
        ("pointer", "fg:#1B5E20 bold"),  # Darker green bold pointer for select
        (
            "selected",
            "bg:#1B5E20 fg:white",
        ),  # Darker green background with white text for selected items
    ]
)

styles = {
    "midnight blue": midnight_blue_style,
    "sunset glow": sunset_glow_style,
    "forest walk": forest_walk_style,
}


def ask_questions(configs: Dict[str, Any]):
    """Prompts the user for input and saves the choices to the 'config' dictionary."""

    # style = questionary.select(
    #     "Select the color theme of this interface :",
    #     choices=[
    #         "midnight blue",
    #         "sunset glow",
    #         "forest walk",
    #     ],
    #     default="midnight blue",
    # ).ask()

    # ------------------------ zip file and output folder ------------------------

    configs["zip_file"] = questionary.path(
        "Enter the path to the zip file :",
        default=configs["zip_file"],
        validate=validate_zip_file,
        style=midnight_blue_style,
    ).ask()

    configs["output_folder"] = questionary.path(
        "Enter the path to the output folder :",
        default=configs["output_folder"],
        style=midnight_blue_style,
    ).ask()

    # ------------------------ author titles ------------------------

    for author_role in configs["conversation"]["message"]["author_headers"].keys():
        configs["conversation"]["message"]["author_headers"][
            author_role
        ] = questionary.text(
            f"Enter the message header (#) for messages from '{author_role}' :",
            default=configs["conversation"]["message"]["author_headers"][author_role],
            validate=validate_header,
            style=midnight_blue_style,
        ).ask()

    # ------------------------ markdown ------------------------

    configs["conversation"]["markdown"]["latex_delimiters"] = questionary.select(
        "Select the LaTeX math delimiters you want to use :",
        choices=["default", "dollar sign"],
        default=configs["conversation"]["markdown"]["latex_delimiters"],
        style=midnight_blue_style,
    ).ask()

    # ------------------------ yaml header ------------------------

    yaml_choices = [
        questionary.Choice(header, checked=value)
        for header, value in configs["conversation"]["yaml"].items()
    ]

    selected_headers = questionary.checkbox(
        "Select the YAML metadata headers you want to include :",
        choices=yaml_choices,
        style=midnight_blue_style,
    ).ask()

    for header in configs["conversation"]["yaml"].keys():
        configs["conversation"]["yaml"][header] = header in selected_headers

    # ------------------------ word clouds ------------------------

    fonts_path = Path("assets/fonts")

    fonts_list = [font.stem for font in fonts_path.iterdir() if font.is_file()]

    configs["wordcloud"]["font"] = questionary.select(
        "Select the font you want to use for the word clouds :",
        choices=fonts_list,
        default=configs["wordcloud"]["font"] if configs["wordcloud"]["font"] else None,
        style=midnight_blue_style,
    ).ask()

    colormaps_path = Path("assets/colormaps.txt")

    with open(colormaps_path, "r", encoding="utf-8") as file:
        colormaps_list = file.read().splitlines()

    configs["wordcloud"]["colormap"] = questionary.select(
        "Select the color theme you want to use for the word clouds :",
        choices=colormaps_list,
        default=configs["wordcloud"]["colormap"]
        if configs["wordcloud"]["colormap"]
        else None,
        style=midnight_blue_style,
    ).ask()

    # ------------------------ heatmaps ------------------------
