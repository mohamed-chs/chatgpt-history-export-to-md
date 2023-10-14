"""Module for all the data visualizations.

Should ideally only return matplotlib objects, and not deal with the filesystem."""

from pathlib import Path
from typing import Any

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import nltk  # type: ignore
import pandas as pd
from nltk.corpus import stopwords  # type: ignore
from wordcloud import WordCloud  # type: ignore

from models.conversation_set import ConversationSet


# Ensure that the stopwords are downloaded
def load_nltk_stopwords() -> set[str]:
    """Loads the nltk stopwords. Returns a set of stopwords."""

    try:
        nltk.data.find("corpora/stopwords")  # type: ignore
    except LookupError:
        nltk.download("stopwords")  # type: ignore

    languages = [
        "arabic",
        "english",
        "french",
        "german",
        "spanish",
        "portuguese",
    ]  # add more languages here ...

    stop_words = set(
        word for lang in languages for word in stopwords.words(lang)  # type: ignore
    )

    return stop_words


def wordcloud_from_text(
    text: str,
    **kwargs: Any,
) -> WordCloud:
    """Creates a wordcloud from the given text. Returns a WordCloud object."""

    custom_stopwords: list[str] = kwargs.get("stopwords", [])
    default_stopwords = load_nltk_stopwords()
    stop_words = default_stopwords.union(set(custom_stopwords))
    background_color = kwargs.get("background_color", None)
    if background_color is None:
        mode = kwargs.get("mode", "RGBA")
    else:
        mode = kwargs.get("mode", "RGB")

    # TODO: add more arguments here ...

    wordcloud = WordCloud(
        font_path=kwargs.get(
            "font_path", "assets/fonts/ArchitectsDaughter-Regular.ttf"
        ),
        width=kwargs.get("width", 1000),
        height=kwargs.get("height", 1000),
        stopwords=stop_words,
        background_color=background_color,
        mode=mode,
        colormap=kwargs.get("colormap", "prism"),
        include_numbers=kwargs.get("include_numbers", False),
    ).generate(  # type: ignore
        text
    )

    return wordcloud


def wordcloud_from_conversation_set(
    conversation_set: ConversationSet, **kwargs: Any
) -> WordCloud:
    """Creates a wordcloud from the given conversation set. Returns a WordCloud object."""
    text = (
        conversation_set.all_user_text() + "\n" + conversation_set.all_assistant_text()
    )

    return wordcloud_from_text(text, **kwargs)


def create_save_graph(all_timestamps: list[float], file_path: Path) -> None:
    """Creates and saves a graph from the given timestamps."""

    df = pd.DataFrame(all_timestamps, columns=["timestamp"])  # type: ignore
    df["datetime"] = pd.to_datetime(df["timestamp"], unit="s")  # type: ignore

    daily_counts = df.groupby(df["datetime"].dt.date).size()  # type: ignore

    plt.figure(figsize=(15, 7))  # type: ignore

    daily_counts.plot(
        kind="line",
        marker="o",
        linestyle="-",
        linewidth=2,
        markersize=8,
        color="royalblue",
        markeredgecolor="white",
        markeredgewidth=0.5,
    )

    plt.title("ChatGPT Prompts per Day", fontsize=20, fontweight="bold", pad=20)  # type: ignore
    plt.xlabel("Month", fontsize=16, labelpad=15)  # type: ignore
    plt.ylabel("Number of Prompts", fontsize=16, labelpad=15)  # type: ignore
    plt.xticks(fontsize=14)  # type: ignore
    plt.yticks(fontsize=14)  # type: ignore

    ax = plt.gca()  # type: ignore
    ax.xaxis.set_major_locator(mdates.MonthLocator())  # type: ignore
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%B"))  # type: ignore

    plt.xticks(rotation=45)  # type: ignore

    plt.grid(True, linestyle="--", linewidth=0.5, alpha=0.7)  # type: ignore

    plt.tight_layout()  # type: ignore

    plt.savefig(file_path)  # type: ignore

    # close the plot
    plt.close()  # type: ignore
