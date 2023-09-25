"""main module

Functions:
    - get_absolute_path(path: str, home_directory: str) -> str:
        Convert a relative path to an absolute path based on the home directory.
    
    - parse_arguments() -> argparse.Namespace:
        Parse the command-line arguments and return them as an argparse.Namespace object.

    - get_sanitized_and_sorted_messages(conversation: dict[str, Any]) -> tuple[str, str]:
        Retrieve sanitized titles and sorted messages from the given conversation.

    - process_conversation(
        conversation: dict[str, Any], title_occurrences: defaultdict[str, int], path: str
        ) -> None:
        Handle a single conversation and save its content as an MD file.

    - main(out_folder: str, zip_file: str) -> None:
        The main processing function, orchestrating the extraction and saving processes.

Attributes:
    ARGS (argparse.Namespace): Parsed command-line arguments.

Todo:
    - Better command line output formatting
    - Configs from the command line
    - Link to submit issues or feedback
"""

import argparse
import json
import os
import pathlib
from collections import defaultdict
from typing import Any

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


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns:
        argparse.Namespace: Parsed arguments.
    """

    parser = argparse.ArgumentParser(description="Process some JSON files.")
    home_directory: str = os.path.expanduser("~")

    default_out_folder: str = os.path.join(
        home_directory, "Documents", "ChatGPT-Conversations", "MD"
    )
    default_zip_file: str | None = get_most_recent_zip()

    parser.add_argument(
        "--out_folder",
        help="The path to the output folder.",
        default=default_out_folder,
    )
    parser.add_argument(
        "--zip_file",
        help="The path to the exported ZIP file.",
        default=default_zip_file,
    )

    args = parser.parse_args()
    args.out_folder = get_absolute_path(args.out_folder, home_directory)
    args.zip_file = get_absolute_path(args.zip_file, home_directory)

    return args


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


def main(out_folder: str, zip_file: str) -> None:
    """Main processing function.

    Args:
        out_folder (str): The output folder path.
        zip_file (str): The ZIP file path.
    """

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
    ARGS = parse_arguments()
    main(ARGS.out_folder, ARGS.zip_file)
