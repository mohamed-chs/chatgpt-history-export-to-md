# utils.py

import os
import re
import datetime
import zipfile
from glob import glob
import sys

# Checking Python version
if sys.version_info[0] < 3:
    raise Exception("Python 3 or a more recent version is required.")

# Pre-compiled pattern for disallowed characters
DISALLOWED_CHARS_PATTERN = re.compile(r'[<>:"/\\|?*\n\r\t\f\v]')


def extract_zip(zip_filepath):
    """Extract the conversation data from the exported ZIP file."""
    try:
        extract_folder = os.path.splitext(os.path.abspath(zip_filepath))[0]

        with zipfile.ZipFile(zip_filepath, "r") as zip_ref:
            zip_ref.extractall(extract_folder)
            print(f"Successfully extracted ZIP file to '{extract_folder}'")
    except Exception as e:
        print(f"An error occurred while extracting the ZIP file: {e}")


def get_most_recent_zip():
    """Get the most recent ZIP file from the '~/Downloads' directory."""
    try:
        from pathlib import Path

        downloads_path = str(Path.home() / "Downloads")

        if not os.path.isdir(downloads_path):
            raise FileNotFoundError(
                f"'Downloads' directory not found: {downloads_path}"
            )

        zip_files = glob(os.path.join(downloads_path, "*.zip"))

        if not zip_files:
            raise FileNotFoundError("No ZIP files found in the 'Downloads' directory.")

        return max(zip_files, key=os.path.getctime)
    except Exception as e:
        print(f"An error occurred while looking for the ZIP file: {e}")
        return None


def sanitize_title(title):
    """Sanitize the title by replacing disallowed characters with '-'."""
    sanitized_title = DISALLOWED_CHARS_PATTERN.sub("-", title.strip())
    return sanitized_title


def timestamp_to_str(timestamp):
    """Convert a Unix timestamp to a formatted string."""
    try:
        dt_object = datetime.datetime.utcfromtimestamp(timestamp)
        formatted_timestamp = dt_object.strftime("%d %b %Y, %H:%M:%S")
        return formatted_timestamp
    except ValueError as e:
        print(f"Invalid timestamp value: {e}")
        return None


def format_title(title, max_length=50):
    """Formats the title to a single line with a maximum length."""
    single_line_title = " ".join(title.splitlines())
    return (
        single_line_title[:max_length] + "..."
        if len(single_line_title) > max_length
        else single_line_title
    )
