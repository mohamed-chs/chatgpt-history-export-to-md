"""Module for various processes that are used in the controllers.

Should ideally be the only module that deals with the filesystem."""


import json
import os
from pathlib import Path
from typing import Any
from zipfile import ZipFile

from tqdm import tqdm

from models.conversation import Conversation
from models.conversation_list import ConversationList

from .data_analysis import wordcloud_from_conversation_list


def load_conversations_from_zip(zip_filepath: Path) -> ConversationList:
    """Load the conversations from the zip file."""

    with ZipFile(zip_filepath, "r") as file:
        file.extractall(zip_filepath.with_suffix(""))

    conversations_path = zip_filepath.with_suffix("") / "conversations.json"

    with open(conversations_path, "r", encoding="utf-8") as file:
        conversations = json.load(file)

    return ConversationList(conversations)


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
        file.write(conversation.file_text_content())
    os.utime(file_path, (conversation.update_time, conversation.update_time))


def save_conversation_list_to_dir(
    conversation_list: ConversationList, dir_path: Path
) -> None:
    """Save a conversation list to a directory."""
    for conversation in tqdm(
        conversation_list.conversations, desc="Writing Markdown 📄 files"
    ):
        file_path = dir_path / f"{conversation.file_name()}.md"
        save_conversation_to_file(conversation, file_path)


def create_n_save_wordclouds(
    conversation_list: ConversationList, folder_path: Path, **kwargs: Any
) -> None:
    """Create the wordclouds for the conversations in the conversation list."""

    weeks_dict = conversation_list.grouped_by_week()
    months_dict = conversation_list.grouped_by_month()
    years_dict = conversation_list.grouped_by_year()

    for week in tqdm(weeks_dict.keys(), desc="Creating weekly wordclouds 🔡☁️ "):
        wordcloud_from_conversation_list(
            weeks_dict[week], **kwargs
        ).to_file(  # type: ignore
            folder_path / f"{week.strftime('%Y week %W')}.png"
        )

    for month in tqdm(months_dict.keys(), desc="Creating monthly wordclouds 🔡☁️ "):
        wordcloud_from_conversation_list(
            months_dict[month], **kwargs
        ).to_file(  # type: ignore
            folder_path / f"{month.strftime('%Y %B')}.png"
        )

    for year in tqdm(years_dict.keys(), desc="Creating yearly wordclouds 🔡☁️ "):
        wordcloud_from_conversation_list(
            years_dict[year], **kwargs
        ).to_file(  # type: ignore
            folder_path / f"{year.strftime('%Y')}.png"
        )


def save_custom_instructions_to_file(
    conversation_list: ConversationList, file_path: Path
) -> None:
    """Create JSON file for custom instructions in the conversation list."""

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(conversation_list.all_custom_instructions(), file, indent=2)
