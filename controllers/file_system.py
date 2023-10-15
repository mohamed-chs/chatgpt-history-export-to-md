"""Module for various processes that are used in the controllers.

Should ideally be the only module that deals with the filesystem.

(besides utils.py, but that doesn't save anything to disk,
and configuration.py, but that's a placeholder for user input in whatever form,
may be replaced later, with a GUI or something)"""


import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any
from zipfile import ZipFile

from tqdm import tqdm

from models.conversation import Conversation
from models.conversation_set import ConversationSet

from .data_analysis import wordcloud_from_conversation_set


def load_conversations_from_openai_zip(zip_filepath: Path) -> ConversationSet:
    """Load the conversations from the OpenAI zip export file."""

    with ZipFile(zip_filepath, "r") as file:
        file.extractall(zip_filepath.with_suffix(""))

    conversations_path = zip_filepath.with_suffix("") / "conversations.json"

    with open(conversations_path, "r", encoding="utf-8") as file:
        conversations = json.load(file)

    return ConversationSet(conversations)


def load_conversations_from_bookmarklet_json(json_filepath: Path) -> ConversationSet:
    """Load the conversations from the bookmarklet json export file."""

    with open(json_filepath, "r", encoding="utf-8") as file:
        conversations = json.load(file)

    return ConversationSet(conversations)


def save_conversation_to_file(conversation: Conversation, file_path: Path) -> None:
    """Save a conversation to a file, with added modification time."""
    base_file_name = file_path.stem

    counter = 0
    while file_path.exists():
        counter += 1
        file_path = file_path.with_name(
            f"{base_file_name} ({counter}){file_path.suffix}"
        )

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(conversation.to_markdown())
    os.utime(file_path, (conversation.update_time, conversation.update_time))


def save_conversation_set_to_dir(
    conversation_set: ConversationSet, dir_path: Path
) -> None:
    """Save a conversation set to a directory, one markdown file per conversation."""
    for conversation in tqdm(
        conversation_set.conversation_list, desc="Writing Markdown 📄 files"
    ):
        file_path = dir_path / f"{conversation.sanitized_title()}.md"
        save_conversation_to_file(conversation, file_path)


def save_wordcloud_from_conversation_set(
    conversation_set: ConversationSet,
    folder_path: Path,
    time_period: tuple[datetime, str],
    **kwargs: Any,
) -> None:
    """Create the wordclouds and save them to the folder."""
    match time_period[1]:
        case "week":
            file_name = f"{time_period[0].strftime('%Y week %W')}.png"
        case "month":
            file_name = f"{time_period[0].strftime('%Y %B')}.png"
        case "year":
            file_name = f"{time_period[0].strftime('%Y')}.png"
        case _:
            raise ValueError("Invalid time period for wordcloud")

    wordcloud_from_conversation_set(conversation_set, **kwargs).to_file(  # type: ignore
        folder_path / file_name
    )


def generate_all_wordclouds(
    conversation_set: ConversationSet, folder_path: Path, **kwargs: Any
) -> None:
    """Create the wordclouds and save them to the folder."""

    weeks_dict = conversation_set.grouped_by_week()
    months_dict = conversation_set.grouped_by_month()
    years_dict = conversation_set.grouped_by_year()

    for week in tqdm(weeks_dict.keys(), desc="Creating weekly wordclouds 🔡☁️ "):
        save_wordcloud_from_conversation_set(
            weeks_dict[week], folder_path, (week, "week"), **kwargs
        )

    for month in tqdm(months_dict.keys(), desc="Creating monthly wordclouds 🔡☁️ "):
        save_wordcloud_from_conversation_set(
            months_dict[month], folder_path, (month, "month"), **kwargs
        )

    for year in tqdm(years_dict.keys(), desc="Creating yearly wordclouds 🔡☁️ "):
        save_wordcloud_from_conversation_set(
            years_dict[year], folder_path, (year, "year"), **kwargs
        )


def save_custom_instructions_to_file(
    conversation_set: ConversationSet, file_path: Path
) -> None:
    """Create JSON file for custom instructions in the conversation set."""

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(conversation_set.all_custom_instructions(), file, indent=2)


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
