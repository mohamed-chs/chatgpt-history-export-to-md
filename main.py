"""Main file for testing the program."""

import os
import shutil
from pathlib import Path

from controllers.configuration import (
    get_user_configs,
    set_model_configs,
    update_config_file,
)
from controllers.data_analysis import create_save_graph
from controllers.file_system import (
    create_n_save_wordclouds,
    load_conversations_from_zip,
    save_conversation_list_to_dir,
    save_custom_instructions_to_file,
)

# DEBUG / PROFILING
pid = os.getpid()
print("PID:", pid)


def main() -> None:
    """Main function."""

    print(
        "Welcome to ChatGPT Data Visualizer ✨📊!\n\n"
        "Follow the instructions in the command line.\n\n"
        "Press 'ENTER' to select the default options.\n\n"
        "If you encounter any issues 🐛, please report 🚨 them here:\n\n"
        " ➡️ https://github.com/mohamed-chs/chatgpt-history-export-to-md/issues/new/choose 🔗\n\n"
    )

    configs_dict = get_user_configs()

    print("\n\nAnd we're off! 🚀🚀🚀\n")

    set_model_configs(configs_dict)

    print("Loading data 📂 ...\n")

    zip_filepath = Path(configs_dict["zip_file"])

    all_conversations_list = load_conversations_from_zip(zip_filepath)

    output_folder = Path(configs_dict["output_folder"])

    # overwrite the output folder if it already exists (might change this in the future)
    if output_folder.exists() and output_folder.is_dir():
        shutil.rmtree(output_folder)

    output_folder.mkdir(parents=True, exist_ok=True)

    markdown_folder = output_folder / "Markdown"
    markdown_folder.mkdir(parents=True, exist_ok=True)

    save_conversation_list_to_dir(all_conversations_list, markdown_folder)

    print(f"\nDone 🎉 ! Check the output 📄 here : {markdown_folder.as_uri()} 🔗\n")

    graph_folder = output_folder / "Graphs"
    graph_folder.mkdir(parents=True, exist_ok=True)

    print("Creating graph 📈 of prompts per day ...\n")

    graph_path = graph_folder / "all messages.png"

    create_save_graph(all_conversations_list.all_message_timestamps(), graph_path)

    print(f"\nDone 🎉 ! Check the output 📈 here : {graph_folder.as_uri()} 🔗\n")
    print("(more graphs 📈 will be added in the future ...)\n")

    wordcloud_folder = output_folder / "Word Clouds"
    wordcloud_folder.mkdir(parents=True, exist_ok=True)

    font_path = f"assets/fonts/{configs_dict['wordcloud']['font']}.ttf"
    colormap = configs_dict["wordcloud"]["colormap"]

    create_n_save_wordclouds(
        all_conversations_list, wordcloud_folder, font_path=font_path, colormap=colormap
    )

    print(f"\nDone 🎉 ! Check the output 🔡☁️ here : {wordcloud_folder.as_uri()} 🔗\n")

    print("Writing custom instructions 📝 ...\n")

    custom_instructions_filepath = output_folder / "custom_instructions.json"

    save_custom_instructions_to_file(
        all_conversations_list, custom_instructions_filepath
    )

    print(
        f"\nDone 🎉 ! Check the output 📝 here : {custom_instructions_filepath.as_uri()} 🔗\n"
    )

    update_config_file(configs_dict)
    print("(Settings ⚙️ have been updated and saved to 'config.json')\n")

    print(
        "ALL DONE 🎉🎉🎉 !\n\n"
        f"Explore the full gallery 🖼️ at: {output_folder.as_uri()} 🔗\n\n"
        "I hope you enjoy the outcome 🤞.\n\n"
        "If you appreciate it, kindly give the project a star 🌟 on GitHub :\n\n"
        "➡️ https://github.com/mohamed-chs/chatgpt-history-export-to-md 🔗\n\n"
    )


if __name__ == "__main__":
    main()
