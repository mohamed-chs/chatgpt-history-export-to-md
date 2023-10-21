"""Module for various processes that are used in the controllers.

Should ideally be the only module that deals with the filesystem.

(besides utils.py, but that doesn't save anything to disk,
and configuration.py, but that's a placeholder for user input in whatever form,
may be replaced later, with a GUI or something)
"""

from __future__ import annotations

from json import dump as json_dump
from json import load as json_load
from os import utime as os_utime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal
from zipfile import ZipFile

from tqdm import tqdm

from models.conversation_set import ConversationSet

from .data_analysis import (
    weekwise_graph_from_conversation_set,
    wordcloud_from_conversation_set,
)

if TYPE_CHECKING:
    from datetime import datetime

    from matplotlib.figure import Figure
    from PIL.Image import Image

    from models.conversation import Conversation


DOWNLOADS_PATH: Path = Path.home() / "Downloads"


def get_most_recently_downloaded_zip() -> Path | None:
    """Path to the most recently created zip file in the Downloads folder."""
    zip_files: list[Path] = list(DOWNLOADS_PATH.glob(pattern="*.zip"))

    if not zip_files:
        return None

    return max(zip_files, key=lambda x: x.stat().st_ctime)


def get_bookmarklet_json_filepath() -> Path | None:
    """Path to the most recent JSON file in Downloads with 'bookmarklet' in the name."""
    bkmrklet_files: list[Path] = [
        x for x in DOWNLOADS_PATH.glob(pattern="*.json") if "bookmarklet" in x.name
    ]

    if not bkmrklet_files:
        return None

    return max(bkmrklet_files, key=lambda x: x.stat().st_ctime)


def conversation_set_from_json(json_filepath: Path) -> ConversationSet:
    """Load the conversations from a JSON file, containing an array of conversations."""
    with json_filepath.open(encoding="utf-8") as file:
        conversations = json_load(fp=file)

    return ConversationSet(conversations=conversations)


def extract_zip(zip_filepath: Path) -> Path:
    """Extract the zip file to the same folder."""
    with ZipFile(file=zip_filepath, mode="r") as file:
        file.extractall(path=zip_filepath.with_suffix(suffix=""))

    return zip_filepath.with_suffix(suffix="")


def conversation_set_from_zip(zip_filepath: Path) -> ConversationSet:
    """Load conversations from a zip file, containing a 'conversations.json' file."""
    return conversation_set_from_json(
        json_filepath=extract_zip(zip_filepath=zip_filepath) / "conversations.json",
    )


def save_conversation(conversation: Conversation, filepath: Path) -> None:
    """Save the conversation to the file, with added modification time."""
    base_file_name: str = filepath.stem

    counter = 0
    while filepath.exists():
        counter += 1
        filepath = filepath.with_name(
            name=f"{base_file_name} ({counter}){filepath.suffix}",
        )

    with filepath.open(mode="w", encoding="utf-8") as file:
        file.write(conversation.markdown_text())
    os_utime(path=filepath, times=(conversation.update_time, conversation.update_time))


def save_conversation_set(conv_set: ConversationSet, dir_path: Path) -> None:
    """Save the conversation set to the directory."""
    for conversation in tqdm(
        iterable=conv_set.conversation_list,
        desc="Writing Markdown 📄 files",
    ):
        save_conversation(
            conversation=conversation,
            filepath=dir_path / f"{conversation.sanitized_title()}.md",
        )


def _save_figure(figure: Figure, filepath: Path) -> None:
    """Save the figure to the file."""
    figure.savefig(fname=filepath)


def save_weekwise_graph_from_conversation_set(
    conv_set: ConversationSet,
    dir_path: Path,
    time_period: tuple[datetime, Literal["month", "year"]],
    **kwargs: Any,
) -> None:
    """Create a weekwise graph and saves it to the folder."""
    if time_period[1] == "month":
        file_name: str = f"{time_period[0].strftime('%Y %B')}.png"
        _save_figure(
            figure=weekwise_graph_from_conversation_set(
                conv_set=conv_set,
                month_name=time_period[0].strftime("%B '%y"),
                **kwargs,
            ),
            filepath=dir_path / file_name,
        )
    elif time_period[1] == "year":
        file_name = f"{time_period[0].strftime('%Y')}.png"
        _save_figure(
            figure=weekwise_graph_from_conversation_set(
                conv_set=conv_set,
                year=time_period[0].strftime("%Y"),
                **kwargs,
            ),
            filepath=dir_path / file_name,
        )


