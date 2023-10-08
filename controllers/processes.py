"""Module for various processes that are used in the controllers."""


import json
from pathlib import Path
from typing import Any, Dict
from zipfile import ZipFile

from tqdm import tqdm

from models.conversation_list import ConversationList

from .data_visualizations import create_save_wordcloud


def load_conversations_from_zip(zip_filepath: Path) -> ConversationList:
    """Load the conversations from the zip file."""

    with ZipFile(zip_filepath, "r") as file:
        file.extractall(zip_filepath.with_suffix(""))

    conversations_path = zip_filepath.with_suffix("") / "conversations.json"

    with open(conversations_path, "r", encoding="utf-8") as file:
        conversations = json.load(file)

    return ConversationList(conversations)


def write_markdown_files(
    conversation_list: ConversationList, markdown_folder: Path
) -> None:
    """Write the markdown files for the conversations in the conversation list."""

    for conversation in tqdm(
        conversation_list.conversations, desc="Writing Markdown 📄 files"
    ):
        file_path = markdown_folder / f"{conversation.sanitized_title()}.md"
        conversation.save_to_file(file_path)


def create_wordclouds(
    conversation_list: ConversationList, wordcloud_folder: Path, configs: Dict[str, Any]
) -> None:
    """Create the wordclouds for the conversations in the conversation list."""

    weeks_dict = conversation_list.grouped_by_week()
    months_dict = conversation_list.grouped_by_month()
    years_dict = conversation_list.grouped_by_year()

    font_path = Path("assets/fonts") / f"{configs['wordcloud']['font']}.ttf"

    colormap = configs["wordcloud"]["colormap"]

    for week in tqdm(weeks_dict.keys(), desc="Creating weekly wordclouds 🔡☁️ "):
        entire_week_text = (
            weeks_dict[week].all_user_text()
            + "\n"
            + weeks_dict[week].all_assistant_text()
        )

        create_save_wordcloud(
            entire_week_text,
            wordcloud_folder / f"{week.strftime('%Y week %W')}.png",
            font_path=str(font_path),
            colormap=colormap,
        )

    for month in tqdm(months_dict.keys(), desc="Creating monthly wordclouds 🔡☁️ "):
        entire_month_text = (
            months_dict[month].all_user_text()
            + "\n"
            + months_dict[month].all_assistant_text()
        )

        create_save_wordcloud(
            entire_month_text,
            wordcloud_folder / f"{month.strftime('%B %Y')}.png",
            font_path=str(font_path),
            colormap=colormap,
        )

    for year in tqdm(years_dict.keys(), desc="Creating yearly wordclouds 🔡☁️ "):
        entire_year_text = (
            years_dict[year].all_user_text()
            + "\n"
            + years_dict[year].all_assistant_text()
        )

        create_save_wordcloud(
            entire_year_text,
            wordcloud_folder / f"{year.strftime('%Y')}.png",
            font_path=str(font_path),
            colormap=colormap,
        )


def write_custom_instructions(
    conversation_list: ConversationList, file_path: Path
) -> None:
    """Create JSON file for custom instructions in the conversation list."""

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(conversation_list.all_custom_instructions(), file, indent=2)
