"""Main file for running the program from the command line."""

from __future__ import annotations

from pathlib import Path
from shutil import rmtree

from .configuration import UserConfigs
from .long_runs import (
    generate_week_barplots,
    generate_wordclouds,
)
from .models import ConversationSet
from .utils import latest_bookmarklet_json


def main() -> None:
    """Run the program."""
    print(
        "Welcome to ChatGPT Data Visualizer ✨📊!\n\n"
        "Follow the instructions in the command line.\n\n"
        "Press 'ENTER' to select the default options.\n\n"
        "If you encounter any issues 🐛, please report 🚨 them here:\n\n"
        "➡️ https://github.com/mohamed-chs/chatgpt-history-export-to-md/issues/new/choose"
        " 🔗\n\n",
    )

    user = UserConfigs()

    user.prompt()

    print("\n\nAnd we're off! 🚀🚀🚀\n")

    user.set_model_configs()

    print("Loading data 📂 ...\n")

    entire_collection = ConversationSet.from_zip(user.configs["zip_filepath"])

    bkmrklet_json = latest_bookmarklet_json()
    if bkmrklet_json:
        print("Found bookmarklet download, loading 📂 ...\n")
        bkmrklet_collection = ConversationSet.from_json(bkmrklet_json)
        entire_collection.update(bkmrklet_collection)

    output_folder = Path(user.configs["output_folder"])

    # overwrite the output folder if it already exists (might change this in the future)
    if output_folder.exists() and output_folder.is_dir():
        rmtree(output_folder)

    output_folder.mkdir(parents=True, exist_ok=True)

    markdown_folder = output_folder / "Markdown"

    entire_collection.save(markdown_folder, progress_bar=True)

    print(f"\nDone ✅ ! Check the output 📄 here : {markdown_folder.as_uri()} 🔗\n")

    graph_folder = output_folder / "Graphs"
    graph_folder.mkdir(parents=True, exist_ok=True)

    generate_week_barplots(
        entire_collection,
        graph_folder,
        **user.configs["graph"],
        progress_bar=True,
    )

    print(f"\nDone ✅ ! Check the output 📈 here : {graph_folder.as_uri()} 🔗\n")
    print("(more graphs 📈 will be added in the future ...)\n")

    wordcloud_folder = output_folder / "Word Clouds"
    wordcloud_folder.mkdir(parents=True, exist_ok=True)

    generate_wordclouds(
        entire_collection,
        wordcloud_folder,
        **user.configs["wordcloud"],
        progress_bar=True,
    )

    print(f"\nDone ✅ ! Check the output 🔡☁️ here : {wordcloud_folder.as_uri()} 🔗\n")

    print("Writing custom instructions 📝 ...\n")

    cstm_inst_filepath = output_folder / "custom_instructions.json"

    entire_collection.save_custom_instructions(cstm_inst_filepath)

    print(f"\nDone ✅ ! Check the output 📝 here : {cstm_inst_filepath.as_uri()} 🔗\n")

    print(
        "ALL DONE 🎉🎉🎉 !\n\n"
        f"Explore the full gallery 🖼️ at: {output_folder.as_uri()} 🔗\n\n"
        "I hope you enjoy the outcome 🤞.\n\n"
        "If you appreciate it, kindly give the project a star 🌟 on GitHub :\n\n"
        "➡️ https://github.com/mohamed-chs/chatgpt-history-export-to-md 🔗\n\n",
    )
