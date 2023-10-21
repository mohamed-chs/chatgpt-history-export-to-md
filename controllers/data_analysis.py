"""Module for all the data visualizations.

Should ideally only return matplotlib objects, and not deal with the filesystem.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from matplotlib.figure import Figure
from nltk import data as nltk_data  # type: ignore[import-untyped]
from nltk import download as nltk_download  # type: ignore[import-untyped]
from nltk.corpus import stopwords as nltk_stopwords  # type: ignore[import-untyped]
from wordcloud import WordCloud  # type: ignore[import-untyped]

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from PIL.Image import Image

    from models.conversation_set import ConversationSet


def weekwise_graph_from_timestamps(
    timestamps: list[float],
    **kwargs: str,
) -> Figure:
    """Create a bar graph from the given timestamps, collapsed on one week."""
    dates: list[datetime] = [
        datetime.fromtimestamp(ts, tz=timezone.utc) for ts in timestamps
    ]

    weekday_counts: defaultdict[str, int] = defaultdict(int)
    days: list[str] = [
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

    x: list[str] = days
    y: list[int] = [weekday_counts[day] for day in days]

    fig: Figure = Figure()
    ax: Axes = fig.add_subplot()

    ax.bar(x=x, height=y)
    ax.set_xlabel(xlabel="Weekday")
    ax.set_ylabel(ylabel="Prompt Count")

    month_name: str = kwargs.get("month_name", "")
    if month_name:
        ax.set_title(label=f"Prompt Count for {month_name}")

    year: str = kwargs.get("year", "")
    if year:
        ax.set_title(label=f"Prompt Count for {year}")

    ax.set_xticks(ticks=x)
    ax.set_xticklabels(labels=x, rotation=45)
    fig.tight_layout()

    return fig


def weekwise_graph_from_conversation_set(
    conv_set: ConversationSet,
    **kwargs: str,
) -> Figure:
    """Create a bar graph from the given conversation set."""
    timestamps: list[float] = conv_set.all_author_message_timestamps(author="user")
    return weekwise_graph_from_timestamps(timestamps=timestamps, **kwargs)


# Ensure that the stopwords are downloaded
def load_nltk_stopwords() -> set[str]:
    """Load nltk stopwords."""
    try:
        nltk_data.find(resource_name="corpora/stopwords")
    except LookupError:
        nltk_download(info_or_id="stopwords")

    languages: list[str] = [
        "arabic",
        "english",
        "french",
        "german",
        "spanish",
        "portuguese",
    ]  # add more languages here ...

    return {word for lang in languages for word in nltk_stopwords.words(fileids=lang)}


def wordcloud_from_text(
    text: str,
    **kwargs: Any,
) -> Image:
    """Create a wordcloud from the given text."""
    default_stopwords: set[str] = load_nltk_stopwords()

    custom_stopwords: str = kwargs.get("custom_stopwords", "")
    custom_stopwords_list: list[str] = (
        custom_stopwords.split(sep=",") if custom_stopwords else []
    )
    custom_stopwords_list = [
        word.strip().lower() for word in custom_stopwords_list if word.strip()
    ]

    stop_words: set[str] = default_stopwords.union(set(custom_stopwords_list))

    background_color: str | None = kwargs.get("background_color", None)
    if background_color is None:
        mode: str = kwargs.get("mode", "RGBA")
    else:
        mode = kwargs.get("mode", "RGB")

    wordcloud: WordCloud = WordCloud(
        font_path=kwargs.get(
            "font_path",
            "assets/fonts/ArchitectsDaughter-Regular.ttf",
        ),
        width=kwargs.get("width", 1000),
        height=kwargs.get("height", 1000),
        stopwords=stop_words,
        background_color=background_color,
        mode=mode,
        colormap=kwargs.get("colormap", "prism"),
        include_numbers=kwargs.get("include_numbers", False),
    ).generate(
        text=text,
    )

    return wordcloud.to_image()


def wordcloud_from_conversation_set(
    conv_set: ConversationSet,
    **kwargs: Any,
) -> Image:
    """Create a wordcloud from the given conversation set."""
    text: str = (
        conv_set.all_author_text(author="user")
        + "\n"
        + conv_set.all_author_text(author="assistant")
    )

    return wordcloud_from_text(text=text, **kwargs)
