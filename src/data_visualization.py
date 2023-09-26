"""Data Visualization

Todo:
    - Make as many insightful, creative, and magnificent visualizations
    of the conversations' data as possible.
"""

import json
import os
from typing import Any

from nltk.corpus import stopwords  # type: ignore
from wordcloud import WordCloud  # type: ignore
import matplotlib.pyplot as plt  # type: ignore


def simplify(conversation: dict[str, Any]) -> dict[str, Any]:
    simple_convo: dict[str, Any] = {}
    simple_convo["title"] = conversation["title"]
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


def create_wordcloud(
    json_filepath: str,
    out_folder_parent: str,
    author: str,
    font_number: int = 0,
    colormap_number: int = 0,
):
    # Load JSON data
    with open(json_filepath, "r", encoding="utf-8") as file:
        conversations = json.load(file)

    text_filepath = os.path.join(
        out_folder_parent, f"all-the-conversations_{author}.txt"
    )

    with open(text_filepath, "w", encoding="utf-8") as file:
        for conversation in conversations:
            simple_convo = simplify(conversation)

            conversation_text = [
                message["content"]["parts"][0]
                if (
                    "author" in message
                    and "parts" in message["content"]
                    and message["author"]["role"] == f"{author}"
                )
                else ""
                for message in simple_convo["messages"]
            ]

            file.write(" ".join(conversation_text))

    # Predefined stop words from NLTK
    languages = ["english", "french", "german", "arabic", "russian"]
    stop_words = set(word for lang in languages for word in stopwords.words(lang))  # type: ignore

    # List of files containing custom stop words
    files = [
        "stopwords/kagglesdsdata_datasets_arabic.txt",
        "stopwords/kagglesdsdata_datasets_english.txt",
        "stopwords/kagglesdsdata_datasets_french.txt",
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

    def font_path(font_name: str):
        return f"fonts/{font_name}.ttf"

    fonts = os.listdir("fonts")
    fonts = [os.path.splitext(font)[0] for font in fonts]

    selected_font = fonts[font_number]

    colormaps = [
        # Perceptually Uniform Sequential
        "viridis",
        "plasma",
        "inferno",
        "magma",
        "cividis",
        # Sequential
        "Blues",
        "Greens",
        "Oranges",
        "Purples",
        "Greys",
        "Reds",
        "YlGnBu",
        "YlOrRd",
        "OrRd",
        # Sequential (Multi-Hue)
        "GnBu",
        "BuGn",
        "PuBu",
        "BuPu",
        "YlGn",
        "PiYG",
        # Diverging
        "RdBu",
        "RdGy",
        "RdYlBu",
        "Spectral",
        "coolwarm",
        "bwr",
        # Cyclic
        "hsv",
        "twilight",
        "twilight_shifted",
        # Qualitative
        "Pastel1",
        "Pastel2",
        "Set1",
        "Set2",
        "Set3",
        "tab10",
        "tab20",
        "tab20c",
        # Miscellaneous
        "rainbow",
        "gist_earth",
        "terrain",
        "ocean",
        "gist_stern",
        "prism",
        "flag",
    ]

    colormap = colormaps[colormap_number]

    # Generate Word Cloud
    print("Creating Word Cloud ...")

    wordcloud = WordCloud(  # type: ignore
        # mask=mask,  # Uncomment this if using a mask
        font_path=font_path(selected_font),  # Point to a font file if you have one
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
        f"Wordclouds/{selected_font}_{colormap}_{author}_wordcloud.png",
    )

    wordcloud.to_file(wordcloud_path)  # type: ignore
