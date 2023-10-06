"""Module for all the data visualizations."""

from pathlib import Path
from typing import Any, List

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import nltk  # type: ignore
import pandas as pd
from nltk.corpus import stopwords  # type: ignore
from wordcloud import WordCloud  # type: ignore


# Ensure that the stopwords are downloaded
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

stop_words = set(word for lang in languages for word in stopwords.words(lang))  # type: ignore


def create_save_wordcloud(
    text: str,
    file_path: Path,
    **kwargs: Any,
) -> None:
    """Creates and saves a wordcloud from the given text."""
    wordcloud = WordCloud(stopwords=stop_words, width=1000, height=1000, background_color=None, mode="RGBA", **kwargs).generate(text)  # type: ignore

    wordcloud.to_file(file_path)  # type: ignore


def create_save_graph(all_timestamps: List[float], file_path: Path) -> None:
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
