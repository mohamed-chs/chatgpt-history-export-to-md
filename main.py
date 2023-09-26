"""main module

Todo:
    - Better command line output formatting
    - Configs from the command line
    - Link to submit issues or feedback
"""

import json
import os
import pathlib
from collections import defaultdict
from typing import Any

import questionary

from src.message_processing import format_message_as_md
from src.metadata_extraction import extract_metadata, save_conversation_to_md
from src.utils import extract_zip, format_title, get_most_recent_zip, sanitize_title


def get_absolute_path(path: str, home_directory: str) -> str:
    """Convert a potentially relative path to an absolute path, relative to the home directory.

    Args:
        path (str): The input path (either relative or absolute).
        home_directory (str): The home directory path.

    Returns:
        str: The absolute path.
    """

    if path.startswith(("~", home_directory)):
        path = os.path.expanduser(path)
    elif path.startswith(("/", "\\")):
        path = path[1:]

    if not os.path.isabs(path):
        path = os.path.join(home_directory, path)
    return os.path.abspath(path)


def get_sanitized_and_sorted_messages(conversation: dict[str, Any]) -> tuple[str, str]:
    """Sanitize and sort messages from the conversation.

    Args:
        conversation (dict): The conversation data.

    Returns:
        tuple[str, str]: The sanitized title and the formatted conversation text.
    """

    title: str = sanitize_title(conversation["title"])
    sorted_messages: list[Any] = sorted(
        conversation["mapping"].items(),
        key=lambda x: 0
        if not x[1]["message"] or x[1]["message"].get("create_time") is None
        else x[1]["message"]["create_time"],
    )
    conversation_text: str = "".join(
        [format_message_as_md(value.get("message", {})) for _, value in sorted_messages]
    )
    return title, conversation_text


def process_conversation(
    conversation: dict[str, Any], title_occurrences: defaultdict[str, int], path: str
) -> None:
    """Process a single conversation and save it to a Markdown file.

    Args:
        conversation (dict): The conversation data.
        title_occurrences (defaultdict[str, int]): Tracks the occurrences of each title.
        path (str): The output path.
    """

    title, conversation_text = get_sanitized_and_sorted_messages(conversation)
    metadata: dict[str, Any] = extract_metadata(conversation)
    save_conversation_to_md(title, conversation_text, title_occurrences, path, metadata)


# default values
HOME: str = os.path.expanduser("~")

default_out_folder: str = os.path.join(HOME, "Documents", "ChatGPT-Conversations", "MD")
default_zip_file: str = get_most_recent_zip()


def main():
    """Main processing function.

    Args:
        out_folder (str): The output folder path.
        zip_file (str): The ZIP file path.
    """

    out_folder: str = questionary.text(
        "Enter the path to the Markdown output folder :", default=default_out_folder
    ).ask()

    out_folder = get_absolute_path(out_folder, HOME)

    zip_file: str = questionary.text(
        "Enter the path to the exported ZIP file :", default_zip_file
    ).ask()

    zip_file = get_absolute_path(zip_file, HOME)

    if not os.path.isfile(zip_file):
        print(f"ZIP file not found: {zip_file}. Ensure the file exists.")
        return

    extract_zip(zip_file)

    json_filepath: str = os.path.join(
        os.path.splitext(zip_file)[0], "conversations.json"
    )
    if not os.path.isfile(json_filepath):
        print(
            f"Expected JSON file not found: {json_filepath}. Check the contents of the ZIP file."
        )
        return

    os.makedirs(out_folder, exist_ok=True)
    print(f"Writing MD files in : '{out_folder}' ...")

    try:
        with open(json_filepath, "r", encoding="utf-8") as file:
            conversations = json.load(file)
    except json.JSONDecodeError:
        print(f"Error decoding JSON from {json_filepath}.")
        return
    except IOError as error:
        print(f"I/O error reading {json_filepath}: {error}")
        return

    title_occurrences: defaultdict[str, int] = defaultdict(int)
    total_conversations: int = len(conversations)

    for i, conversation in enumerate(conversations):
        title: str = get_sanitized_and_sorted_messages(conversation)[0]
        title = format_title(title)
        process_conversation(conversation, title_occurrences, out_folder)

        print(f"\n\x1b[KProcessing chat: {title}", end="", flush=True)
        print(
            f"\x1b[A\rProcessed {i+1}/{total_conversations} conversations",
            end="",
            flush=True,
        )

    print(
        "\r\n\r\nProcessing completed 🎉.",
        end="\n\n",
        flush=True,
    )

    path = pathlib.Path(out_folder).resolve()

    uri = path.as_uri()

    print(f"Check the output here : {uri}")


if __name__ == "__main__":
    main()
