"""Main file for testing the program."""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List
from zipfile import ZipFile

from tqdm import tqdm

from models.conversation import Conversation, group_by_month, group_by_week
from views.data_visualizations import create_save_graph, create_save_wordcloud
from views.questions import ask_questions

HOME: Path = Path.home()
DOWNLOADS: Path = HOME / "Downloads"

# most recent zip file in downloads folder
default_zip_filepath: Path = max(
    DOWNLOADS.glob("*.zip"), key=lambda x: x.stat().st_ctime
)

default_output_folder: Path = HOME / "Documents" / "TEST"


# utility function
def all_mondays(year: int) -> List[datetime]:
    # Start from the first day of the year
    d = datetime(year, 1, 1)

    # Move to the first Monday of the year
    while d.weekday() != 0:
        d += timedelta(days=1)

    # Collect all Mondays
    mondays: List[datetime] = []
    while d.year == year:
        mondays.append(d)
        d += timedelta(days=7)  # jump to next Monday

    return mondays


def main():
    """Main function."""

    print("Welcome to ChatGPT Data Visualizer ✨📊!\n")
    print("Follow the instructions in the command line.\n")
    print("Press 'ENTER' to select the default options.\n\n")

    # -------------- getting configs --------------

    with open("config.json", "r", encoding="utf-8") as file:
        configs = json.load(file)

    if not configs["zip_file"]:
        configs["zip_file"] = str(default_zip_filepath)

    if not configs["output_folder"]:
        configs["output_folder"] = str(default_output_folder)

    ask_questions(configs)

    print("\n\nAnd we're off! 🚀🚀🚀\n")

    # -------------- loading data --------------

    zip_filepath = Path(configs["zip_file"])
    with ZipFile(zip_filepath, "r") as zip_ref:
        zip_ref.extractall(zip_filepath.with_suffix(""))

    with open(
        zip_filepath.with_suffix("") / Path("conversations.json"), "r", encoding="utf-8"
    ) as file_ref:
        conversations = json.load(file_ref)

    # -------------- creating output folder --------------

    output_folder = Path(configs["output_folder"])
    output_folder.mkdir(parents=True, exist_ok=True)

    # ------------ grouping conversations by week and month -----------

    all_conversations: List[Conversation] = []

    for convo in conversations:
        conversation = Conversation(**convo)
        conversation.configuration = configs["conversation"]
        all_conversations.append(conversation)

    weeks_dict = group_by_week(all_conversations)

    months_dict = group_by_month(all_conversations)

    # --------- writing markdown files ---------

    markdown_folder = output_folder / "Markdown"
    markdown_folder.mkdir(parents=True, exist_ok=True)

    for conversation in tqdm(conversations, desc="Writing Markdown 📄 files"):
        conversation = Conversation(**conversation)
        conversation.configuration = configs["conversation"]
        conversation.save_to_dir(markdown_folder)

    print(f"\nDone 🎉 ! Check the output 📄 here : {markdown_folder.as_uri()} 🔗\n")

    # ----------- creating graphs -------------

    graph_folder = output_folder / "Graphs"
    graph_folder.mkdir(parents=True, exist_ok=True)

    # for week in tqdm(weeks_dict.keys(), desc="Creating weekly graphs 📈 ..."):
    #     all_week_timestamps = [
    #         node.message.create_time
    #         for convo in weeks_dict[week]
    #         for node in convo.user_nodes + convo.assistant_nodes
    #         if node.message and node.message.create_time
    #     ]

    #     create_save_graph(
    #         all_week_timestamps, graph_folder / f"{week.strftime('week %d %m %Y')}.png"
    #     )

    # for month in tqdm(months_dict.keys(), desc="Creating monthly graphs 📈 ..."):
    #     all_month_timestamps = [
    #         node.message.create_time
    #         for convo in months_dict[month]
    #         for node in convo.user_nodes + convo.assistant_nodes
    #         if node.message and node.message.create_time
    #     ]

    #     create_save_graph(
    #         all_month_timestamps, graph_folder / f"{month.strftime('%B')}.png"
    #     )

    print("Creating graph 📈 of prompts per day ...\n")

    # creating the graph of ALL messages
    all_timestamps = [
        node.message.create_time
        for convo in all_conversations
        for node in convo.user_nodes + convo.assistant_nodes
        if node.message and node.message.create_time
    ]

    create_save_graph(all_timestamps, graph_folder / "all conversations.png")

    print(f"\nDone 🎉 ! Check the output 📈 here : {graph_folder.as_uri()} 🔗\n")
    print("(more graphs 📈 will be added in the future)\n")

    # ----------- creating bar charts -------------

    # print("Creating bar charts 📊 ...\n")

    # bar_chart_folder = output_folder / "Bar Charts"
    # bar_chart_folder.mkdir(parents=True, exist_ok=True)

    # # bar chart logic here ...

    # print(f"\nDone 🎉 ! Check the output 📊 here : {bar_chart_folder.as_uri()} 🔗\n")

    # ----------- creating wordclouds -------------

    # print("Creating wordclouds 🔡☁️ ...\n")

    wordcloud_folder = output_folder / "Word Clouds"
    wordcloud_folder.mkdir(parents=True, exist_ok=True)

    font_path = Path("assets/fonts") / f"{configs['wordcloud']['font']}.ttf"

    colormap = configs["wordcloud"]["colormap"]

    for week in tqdm(weeks_dict.keys(), desc="Creating weekly wordclouds 🔡☁️ "):
        entire_week_text = "\n".join(
            convo.entire_user_text + "\n" + convo.entire_assistant_text
            for convo in weeks_dict[week]
        )

        create_save_wordcloud(
            entire_week_text,
            wordcloud_folder / f"{week.strftime('Week %Y %m %d')}.png",
            font_path=str(font_path),
            colormap=colormap,
        )

    for month in tqdm(months_dict.keys(), desc="Creating monthly wordclouds 🔡☁️ "):
        entire_month_text = "\n".join(
            convo.entire_user_text + "\n" + convo.entire_assistant_text
            for convo in months_dict[month]
        )

        create_save_wordcloud(
            entire_month_text,
            wordcloud_folder / f"{month.strftime('%B')}.png",
            font_path=str(font_path),
            colormap=colormap,
        )

    print(f"\nDone 🎉 ! Check the output 🔡☁️ here : {wordcloud_folder.as_uri()} 🔗\n")

    # ----------- creating heatmaps -------------

    # print("Creating heatmaps 🗺️ ...\n")

    # heatmap_folder = output_folder / "Heatmaps"
    # heatmap_folder.mkdir(parents=True, exist_ok=True)

    # # heatmap logic here ...

    # print(f"\nDone 🎉 ! Check the output 🗺️ here : {heatmap_folder.as_uri()} 🔗\n")

    # ------------- writing custom instructions --------------

    print("Writing custom instructions 📝 ...\n")

    ci_json_filepath = output_folder / "custom_instructions.json"

    custom_instructions: List[Dict[str, Any]] = []

    for convo in all_conversations:
        if not convo.custom_instructions:
            continue

        custom_instruction = {
            "chat_title": convo.title,
            "chat_link": convo.chat_link,
            "time": time.ctime(convo.create_time),
            "custom_instructions": convo.custom_instructions,
        }

        custom_instructions.append(custom_instruction)

    with open(ci_json_filepath, "w", encoding="utf-8") as file:
        json.dump(custom_instructions, file, indent=2)

    print(f"\nDone 🎉 ! Check the output 📝 here : {ci_json_filepath.as_uri()} 🔗\n")

    # ------------ Done ! saving configs ... -------------

    print("(Settings ⚙️ have been updated and saved to 'config.json')\n")

    print("ALL DONE 🎉🎉🎉 !\n")
    print(f"Explore the full gallery 🖼️ at: {output_folder.as_uri()} 🔗\n")
    print("I hope you enjoy the outcome 🤞.\n")
    print("If you appreciate it, kindly give the project a star 🌟 on GitHub :\n")
    print("➡️ https://github.com/mohamed-chs/chatgpt-history-export-to-md 🔗\n")

    with open("config.json", "w", encoding="utf-8") as file:
        json.dump(configs, file, indent=2)


if __name__ == "__main__":
    main()
