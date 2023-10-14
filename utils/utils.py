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


def default_output_folder() -> str:
    """Returns the default output folder path.

    (put the function in a separate file to isolate file system operations)"""

    return str(Path.home() / "Documents" / "ChatGPT Data")


def get_openai_zip_filepath() -> str:
    """Returns the path to the most recent zip file in the Downloads folder,
    excluding those containing 'bookmarklet'."""

    downloads_folder = Path.home() / "Downloads"

    # Filter out zip files with names that contain "bookmarklet"
    zip_files = [
        x for x in downloads_folder.glob("*.zip") if "bookmarklet" not in x.name
    ]

    if not zip_files:
        return ""

    # Most recent zip file in downloads folder, excluding those containing "bookmarklet"
    default_zip_filepath: Path = max(zip_files, key=lambda x: x.stat().st_ctime)

    return str(default_zip_filepath)


def get_bookmarklet_json_filepath() -> Path | None:
    """Returns the path to the most recent json file in the Downloads folder,
    containing 'bookmarklet'."""

    downloads_folder = Path.home() / "Downloads"

    # Filter out json files with names that do not contain "bookmarklet"
    bookmarklet_json_files = [
        x for x in downloads_folder.glob("*.json") if "bookmarklet" in x.name
    ]

    if not bookmarklet_json_files:
        return None

    # Most recent json file in downloads folder, containing "bookmarklet"
    bookmarklet_json_filepath: Path = max(
        bookmarklet_json_files, key=lambda x: x.stat().st_ctime
    )

    return bookmarklet_json_filepath
