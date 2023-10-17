"""Module for various processes that are used in the controllers.

Should ideally be the only module that deals with the filesystem.

(besides utils.py, but that doesn't save anything to disk,
and configuration.py, but that's a placeholder for user input in whatever form,
may be replaced later, with a GUI or something)"""

from datetime import datetime
from json import dump, load
from os import utime
from pathlib import Path
from typing import Any
from zipfile import ZipFile

from tqdm import tqdm

from models.conversation import Conversation
from models.conversation_set import ConversationSet

from .data_analysis import wordcloud_from_conversation_set


def load_conversations_from_openai_zip(zip_filepath: Path) -> ConversationSet:
    """Load the conversations from the OpenAI zip export file."""

    with ZipFile(file=zip_filepath, mode="r") as file:
        file.extractall(path=zip_filepath.with_suffix(suffix=""))

    conversations_path: Path = (
        zip_filepath.with_suffix(suffix="") / "conversations.json"
    )

    with open(file=conversations_path, mode="r", encoding="utf-8") as file:
        conversations = load(fp=file)

    return ConversationSet(conversations=conversations)


def load_conversations_from_bookmarklet_json(json_filepath: Path) -> ConversationSet:
    """Load the conversations from the bookmarklet json export file."""

    with open(file=json_filepath, mode="r", encoding="utf-8") as file:
        conversations = load(fp=file)

    return ConversationSet(conversations=conversations)


def save_conversation_to_file(conversation: Conversation, filepath: Path) -> None:
    """Save a conversation to a file, with added modification time."""
    base_file_name: str = filepath.stem

    counter = 0
    while filepath.exists():
        counter += 1
        filepath = filepath.with_name(
            name=f"{base_file_name} ({counter}){filepath.suffix}"
        )

    with open(file=filepath, mode="w", encoding="utf-8") as file:
        file.write(conversation.to_markdown())
    utime(path=filepath, times=(conversation.update_time, conversation.update_time))


def save_conversation_set_to_dir(conv_set: ConversationSet, dir_path: Path) -> None:
    """Save a conversation set to a directory, one markdown file per conversation."""
    for conversation in tqdm(
        iterable=conv_set.conversation_list, desc="Writing Markdown 📄 files"
    ):
        file_path: Path = dir_path / f"{conversation.sanitized_title()}.md"
        save_conversation_to_file(conversation=conversation, filepath=file_path)


def save_wordcloud_from_conversation_set(
    conv_set: ConversationSet,
    dir_path: Path,
    time_period: tuple[datetime, str],
    **kwargs: Any,
) -> None:
    """Create the wordclouds and save them to the folder."""
    match time_period[1]:
        case "week":
            file_name: str = f"{time_period[0].strftime('%Y week %W')}.png"
        case "month":
            file_name = f"{time_period[0].strftime('%Y %B')}.png"
        case "year":
            file_name = f"{time_period[0].strftime('%Y')}.png"
        case _:
            raise ValueError("Invalid time period for wordcloud")

    wordcloud_from_conversation_set(conv_set=conv_set, **kwargs).to_file(  # type: ignore
        filename=dir_path / file_name
    )


def generate_all_wordclouds(
    conv_set: ConversationSet, dir_path: Path, **kwargs: Any
) -> None:
    """Create the wordclouds and save them to the folder."""

    weeks_dict: dict[datetime, ConversationSet] = conv_set.grouped_by_week()
    months_dict: dict[datetime, ConversationSet] = conv_set.grouped_by_month()
    years_dict: dict[datetime, ConversationSet] = conv_set.grouped_by_year()

    for week in tqdm(
        iterable=weeks_dict.keys(), desc="Creating weekly wordclouds 🔡☁️ "
    ):
        save_wordcloud_from_conversation_set(
            conv_set=weeks_dict[week],
            dir_path=dir_path,
            time_period=(week, "week"),
            **kwargs,
        )

    for month in tqdm(
        iterable=months_dict.keys(), desc="Creating monthly wordclouds 🔡☁️ "
    ):
        save_wordcloud_from_conversation_set(
            conv_set=months_dict[month],
            dir_path=dir_path,
            time_period=(month, "month"),
            **kwargs,
        )

    for year in tqdm(
        iterable=years_dict.keys(), desc="Creating yearly wordclouds 🔡☁️ "
    ):
        save_wordcloud_from_conversation_set(
            conv_set=years_dict[year],
            dir_path=dir_path,
            time_period=(year, "year"),
            **kwargs,
        )


def save_custom_instructions_to_file(conv_set: ConversationSet, filepath: Path) -> None:
    """Create JSON file for custom instructions in the conversation set."""

    with open(file=filepath, mode="w", encoding="utf-8") as file:
        dump(obj=conv_set.all_custom_instructions(), fp=file, indent=2)


def default_output_folder() -> str:
    """Returns the default output folder path.

    (put the function in a separate file to isolate file system operations)"""

    return str(object=Path.home() / "Documents" / "ChatGPT Data")


def get_openai_zip_filepath() -> str:
    """Returns the path to the most recent zip file in the Downloads folder,
    excluding those containing 'bookmarklet'."""

    downloads_folder: Path = Path.home() / "Downloads"

    # Filter out zip files with names that contain "bookmarklet"
    zip_files: list[Path] = [
        x for x in downloads_folder.glob(pattern="*.zip") if "bookmarklet" not in x.name
    ]

    if not zip_files:
        return ""

    # Most recent zip file in downloads folder, excluding those containing "bookmarklet"
    default_zip_filepath: Path = max(zip_files, key=lambda x: x.stat().st_ctime)

    return str(object=default_zip_filepath)


def get_bookmarklet_json_filepath() -> Path | None:
    """Returns the path to the most recent json file in the Downloads folder,
    containing 'bookmarklet'."""

    downloads_folder: Path = Path.home() / "Downloads"

    # Filter out json files with names that do not contain "bookmarklet"
    bookmarklet_json_files: list[Path] = [
        x for x in downloads_folder.glob(pattern="*.json") if "bookmarklet" in x.name
    ]

    if not bookmarklet_json_files:
        return None

    # Most recent json file in downloads folder, containing "bookmarklet"
    bookmarklet_json_filepath: Path = max(
        bookmarklet_json_files, key=lambda x: x.stat().st_ctime
    )

    return bookmarklet_json_filepath
