"""Module for various processes that are used in the controllers."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Unpack

from tqdm import tqdm

if TYPE_CHECKING:
    from .models import ConversationSet
    from .utils import GraphKwargs, WordCloudKwargs


def generate_week_barplots(
    conv_set: ConversationSet,
    dir_path: Path | str,
    *,
    progress_bar: bool = False,
    **kwargs: Unpack[GraphKwargs],
) -> None:
    """Create the weekwise graphs and save them to the folder."""
    dir_path = Path(dir_path)

    month_groups = conv_set.group_by_month()
    year_groups = conv_set.group_by_year()

    for month in tqdm(
        month_groups.keys(),
        "Creating monthly weekwise graphs 📈 ",
        disable=not progress_bar,
    ):
        title = month.strftime("%B '%y")
        month_groups[month].week_barplot(title, **kwargs).savefig(  # pyright: ignore [reportUnknownMemberType]
            dir_path / f"{month.strftime('%Y %B')}.png",
        )

    for year in tqdm(
        year_groups.keys(),
        "Creating yearly weekwise graphs 📈 ",
        disable=not progress_bar,
    ):
        title = year.strftime("%Y")
        year_groups[year].week_barplot(title, **kwargs).savefig(  # pyright: ignore [reportUnknownMemberType]
            dir_path / f"{year.strftime('%Y')}.png",
        )


def generate_wordclouds(
    conv_set: ConversationSet,
    dir_path: Path | str,
    *,
    progress_bar: bool = False,
    **kwargs: Unpack[WordCloudKwargs],
) -> None:
    """Create the wordclouds and save them to the folder."""
    dir_path = Path(dir_path)

    week_groups = conv_set.group_by_week()
    month_groups = conv_set.group_by_month()
    year_groups = conv_set.group_by_year()

    for week in tqdm(
        week_groups.keys(),
        "Creating weekly wordclouds 🔡☁️ ",
        disable=not progress_bar,
    ):
        week_groups[week].wordcloud(**kwargs).save(
            dir_path / f"{week.strftime('%Y week %W')}.png",
            optimize=True,
        )

    for month in tqdm(
        month_groups.keys(),
        "Creating monthly wordclouds 🔡☁️ ",
        disable=not progress_bar,
    ):
        month_groups[month].wordcloud(**kwargs).save(
            dir_path / f"{month.strftime('%Y %B')}.png",
            optimize=True,
        )

    for year in tqdm(
        year_groups.keys(),
        "Creating yearly wordclouds 🔡☁️ ",
        disable=not progress_bar,
    ):
        year_groups[year].wordcloud(**kwargs).save(
            dir_path / f"{year.strftime('%Y')}.png",
            optimize=True,
        )
