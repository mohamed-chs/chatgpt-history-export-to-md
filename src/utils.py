"""Utility Functions

Attributes:
    DISALLOWED_CHARS_PATTERN (Pattern): A pre-compiled regex pattern for
        detecting characters disallowed in file names.

Functions:
    extract_zip(zip_filepath: str) -> None:
        Extracts the specified ZIP file.

    get_most_recent_zip() -> Optional[str]:
        Fetches the path of the most recent ZIP file in the '~/Downloads' directory.

    sanitize_title(title: str) -> str:
        Sanitizes a title by replacing disallowed characters with '-'.

    timestamp_to_str(timestamp: float) -> Optional[str]:
        Converts a Unix timestamp to a formatted string.

    format_title(title: str, max_length: int = 50) -> str:
        Formats a title for better display in the terminal.

    replace_delimiters(file_name: str) -> None:
        Replaces LaTeX bracket delimiters in a Markdown file with dollar sign delimiters.

Raises:
    RuntimeError: If the Python version is below 3.10.

Todo:
    - Refactor the regex patterns for LaTeX delimiter replacements to account for nested delimiters.
"""

import datetime
import os
import re
import sys
import zipfile
from glob import glob
from pathlib import Path
from typing import Optional

# Checking Python version to ensure compatibility
# specifically for the new type hints syntax
if sys.version_info < (3, 10):
    raise RuntimeError("Python 3.10 or a more recent version is required.")

# Pre-compiled pattern for disallowed characters in file names
DISALLOWED_CHARS_PATTERN = re.compile(r'[<>:"/\\|?*\n\r\t\f\v]')


def extract_zip(zip_filepath: str) -> None:
    """Extract the contents of the specified ZIP file.

    Args:
        zip_filepath (str): The file path of the ZIP file to extract.
    """

    try:
        extract_folder: str = os.path.splitext(os.path.abspath(zip_filepath))[0]

        with zipfile.ZipFile(zip_filepath, "r") as zip_ref:
            zip_ref.extractall(extract_folder)
            print(f"Successfully extracted ZIP file to '{extract_folder}'")
    except zipfile.BadZipFile as error:
        print(f"The ZIP file is corrupted or invalid: {error}")
    except IOError as error:
        print(f"I/O error occurred while extracting the ZIP file: {error}")


def get_most_recent_zip() -> Optional[str]:
    """Get the most recent ZIP file from the '~/Downloads' directory.

    Raises:
        FileNotFoundError: If the 'Downloads' directory is not found.
        FileNotFoundError: If no ZIP files are found in the 'Downloads' directory.

    Returns:
        Optional[str]: Path to the most recent ZIP file in 'Downloads', or None
    """

    try:
        downloads_path = str(Path.home() / "Downloads")

        if not os.path.isdir(downloads_path):
            raise FileNotFoundError(
                f"'Downloads' directory not found: {downloads_path}"
            )

        zip_files: list[str] = glob(os.path.join(downloads_path, "*.zip"))

        if not zip_files:
            raise FileNotFoundError("No ZIP files found in the 'Downloads' directory.")

        return max(zip_files, key=os.path.getctime)
    except FileNotFoundError as error:
        print(f"An error occurred while looking for the ZIP file: {error}")
        return None


def sanitize_title(title: str) -> str:
    """Sanitize the title by replacing disallowed characters with '-'.

    Args:
        title (str): The title to sanitize.

    Returns:
        str: The sanitized title.
    """

    sanitized_title: str = DISALLOWED_CHARS_PATTERN.sub("-", title.strip())
    return sanitized_title


def timestamp_to_str(timestamp: float) -> Optional[str]:
    """Convert a Unix timestamp to a formatted string.

    Args:
        timestamp (float): The Unix timestamp to convert.

    Returns:
        Optional[str]: The formatted timestamp as a string, or None if the input is invalid.
    """

    try:
        dt_object = datetime.datetime.utcfromtimestamp(timestamp)
        formatted_timestamp: str = dt_object.strftime("%d %b %Y, %H:%M:%S")
        return formatted_timestamp
    except ValueError as error:
        print(f"Invalid timestamp value: {error}")
        return None


def format_title(title: str, max_length: int = 50) -> str:
    """Formats the title, for better printing the output in the terminal.

    Args:
        title (str): The title to format.
        max_length (int, optional): The maximum allowed length for the title. Defaults to 50.

    Returns:
        str: The formatted title.
    """

    single_line_title: str = " ".join(title.splitlines())
    return (
        single_line_title[:max_length] + "..."
        if len(single_line_title) > max_length
        else single_line_title
    )


def replace_delimiters(file_name: str) -> None:
    """Replace all the LaTeX bracket delimiters in the MD file with dollar sign ones.

    Args:
        file_name (str): The Markdown file to modify.
    """

    with open(file_name, "r", encoding="utf-8") as file:
        content: str = file.read()

        # Use regular expressions to replace delimiters
        # Be careful to ensure we don't match nested or broken delimiters.
        # Replace \[ ... \] first to avoid overlap with \( ... \)
        content = re.sub(r"\\\[", "$$", content)
        content = re.sub(r"\\\]", "$$", content)
        content = re.sub(r"\\\(", "$", content)
        content = re.sub(r"\\\)", "$", content)

    with open(file_name, "w", encoding="utf-8") as file:
        file.write(content)
