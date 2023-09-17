# main.py

import os
import json
import argparse
from collections import defaultdict
from src.utils import sanitize_title, extract_zip, get_most_recent_zip, format_title
from src.message_processing import format_message_as_md
from src.metadata_extraction import extract_metadata, save_conversation_to_md


def get_absolute_path(path, home_directory):
    """Convert a potentially relative path to an absolute path, relative to the home directory."""
    if path.startswith(("~", home_directory)):
        path = os.path.expanduser(path)
    elif path.startswith(("/", "\\")):
        path = path[1:]

    if not os.path.isabs(path):
        path = os.path.join(home_directory, path)
    return os.path.abspath(path)


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Process some JSON files.")

    home_directory = os.path.expanduser("~")
    default_out_folder = os.path.join(
        home_directory, "Documents", "ChatGPT-Conversations", "MD"
    )
    default_zip_file = get_most_recent_zip()

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


def get_sanitized_and_sorted_messages(conversation):
    """Sanitize and sort messages from the conversation."""
    title = sanitize_title(conversation["title"])
    sorted_messages = sorted(
        conversation["mapping"].items(),
        key=lambda x: 0
        if not x[1]["message"] or x[1]["message"].get("create_time") is None
        else x[1]["message"]["create_time"],
    )
    conversation_text = "".join(
        [
            format_message_as_md(value.get("message", {}))
            for key, value in sorted_messages
        ]
    )
    return title, conversation_text


def process_conversation(conversation, title_occurrences, path):
    """Process a single conversation."""
    title, conversation_text = get_sanitized_and_sorted_messages(conversation)
    metadata = extract_metadata(conversation)
    save_conversation_to_md(title, conversation_text, title_occurrences, path, metadata)


def main(out_folder, zip_file):
    """Main processing function."""
    if not os.path.isfile(zip_file):
        print(f"ZIP file not found: {zip_file}. Ensure the file exists.")
        return

    extract_zip(zip_file)

    json_filepath = os.path.join(os.path.splitext(zip_file)[0], "conversations.json")
    if not os.path.isfile(json_filepath):
        print(
            f"Expected JSON file not found: {json_filepath}. Check the contents of the ZIP file."
        )
        return

    os.makedirs(out_folder, exist_ok=True)
    print(f"Writing MD files in : '{out_folder}' ...")

    try:
        with open(json_filepath, "r") as file:
            conversations = json.load(file)
    except json.JSONDecodeError:
        print(f"Error decoding JSON from {json_filepath}.")
        return
    except Exception as e:
        print(f"Unexpected error reading {json_filepath}: {e}")
        return

    title_occurrences = defaultdict(int)
    total_conversations = len(conversations)
    for i, conversation in enumerate(conversations):
        title = get_sanitized_and_sorted_messages(conversation)[0]
        title = format_title(title)
        process_conversation(conversation, title_occurrences, out_folder)

        print(f"\n\x1b[KProcessing chat: {title}", end="", flush=True)
        print(
            f"\x1b[A\rProcessed {i+1}/{total_conversations} conversations",
            end="",
            flush=True,
        )

    print(
        f"\r\n\r\nProcessing completed.",
        end="\n\n",
        flush=True,
    )


if __name__ == "__main__":
    args = parse_arguments()
    main(args.out_folder, args.zip_file)
