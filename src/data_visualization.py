"""Data Visualization

Todo:
    - Make as many insightful, creative, and magnificent visualizations
    of the conversations' data as possible.
"""

import calendar
import datetime
import json
import os
from typing import Any

import matplotlib.pyplot as plt  # type: ignore
import nltk  # type: ignore
from nltk.corpus import stopwords  # type: ignore
from wordcloud import WordCloud  # type: ignore


# This function will check if the stopwords are available. If not, it will download them.
def ensure_stopwords_downloaded():
    try:
        # Try to access the stopwords. If this throws an error, it means they aren't downloaded.
        nltk.data.find("corpora/stopwords")  # type: ignore
    except LookupError:
        # If the stopwords aren't found, download them.
        nltk.download("stopwords")  # type: ignore


# Run the function
ensure_stopwords_downloaded()


def simplify(conversation: dict[str, Any]) -> dict[str, Any]:
    simple_convo: dict[str, Any] = {}
    simple_convo["title"] = conversation.get("title", "Untitled")
    simple_convo["create_time"] = conversation["create_time"]
    simple_convo["update_time"] = conversation["update_time"]
    simple_convo["id"] = conversation["id"]
    mappings = conversation["mapping"]
    messages = [value for _, value in mappings.items()]
    messages = [
        message.get("message") for message in messages if message.get("message")
    ]
    simple_convo["messages"] = messages

    return simple_convo


# Get the current date
now = datetime.datetime.now()

# Extract the month and year
current_month_name = calendar.month_name[now.month]
current_year = now.year


def get_unix_timestamp(month: str, year: int = 2023) -> int:
    """Get the UNIX timestamp for the first day of the given month and year."""

    # Convert month name to its corresponding number
    month_number = list(calendar.month_abbr).index(month.capitalize()[:3])

    if month_number == 0:
        raise ValueError(f"Invalid month name: {month}")

    dt = datetime.datetime(year, month_number, 1)

    # Convert the datetime object to UNIX timestamp
    timestamp = int(dt.timestamp())

    return timestamp


def get_font_name(font_path: str):
    return os.path.splitext(os.path.basename(font_path))[0]


def create_wordcloud(
    json_filepath: str,
    out_folder_parent: str,
    author: str,
    font_path: str,
    colormap: str,
    start_month: str = "January",
    end_month: str = current_month_name,
):
    # Load JSON data
    with open(json_filepath, "r", encoding="utf-8") as file:
        conversations = json.load(file)

    font_name = get_font_name(font_path)

    text_filepath = os.path.join(
        out_folder_parent,
        f"01-{start_month} to 01-{end_month} Prompts.txt",
    )

    start_timestamp = get_unix_timestamp(start_month)
    end_timestamp = get_unix_timestamp(end_month)

    with open(text_filepath, "w", encoding="utf-8") as file:
        for conversation in conversations:
            if conversation["create_time"] < start_timestamp:
                continue
            if conversation["create_time"] > end_timestamp:
                continue

            simple_convo = simplify(conversation)

            conversation_text = [
                message["content"]["parts"][0]
                for message in simple_convo["messages"]
                if (
                    "author" in message
                    and "parts" in message["content"]
                    and message["author"]["role"] == f"{author}"
                )
            ]

            file.write(
                f"{conversation_text[0]} \n\n{'-'*100}\n\n"
            )  # just the first message (Prompt)

    # Predefined stop words from NLTK
    languages = ["english", "french", "german", "arabic", "russian"]
    stop_words = set(word for lang in languages for word in stopwords.words(lang))  # type: ignore

    # List of files containing custom stop words
    files = [
        # "assets/stopwords/kagglesdsdata_datasets_arabic.txt",
        # "assets/stopwords/kagglesdsdata_datasets_english.txt",
        # "assets/stopwords/kagglesdsdata_datasets_french.txt",
        "assets/stopwords/programming-languages-keywords.txt",
    ]

    # Read the custom stop words from each file and add to the list
    custom_stop_words = []
    for text_dataset in files:
        with open(text_dataset, "r", encoding="utf-8") as f:
            custom_stop_words.extend(f.read().splitlines())  # type: ignore

    # Update the existing stop_words set with the custom_stop_words
    stop_words.update(custom_stop_words)

    with open(text_filepath, "r", encoding="utf-8") as file:
        text = file.read()

    words = text.split()
    words = [
        word.lower()
        for word in words
        if word.isalpha() and word.lower() not in stop_words
    ]
    cleaned_text = " ".join(words)

    # Generate Word Cloud
    print("Creating Word Cloud ...\n")

    wordcloud = WordCloud(  # type: ignore
        # mask=mask,  # Uncomment this if using a mask
        font_path=font_path,  # Point to a font file if you have one
        background_color="white",
        max_font_size=100,
        contour_width=3,
        colormap=colormap,
        width=800,
        height=800,
        contour_color="steelblue",
    ).generate(cleaned_text)

    os.makedirs(os.path.join(out_folder_parent, "Wordclouds"), exist_ok=True)

    wordcloud_path = os.path.join(
        out_folder_parent,
        f"Wordclouds/01-{start_month} to 01-{end_month} {font_name} {colormap} wordcloud.png",
    )

    wordcloud.to_file(wordcloud_path)  # type: ignore

    print(f"Word Cloud 🔡☁️ created successfully ! :\n'{os.path.basename(wordcloud_path)}'\n")
