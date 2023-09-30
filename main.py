"""main module

Todo:
    - Better command line output formatting
    - Configs from the command line
    - Link to submit issues or feedback
"""

import calendar
import datetime
import json
import os
import pathlib
import re
from collections import defaultdict
from typing import Any, Dict, List, Tuple

import questionary

from src.custom_json_files import create_custom_instructions_json
from src.data_visualization import create_graph, create_wordcloud
from src.message_processing import format_message_as_md
from src.metadata_extraction import extract_metadata, save_conversation_to_md
from src.utils import extract_zip, format_title, get_most_recent_zip

# Load the configuration JSON file
with open("config.json", encoding="utf-8") as c_file:
    config = json.load(c_file)

# Pre-compiled pattern for disallowed characters in file names
PATTERN = re.compile(r'[<>:"/\\|?*\n\r\t\f\v]')

# default values
HOME: str = os.path.expanduser("~")

default_out_folder: str = os.path.join(HOME, "Documents", "My ChatGPT Data")
default_zip_file: str = get_most_recent_zip()

# Get the current date
now = datetime.datetime.now()

# Extract the month and year
current_month_name = calendar.month_name[now.month]
current_year = now.year


def get_absolute_path(path: str) -> str:
    """Convert a potentially relative path to an absolute path, relative to the home directory.

    Args:
        path (str): The input path (either relative or absolute).

    Returns:
        str: The absolute path.
    """

    if path.startswith(("~", HOME)):
        path = os.path.expanduser(path)
    elif path.startswith(("/", "\\")):
        path = path[1:]

    if not os.path.isabs(path):
        path = os.path.join(HOME, path)
    return os.path.abspath(path)


def get_sanitized_and_sorted_messages(conversation: Dict[str, Any]) -> Tuple[str, str]:
    """Sanitize and sort messages from the conversation.

    Args:
        conversation (dict): The conversation data.

    Returns:
        tuple[str, str]: The sanitized title and the formatted conversation text.
    """

    title: str = PATTERN.sub("-", conversation.get("title", "Untitled").strip())
    sorted_messages: List[Any] = sorted(
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
    conversation: Dict[str, Any], title_occurrences: defaultdict[str, int], path: str
) -> None:
    """Process a single conversation and save it to a Markdown file.

    Args:
        conversation (dict): The conversation data.
        title_occurrences (defaultdict[str, int]): Tracks the occurrences of each title.
        path (str): The output path.
    """

    title, conversation_text = get_sanitized_and_sorted_messages(conversation)
    metadata: Dict[str, Any] = extract_metadata(conversation)
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


