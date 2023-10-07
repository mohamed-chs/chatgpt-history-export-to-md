"""Utility functions for the project."""

import re


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
