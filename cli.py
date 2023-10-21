"""Main file for running the program from the command line."""

from __future__ import annotations

from pathlib import Path
from shutil import rmtree
from typing import TYPE_CHECKING, Any

from controllers.configuration import get_user_configs, save_configs, set_model_configs
from controllers.file_system import (
    conversation_set_from_json,
    conversation_set_from_zip,
    create_all_weekwise_graphs,
    create_all_wordclouds,
    get_bookmarklet_json_filepath,
    save_conversation_set,
    save_custom_instructions,
)

if TYPE_CHECKING:
    from models.conversation_set import ConversationSet


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

    configs_dict: dict[str, Any] = get_user_configs()

    print("\n\nAnd we're off! 🚀🚀🚀\n")

    set_model_configs(configs=configs_dict)

    print("Loading data 📂 ...\n")

    zip_filepath = Path(configs_dict["zip_file"])

    all_conversations_set: ConversationSet = conversation_set_from_zip(
        zip_filepath=zip_filepath,
    )

    bookmarklet_json_filepath: Path | None = get_bookmarklet_json_filepath()
    if bookmarklet_json_filepath:
        print("Found bookmarklet download, loading 📂 ...\n")
        bookmarklet_conversations_set: ConversationSet = conversation_set_from_json(
            json_filepath=bookmarklet_json_filepath,
        )
        all_conversations_set.update(conv_set=bookmarklet_conversations_set)

    output_folder = Path(configs_dict["output_folder"])

    # overwrite the output folder if it already exists (might change this in the future)
    if output_folder.exists() and output_folder.is_dir():
        rmtree(output_folder)

    output_folder.mkdir(parents=True, exist_ok=True)

    markdown_folder: Path = output_folder / "Markdown"
    markdown_folder.mkdir(parents=True, exist_ok=True)

    save_conversation_set(
        conv_set=all_conversations_set,
        dir_path=markdown_folder,
    )

    print(f"\nDone ✅ ! Check the output 📄 here : {markdown_folder.as_uri()} 🔗\n")

    graph_folder: Path = output_folder / "Graphs"
    graph_folder.mkdir(parents=True, exist_ok=True)

    create_all_weekwise_graphs(
        conv_set=all_conversations_set,
        dir_path=graph_folder,
    )

    print(f"\nDone ✅ ! Check the output 📈 here : {graph_folder.as_uri()} 🔗\n")
    print("(more graphs 📈 will be added in the future ...)\n")

    wordcloud_folder: Path = output_folder / "Word Clouds"
    wordcloud_folder.mkdir(parents=True, exist_ok=True)

    font_path: str = f"assets/fonts/{configs_dict['wordcloud']['font']}.ttf"
    colormap: str = configs_dict["wordcloud"]["colormap"]
    custom_stopwords: str = configs_dict["wordcloud"]["custom_stopwords"]

    create_all_wordclouds(
        conv_set=all_conversations_set,
        dir_path=wordcloud_folder,
        font_path=font_path,
        colormap=colormap,
        custom_stopwords=custom_stopwords,
    )

    print(f"\nDone ✅ ! Check the output 🔡☁️ here : {wordcloud_folder.as_uri()} 🔗\n")

    print("Writing custom instructions 📝 ...\n")

    custom_instructions_filepath: Path = output_folder / "custom_instructions.json"

    save_custom_instructions(
        conv_set=all_conversations_set,
        filepath=custom_instructions_filepath,
    )

    print(
        "\nDone ✅ ! Check the output 📝 here :"
        f" {custom_instructions_filepath.as_uri()} 🔗\n",
    )

    save_configs(user_configs=configs_dict)
    print("(Settings ⚙️ have been updated and saved to 'user_config.json')\n")

    print(
        "ALL DONE 🎉🎉🎉 !\n\n"
        f"Explore the full gallery 🖼️ at: {output_folder.as_uri()} 🔗\n\n"
        "I hope you enjoy the outcome 🤞.\n\n"
        "If you appreciate it, kindly give the project a star 🌟 on GitHub :\n\n"
        "➡️ https://github.com/mohamed-chs/chatgpt-history-export-to-md 🔗\n\n",
    )


if __name__ == "__main__":
    main()
