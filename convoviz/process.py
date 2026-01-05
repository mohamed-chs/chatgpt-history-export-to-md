"Main processing logic for convoviz."

from __future__ import annotations

from pathlib import Path
from shutil import rmtree

from rich.console import Console

from .config import AllConfigs
from .long_runs import (
    generate_week_barplots,
    generate_wordclouds,
)
from .models import Conversation, ConversationSet, Message
from .utils import latest_bookmarklet_json

console = Console()


def run_process(configs: AllConfigs) -> None:
    """Run the main processing pipeline with the given configuration."""
    
    # Update global model configs
    # This is a legacy pattern from the original code using ClassVars
    Message.update_configs(configs["message"])
    Conversation.update_configs(configs["conversation"])

    console.print("Loading data [bold yellow]📂[/bold yellow] ...\n")

    zip_path = Path(configs["zip_filepath"])
    if not zip_path.exists():
        console.print(f"[bold red]Error:[/bold red] Zip file not found at {zip_path}")
        return

    entire_collection = ConversationSet.from_zip(zip_path)

    bkmrklet_json = latest_bookmarklet_json()
    if bkmrklet_json:
        console.print("Found bookmarklet download, loading [bold yellow]📂[/bold yellow] ...\n")
        try:
            bkmrklet_collection = ConversationSet.from_json(bkmrklet_json)
            entire_collection.update(bkmrklet_collection)
        except Exception as e:
            console.print(f"[bold red]Warning:[/bold red] Failed to load bookmarklet data: {e}")

    output_folder = Path(configs["output_folder"])

    # overwrite the output folder if it already exists
    if output_folder.exists() and output_folder.is_dir():
        rmtree(output_folder)

    output_folder.mkdir(parents=True, exist_ok=True)

    markdown_folder = output_folder / "Markdown"
    entire_collection.save(markdown_folder, progress_bar=True)

    console.print(f"\nDone [bold green]✅[/bold green] ! Check the output [bold blue]📄[/bold blue] here : {markdown_folder.as_uri()} 🔗\n")

    graph_folder = output_folder / "Graphs"
    graph_folder.mkdir(parents=True, exist_ok=True)

    generate_week_barplots(
        entire_collection,
        graph_folder,
        **configs["graph"],
        progress_bar=True,
    )

    console.print(f"\nDone [bold green]✅[/bold green] ! Check the output [bold blue]📈[/bold blue] here : {graph_folder.as_uri()} 🔗\n")
    console.print("(more graphs [bold blue]📈[/bold blue] will be added in the future ...)\n")

    wordcloud_folder = output_folder / "Word Clouds"
    wordcloud_folder.mkdir(parents=True, exist_ok=True)

    generate_wordclouds(
        entire_collection,
        wordcloud_folder,
        **configs["wordcloud"],
        progress_bar=True,
    )

    console.print(f"\nDone [bold green]✅[/bold green] ! Check the output [bold blue]🔡☁️[/bold blue] here : {wordcloud_folder.as_uri()} 🔗\n")

    console.print("Writing custom instructions [bold blue]📝[/bold blue] ...\n")

    cstm_inst_filepath = output_folder / "custom_instructions.json"
    entire_collection.save_custom_instructions(cstm_inst_filepath)

    console.print(f"\nDone [bold green]✅[/bold green] ! Check the output [bold blue]📝[/bold blue] here : {cstm_inst_filepath.as_uri()} 🔗\n")

    console.print(
        "ALL DONE [bold green]🎉🎉🎉[/bold green] !\n\n"
        f"Explore the full gallery [bold yellow]🖼️[/bold yellow] at: {output_folder.as_uri()} 🔗\n\n"
        "I hope you enjoy the outcome 🤞.\n\n"
        "If you appreciate it, kindly give the project a star 🌟 on GitHub :\n\n"
        "➡️ https://github.com/mohamed-chs/chatgpt-history-export-to-md 🔗\n\n",
    )