def create_all_weekwise_graphs(
    conv_set: ConversationSet,
    dir_path: Path,
    **kwargs: Any,
) -> None:
    """Create the weekwise graphs and save them to the folder."""
    months_dict: dict[datetime, ConversationSet] = conv_set.grouped_by_month()
    years_dict: dict[datetime, ConversationSet] = conv_set.grouped_by_year()

    for month in tqdm(
        iterable=months_dict.keys(),
        desc="Creating monthly weekwise graphs 📈 ",
    ):
        save_weekwise_graph_from_conversation_set(
            conv_set=months_dict[month],
            dir_path=dir_path,
            time_period=(month, "month"),
            **kwargs,
        )

    for year in tqdm(
        iterable=years_dict.keys(),
        desc="Creating yearly weekwise graphs 📈 ",
    ):
        save_weekwise_graph_from_conversation_set(
            conv_set=years_dict[year],
            dir_path=dir_path,
            time_period=(year, "year"),
            **kwargs,
        )


def _save_image(image: Image, filepath: Path) -> None:
    """Save the word cloud to the file."""
    image.save(fp=filepath, optimize=True)


def save_wordcloud_from_conversation_set(
    conv_set: ConversationSet,
    dir_path: Path,
    time_period: tuple[datetime, Literal["week", "month", "year"]],
    **kwargs: Any,
) -> None:
    """Create a wordcloud and saves it to the folder."""
    if time_period[1] == "week":
        file_name: str = f"{time_period[0].strftime('%Y week %W')}.png"
    elif time_period[1] == "month":
        file_name = f"{time_period[0].strftime('%Y %B')}.png"
    elif time_period[1] == "year":
        file_name = f"{time_period[0].strftime('%Y')}.png"

    _save_image(
        image=wordcloud_from_conversation_set(conv_set=conv_set, **kwargs),
        filepath=dir_path / file_name,
    )


def create_all_wordclouds(
    conv_set: ConversationSet,
    dir_path: Path,
    **kwargs: Any,
) -> None:
    """Create the wordclouds and save them to the folder."""
    weeks_dict: dict[datetime, ConversationSet] = conv_set.grouped_by_week()
    months_dict: dict[datetime, ConversationSet] = conv_set.grouped_by_month()
    years_dict: dict[datetime, ConversationSet] = conv_set.grouped_by_year()

    for week in tqdm(
        iterable=weeks_dict.keys(),
        desc="Creating weekly wordclouds 🔡☁️ ",
    ):
        save_wordcloud_from_conversation_set(
            conv_set=weeks_dict[week],
            dir_path=dir_path,
            time_period=(week, "week"),
            **kwargs,
        )

    for month in tqdm(
        iterable=months_dict.keys(),
        desc="Creating monthly wordclouds 🔡☁️ ",
    ):
        save_wordcloud_from_conversation_set(
            conv_set=months_dict[month],
            dir_path=dir_path,
            time_period=(month, "month"),
            **kwargs,
        )

    for year in tqdm(
        iterable=years_dict.keys(),
        desc="Creating yearly wordclouds 🔡☁️ ",
    ):
        save_wordcloud_from_conversation_set(
            conv_set=years_dict[year],
            dir_path=dir_path,
            time_period=(year, "year"),
            **kwargs,
        )


def save_custom_instructions(conv_set: ConversationSet, filepath: Path) -> None:
    """Create JSON file for custom instructions in the conversation set."""
    with filepath.open(mode="w", encoding="utf-8") as file:
        json_dump(obj=conv_set.all_custom_instructions(), fp=file, indent=2)
