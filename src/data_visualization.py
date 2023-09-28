"""Data Visualization

Todo:
    - Make as many insightful, creative, and magnificent visualizations
    of the conversations' data as possible.
"""

import json
import os
from typing import Any

import nltk  # type: ignore
from nltk.corpus import stopwords  # type: ignore
from wordcloud import WordCloud  # type: ignore
import matplotlib.pyplot as plt  # type: ignore


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


def create_wordcloud(
    json_filepath: str,
    out_folder_parent: str,
    author: str,
    font_path: str,
    colormap: str,
):
    # Load JSON data
    with open(json_filepath, "r", encoding="utf-8") as file:
        conversations = json.load(file)

    text_filepath = os.path.join(out_folder_parent, f"Prompts_{author}.txt")

    with open(text_filepath, "w", encoding="utf-8") as file:
        for conversation in conversations:
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
        "assets/stopwords/kagglesdsdata_datasets_arabic.txt",
        "assets/stopwords/kagglesdsdata_datasets_english.txt",
        "assets/stopwords/kagglesdsdata_datasets_french.txt",
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
    print("Creating Word Cloud ...")

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

    def get_font_name(font_path: str):
        return os.path.splitext(os.path.basename(font_path))[0]

    wordcloud_path = os.path.join(
        out_folder_parent,
        f"Wordclouds/{get_font_name(font_path)}_{colormap}_{author}_wordcloud.png",
    )

    wordcloud.to_file(wordcloud_path)  # type: ignore

    print("Word Cloud 🔡☁️ created successfully !")
