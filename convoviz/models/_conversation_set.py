"""ConversationSet class to model a set of conversations.

Groups conversations by week, month, and year, etc.
"""

from __future__ import annotations

from json import dump as json_dump
from json import load as json_load
from pathlib import Path
from time import ctime
from typing import TYPE_CHECKING

from tqdm import tqdm

from convoviz.data_analysis import generate_week_barplot, generate_wordcloud
from convoviz.utils import get_archive, sanitize

from ._conversation import Conversation

if TYPE_CHECKING:
    from datetime import datetime
    from typing import Any, ClassVar

    from matplotlib.figure import Figure
    from PIL.Image import Image
    from typing_extensions import Self, Unpack

    from convoviz.utils import GraphKwargs, WordCloudKwargs

    from ._conversation import ConversationJSON
    from ._message import AuthorRole


class ConversationSet:
    """Stores a set of conversations."""

    _configs: ClassVar[dict[str, Any]] = {}

    def __init__(self, conversations: list[ConversationJSON]) -> None:
        """Initialize ConversationSet object."""
        self.index = {
            conversation["conversation_id"]: Conversation(conversation)
            for conversation in conversations
        }

        self.array = list(self.index.values())

    @classmethod
    def update_configs(cls, configs: dict[str, Any]) -> None:
        """Set the configuration for all conversation sets."""
        cls._configs.update(configs)

    @classmethod
    def from_json(cls, filepath: Path | str) -> Self:
        """Load from a JSON file, containing an array of conversations."""
        filepath = Path(filepath)
        with filepath.open(encoding="utf-8") as file:
            return cls(json_load(file))

    @classmethod
    def from_zip(cls, filepath: Path | str) -> Self:
        """Load from a ZIP file, containing a JSON file."""
        filepath = Path(filepath)
        conversations_path = get_archive(filepath) / "conversations.json"

        return cls.from_json(conversations_path)

    @property
    def last_updated(self) -> float:
        """Return the timestamp of the last updated conversation in the list."""
        return max(conversation.update_time for conversation in self.array)

    def update(self, conv_set: Self) -> None:
        """Update the conversation set with the new one."""
        if conv_set.last_updated <= self.last_updated:
            return
        self.index.update(conv_set.index)
        self.array = list(self.index.values())

    def save(self, dir_path: Path | str, *, progress_bar: bool = False) -> None:
        """Save the conversation set to the directory."""
        dir_path = Path(dir_path)
        dir_path.mkdir(parents=True, exist_ok=True)

        for conversation in tqdm(
            self.array,
            "Writing Markdown 📄 files",
            disable=not progress_bar,
        ):
            filepath = dir_path / sanitize(f"{conversation.title}.md")
            conversation.save(filepath)

    @property
    def custom_instructions(self) -> list[dict[str, Any]]:
        """Get a list of all custom instructions, in all conversations in the set."""
        custom_instructions: list[dict[str, Any]] = []

        for conversation in self.array:
            if not conversation.custom_instructions:
                continue

            instructions_info = {
                "chat_title": conversation.title,
                "chat_link": conversation.chat_link,
                "time": ctime(conversation.create_time),
                "custom_instructions": conversation.custom_instructions,
            }

            custom_instructions.append(instructions_info)

        return custom_instructions

    def save_custom_instructions(self, filepath: Path | str) -> None:
        """Save the custom instructions to the file."""
        filepath = Path(filepath)
        with filepath.open("w", encoding="utf-8") as file:
            json_dump(self.custom_instructions, file, indent=2)

    def timestamps(
        self,
        *authors: AuthorRole,
    ) -> list[float]:
        """Get a list of all message timestamps, in all conversations in the list."""
        timestamps: list[float] = []

        for conversation in self.array:
            timestamps.extend(conversation.timestamps(*authors))

        return timestamps

    def week_barplot(
        self,
        title: str,
        *authors: AuthorRole,
        **kwargs: Unpack[GraphKwargs],
    ) -> Figure:
        """Create a bar graph from the given conversation set."""
        if len(authors) == 0:
            authors = ("user",)
        timestamps = self.timestamps(*authors)
        return generate_week_barplot(timestamps, title, **kwargs)

    def plaintext(
        self,
        *authors: AuthorRole,
    ) -> str:
        """Get a string of all text, in all conversations in the list."""
        return "\n".join(
            conversation.plaintext(*authors) for conversation in self.array
        )

    def wordcloud(
        self,
        *authors: AuthorRole,
        **kwargs: Unpack[WordCloudKwargs],
    ) -> Image:
        """Create a wordcloud from the given conversation set."""
        if len(authors) == 0:
            authors = ("user", "assistant")
        text = self.plaintext(*authors)
        return generate_wordcloud(text, **kwargs)

    def add(self, conv: Conversation) -> None:
        """Add a conversation to the dictionary and list."""
        self.index[conv.conversation_id] = conv
        self.array.append(conv)

    def group_by_week(self) -> dict[datetime, Self]:
        """Get a dictionary of conversations grouped by the start of the week."""
        grouped: dict[datetime, Self] = {}

        for conversation in self.array:
            week_start = conversation.week_start
            if week_start not in grouped:
                grouped[week_start] = self.__class__([])
            grouped[week_start].add(conversation)

        return grouped

    def group_by_month(self) -> dict[datetime, Self]:
        """Get a dictionary of conversations grouped by the start of the month."""
        grouped: dict[datetime, Self] = {}

        for conversation in self.array:
            month_start = conversation.month_start
            if month_start not in grouped:
                grouped[month_start] = self.__class__([])
            grouped[month_start].add(conversation)

        return grouped

    def group_by_year(self) -> dict[datetime, Self]:
        """Get a dictionary of conversations grouped by the start of the year."""
        grouped: dict[datetime, Self] = {}

        for conversation in self.array:
            year_start = conversation.year_start
            if year_start not in grouped:
                grouped[year_start] = self.__class__([])
            grouped[year_start].add(conversation)

        return grouped
