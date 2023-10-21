"""Utility functions for the project."""

from __future__ import annotations

from pathlib import Path
from re import sub as re_sub
from zipfile import ZipFile


def ensure_closed_code_blocks(string: str) -> str:
    """Ensure that all code blocks are closed."""
    # A code block can be opened with triple backticks, possibly followed by a lang name
    # It can only be closed however with triple backticks, with nothing else on the line

    open_code_block = False

    lines: list[str] = string.split(sep="\n")

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
    string = re_sub(pattern=r"\\\[", repl="$$", string=string)
    string = re_sub(pattern=r"\\\]", repl="$$", string=string)
    string = re_sub(pattern=r"\\\(", repl="$", string=string)

    return re_sub(pattern=r"\\\)", repl="$", string=string)


def get_font_names() -> list[str]:
    """Return a list of all the font names in the assets/fonts folder."""
    return [font.stem for font in Path("assets/fonts").iterdir()]


def get_colormap_names() -> list[str]:
    """Return a list of all the colormap names in the assets/colormaps.txt file."""
    with Path("assets/colormaps.txt").open(encoding="utf-8") as file:
        return file.read().splitlines()


def validate_zip_file(path_str: str) -> bool:
    """Return True if the given path is a zip file with a 'conversations.json' file."""
    if not Path(path_str).is_file() or Path(path_str).suffix != ".zip":
        return False
    with ZipFile(file=path_str) as zip_ref:
        if "conversations.json" not in zip_ref.namelist():
            return False
    return True
