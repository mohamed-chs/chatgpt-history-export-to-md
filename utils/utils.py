"""Utility functions for the project."""

import re
from pathlib import Path
from zipfile import ZipFile


def ensure_closed_code_blocks(string: str) -> str:
    """Ensure that all code blocks are closed."""
    # A code block can be opened with triple backticks, possibly followed by a language name.
    # It can only be closed however with triple backticks, with nothing else on the line.

    open_code_block = False

    lines = string.split("\n")

    for line in lines:
        if line.startswith("```") and not open_code_block:
            open_code_block = True
            continue

        if line == "```" and open_code_block:
            open_code_block = False

    if open_code_block:
        string += "\n```"

    return string


def replace_latex_delimiters(string: str) -> str:
    """Replace all the LaTeX bracket delimiters in the string with dollar sign ones."""

    string = re.sub(r"\\\[", "$$", string)
    string = re.sub(r"\\\]", "$$", string)
    string = re.sub(r"\\\(", "$", string)
    string = re.sub(r"\\\)", "$", string)

    return string


def get_font_names() -> list[str]:
    """Returns a list of all the font names in the assets/fonts folder."""

    fonts_path = Path("assets/fonts")
    font_names = [font.stem for font in fonts_path.iterdir() if font.is_file()]
    return font_names


def get_colormap_names() -> list[str]:
    """Returns a list of all the colormap names in the assets/colormaps.txt file."""

    colormaps_path = Path("assets/colormaps.txt")

    with open(colormaps_path, "r", encoding="utf-8") as file:
        colormaps_list = file.read().splitlines()

    return colormaps_list


def validate_zip_file(path_str: str) -> bool:
    """Returns True if the given path is a zip file with a 'conversations.json' file."""

    if not Path(path_str).is_file() or Path(path_str).suffix != ".zip":
        return False
    with ZipFile(path_str) as zip_ref:
        if "conversations.json" not in zip_ref.namelist():
            return False
    return True