def main():
    """Main processing function.

    Args:
        out_folder (str): The output folder path.
        zip_file (str): The ZIP file path.
    """

    out_folder: str = questionary.text(
        "Enter the path to the output folder :", default=default_out_folder
    ).ask()

    out_folder = get_absolute_path(out_folder)

    os.makedirs(out_folder, exist_ok=True)

    zip_file: str = questionary.text(
        "Enter the path to the exported ZIP file :", default_zip_file
    ).ask()

    zip_file = get_absolute_path(zip_file)

    extract_zip(zip_file)

    if not os.path.isfile(zip_file):
        print(f"ZIP file not found: '{zip_file}'. Ensure the file exists.")
        return

    json_filepath: str = os.path.join(
        os.path.splitext(zip_file)[0], "conversations.json"
    )
    if not os.path.isfile(json_filepath):
        print(
            f"Expected JSON file not found: '{json_filepath}'. Check the contents of the ZIP file."
        )
        return

    # generating custom instructions.json file

    print("Writing 'custom_instructions.json' file...\n")

    deduplication_mode = config["deduplication_mode"] = questionary.select(
        "Select which custom instructions to keep in this JSON file (in case of duplicates) :",
        choices=["all", "latest", "earliest"],
        default=config["deduplication_mode"],
    ).ask()

    create_custom_instructions_json(json_filepath, out_folder, deduplication_mode)

    # generating markdown files

    want_markdown = config["want_markdown"] = questionary.confirm(
        "Do you want to generate markdown files ?", default=config["want_markdown"]
    ).ask()

    if want_markdown:
        # Roles Configuration
        print("Configuring message headers:")

        config["roles"]["system_title"] = questionary.text(
            "System message header:", default=config["roles"]["system_title"]
        ).ask()

        config["roles"]["user_title"] = questionary.text(
            "User message header:", default=config["roles"]["user_title"]
        ).ask()

        config["roles"]["assistant_title"] = questionary.text(
            "Assistant message header:", default=config["roles"]["assistant_title"]
        ).ask()

        config["roles"]["tool_title"] = questionary.text(
            "Tool message header:", default=config["roles"]["tool_title"]
        ).ask()

        # Delimiters Configuration
        config["delimiters_default"] = questionary.confirm(
            "Use default LaTeX delimiters?", default=config["delimiters_default"]
        ).ask()

        # YAML Headers Configuration
        print("Configuring YAML headers:")

        # Create choices with pre-selected items based on the config
        choices = [
            questionary.Choice(header, checked=value)
            for header, value in config["yaml_headers"].items()
        ]

        selected_headers = questionary.checkbox(
            "Select the headers you want to include:",
            choices=choices,
        ).ask()

        # Process the selected headers to update the config
        for header in config["yaml_headers"].keys():
            config["yaml_headers"][header] = header in selected_headers

        try:
            with open(json_filepath, "r", encoding="utf-8") as file:
                conversations = json.load(file)
        except json.JSONDecodeError:
            print(f"Error decoding JSON from '{json_filepath}'.")
            return
        except IOError as error:
            print(f"I/O error reading '{json_filepath}': {error}")
            return

        title_occurrences: defaultdict[str, int] = defaultdict(int)
        total_conversations: int = len(conversations)

        markdown_path = os.path.join(out_folder, "Markdown")
        os.makedirs(markdown_path, exist_ok=True)

        print(f"Writing MD files in :\n'{markdown_path}' ...\n")

        for i, conversation in enumerate(conversations):
            title: str = get_sanitized_and_sorted_messages(conversation)[0]
            title = format_title(title)
            process_conversation(conversation, title_occurrences, markdown_path)

            print(f"\n\x1b[KProcessing chat: '{title}'", end="", flush=True)
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

    # creating prompts per day graph

    create_graph(json_filepath, out_folder)

    # create wordcloud

    want_wordclouds = config["want_wordclouds"] = questionary.confirm(
        "Do you want a word cloud ?", default=config["want_wordclouds"]
    ).ask()

    def get_font_path(font_name: str):
        return f"assets/fonts/{font_name}.ttf"

    fonts = os.listdir("assets/fonts")
    fonts = [os.path.splitext(font)[0] for font in fonts]

    with open("assets/colormaps.txt", "r", encoding="utf-8") as file:
        colormaps = file.read().splitlines()

    if want_wordclouds:
        font = config["data_viz"]["wordclouds"]["font"] = questionary.select(
            "Select a font for the word cloud :",
            choices=fonts,
            default=config["data_viz"]["wordclouds"]["font"],
        ).ask()

        font_path = get_font_path(font)

        colormap = config["data_viz"]["wordclouds"]["colormap"] = questionary.select(
            "Select a color theme for the word cloud :",
            choices=colormaps,
            default=config["data_viz"]["wordclouds"]["colormap"],
        ).ask()

        month_names = list(calendar.month_name)[1:]

        all_months = config["data_viz"]["wordclouds"][
            "all_months"
        ] = questionary.confirm(
            "One word cloud for each month ? (This may take a while. Otherwise, specify the start and end months.))",
            default=config["data_viz"]["wordclouds"]["all_months"],
        ).ask()

        if all_months:
            for i in range(len(month_names) - 1):
                create_wordcloud(
                    json_filepath,
                    out_folder,
                    "user",
                    font_path,
                    colormap,
                    month_names[i],
                    month_names[i + 1],
                )
                if month_names[i] == current_month_name:
                    break

        else:
            start_month = config["data_viz"]["wordclouds"][
                "start_month"
            ] = questionary.select(
                "Select a start month for the word cloud :",
                choices=month_names,
                default=config["data_viz"]["wordclouds"]["start_month"],
            ).ask()

            end_month = config["data_viz"]["wordclouds"][
                "end_month"
            ] = questionary.select(
                "Select an end month for the word cloud :",
                choices=month_names,
                default=config["data_viz"]["wordclouds"]["end_month"],
            ).ask()

            create_wordcloud(
                json_filepath,
                out_folder,
                "user",
                font_path,
                colormap,
                start_month,
                end_month,
            )

    # Save updated configuration
    with open("config.json", "w", encoding="utf-8") as a_file:
        json.dump(config, a_file, indent=2)

    print("Configuration has been updated and saved to 'config.json'.\n")

    path = pathlib.Path(out_folder).resolve()

    uri = path.as_uri()

    print(f"Check the output here : {uri}.\n")


if __name__ == "__main__":
    print(
        "Welcome to ChatGPT Data Visualizer ✨📊!\nFollow the instructions in the command line.\nPress 'ENTER' to select the default options.\n\n"
    )
    main()
