"""Module for all the data visualizations.

Should ideally only return matplotlib objects, and not deal with the filesystem.
"""

# pyright: reportUnknownMemberType = false

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Unpack

from matplotlib.figure import Figure
from nltk import download as nltk_download  # type: ignore[import-untyped]
from nltk.corpus import stopwords as nltk_stopwords  # type: ignore[import-untyped]
from nltk.data import find as nltk_find  # type: ignore[import-untyped]
from wordcloud import WordCloud  # type: ignore[import-untyped]

from .utils import DEFAULT_WORDCLOUD_CONFIGS

if TYPE_CHECKING:
    from PIL.Image import Image

    from .utils import GraphKwargs, WordCloudKwargs


def generate_week_barplot(
    timestamps: list[float],
    title: str,
    **kwargs: Unpack[GraphKwargs],
) -> Figure:
    """Create a bar graph from the given timestamps, collapsed on one week."""
    dates = [datetime.fromtimestamp(ts, timezone.utc) for ts in timestamps]

    weekday_counts: defaultdict[str, int] = defaultdict(int)
    days = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]

    for date in dates:
        weekday_counts[days[date.weekday()]] += 1

    x = days
    y = [weekday_counts[day] for day in days]

    fig = Figure(dpi=300)
    ax = fig.add_subplot()

    ax.bar(x, y)
    ax.set_xlabel("Weekday")
    ax.set_ylabel("Prompt Count")

    ax.set_title(title)

    ax.set_xticks(x)
    ax.set_xticklabels(x, rotation=45)
    fig.tight_layout()

    return fig


# Ensure that the stopwords are downloaded
def _load_nltk_stopwords() -> set[str]:
    """Load nltk stopwords."""
    try:
        nltk_find("corpora/stopwords")
    except LookupError:
        nltk_download("stopwords")

    languages = [
        "arabic",
        "english",
        "french",
        "german",
        "spanish",
        "portuguese",
    ]  # add more languages here ...

    return {word for lang in languages for word in nltk_stopwords.words(fileids=lang)}


def generate_wordcloud(
    text: str,
    **kwargs: Unpack[WordCloudKwargs],
) -> Image:
    """Create a wordcloud from the given text."""
    configs = DEFAULT_WORDCLOUD_CONFIGS.copy()
    configs.update(kwargs)

    nltk_stopwords = _load_nltk_stopwords()

    custom_stopwords = configs.get("custom_stopwords")
    custom_stopwords_list = custom_stopwords.split(sep=",") if custom_stopwords else []
    custom_stopwords_list = [
        word.strip().lower() for word in custom_stopwords_list if word.strip()
    ]

    stopwords = nltk_stopwords.union(set(custom_stopwords_list))

    wordcloud = WordCloud(
        font_path=configs.get("font_path"),
        width=configs.get("width"),  # pyright: ignore[reportGeneralTypeIssues]
        height=configs.get("height"),  # pyright: ignore[reportGeneralTypeIssues]
        stopwords=stopwords,  # pyright: ignore[reportGeneralTypeIssues]
        background_color=configs.get("background_color"),  # pyright: ignore[reportGeneralTypeIssues]
        mode=configs.get("mode"),  # pyright: ignore[reportGeneralTypeIssues]
        colormap=configs.get("colormap"),
        include_numbers=configs.get("include_numbers"),  # pyright: ignore[reportGeneralTypeIssues]
    ).generate(text)

    return wordcloud.to_image()
