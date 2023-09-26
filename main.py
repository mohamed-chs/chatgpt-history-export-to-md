"""main module

Todo:
    - Better command line output formatting
    - Configs from the command line
    - Link to submit issues or feedback
"""

import json
import os
import pathlib
import re
from collections import defaultdict
from random import randint
from typing import Any

import questionary

from src.message_processing import format_message_as_md
from src.metadata_extraction import extract_metadata, save_conversation_to_md
from src.utils import extract_zip, format_title, get_most_recent_zip
from src.data_visualization import create_wordcloud

# Load the configuration JSON file
with open("config.json", encoding="utf-8") as c_file:
    config = json.load(c_file)

# Pre-compiled pattern for disallowed characters in file names
PATTERN = re.compile(r'[<>:"/\\|?*\n\r\t\f\v]')


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

    title: str = PATTERN.sub("-", conversation.get("title", "Untitled").strip())
    sorted_messages: list[Any] = sorted(
        conversation["mapping"].items(),
        key=lambda x: 0
        if not x[1]["message"] or x[1]["message"].get("create_time") is None
        else x[1]["message"]["create_time"],
    )
    conversation_text: str = "".join(
        [
            format_message_as_md(value.get("message", {}), config["roles"])
            for _, value in sorted_messages
        ]
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
    delimiters = config["delimiters_default"]
    yaml_config = config["yaml_headers"]
    save_conversation_to_md(
        title,
        conversation_text,
        title_occurrences,
        path,
        metadata,
        delimiters,
        yaml_config,
    )


# default values
HOME: str = os.path.expanduser("~")

default_out_folder: str = os.path.join(HOME, "Documents", "ChatGPT-Conversations")
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

    ### COMMAND LINE CONFIGURATIONS -------------

    # Roles Configuration
    print("Configuring roles titles:")
    config["roles"]["system_title"] = questionary.text(
        "System Title:", default=config["roles"]["system_title"]
    ).ask()
    config["roles"]["user_title"] = questionary.text(
        "User Title:", default=config["roles"]["user_title"]
    ).ask()
    config["roles"]["assistant_title"] = questionary.text(
        "Assistant Title:", default=config["roles"]["assistant_title"]
    ).ask()
    config["roles"]["tool_title"] = questionary.text(
        "Tool Title:", default=config["roles"]["tool_title"]
    ).ask()

    # Delimiters Configuration
    config["delimiters_default"] = questionary.confirm(
        "Use default delimiters?", default=config["delimiters_default"]
    ).ask()

    # YAML Headers Configuration
    print("Configuring YAML headers:")

    selected_headers = questionary.checkbox(
        "Select the headers you want to include:",
        choices=list(config["yaml_headers"].keys()),
    ).ask()

    for header in config["yaml_headers"].keys():
        config["yaml_headers"][header] = header in selected_headers

    # # Data Visualizations Configuration
    # # Assuming that data visualizations are a dictionary with boolean values
    # print("Configuring Data Visualizations:")
    # for viz, value in config["data_visualizations"].items():
    #     config["data_visualizations"][viz] = questionary.confirm(
    #         f"Enable {viz}?", default=value
    #     ).ask()

    # Save updated configuration
    with open("config.json", "w", encoding="utf-8") as a_file:
        json.dump(config, a_file, indent=2)

    print("Configuration has been updated and saved to 'config.json'")

    ### -------------------------------

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

    # create wordcloud

    want_wordcloud = questionary.confirm("Do you want a word cloud ?").ask()

    if want_wordcloud:
        font_number = int(
            questionary.text(
                "Pick a font number from 1 to 41 (or surprise me -->", default=str(randint(0, 40))
            ).ask()
        )
        
        colormap_number = int(
            questionary.text(
                "Pick a colormap number from 1 to 44 (or surprise me -->", default=str(randint(0, 43))
            ).ask()
        )

        create_wordcloud(json_filepath, out_folder, "user", font_number, colormap_number)

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

    markdown_path = os.path.join(out_folder, "Markdown")

    print(f"Writing MD files in : '{markdown_path}' ...")

    for i, conversation in enumerate(conversations):
        title: str = get_sanitized_and_sorted_messages(conversation)[0]
        title = format_title(title)
        os.makedirs(markdown_path, exist_ok=True)
        process_conversation(conversation, title_occurrences, markdown_path)

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
