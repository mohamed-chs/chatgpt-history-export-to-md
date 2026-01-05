"""Main processing pipeline for convoviz."""

from pathlib import Path
from shutil import rmtree

from rich.console import Console

from convoviz.analysis.graphs import generate_week_barplots
from convoviz.analysis.wordcloud import generate_wordclouds
from convoviz.config import ConvovizConfig
from convoviz.exceptions import InvalidZipError
from convoviz.io.loaders import (
    find_latest_bookmarklet_json,
    load_collection_from_json,
    load_collection_from_zip,
)
from convoviz.io.writers import save_collection, save_custom_instructions

console = Console()


def run_pipeline(config: ConvovizConfig) -> None:
    """Run the main processing pipeline.

    Args:
        config: Complete configuration for the pipeline

    Raises:
        InvalidZipError: If the zip file is invalid
        ConfigurationError: If configuration is incomplete
    """
    if not config.zip_filepath:
        raise InvalidZipError("", reason="No zip file specified")

    zip_path = Path(config.zip_filepath)
    if not zip_path.exists():
        raise InvalidZipError(str(zip_path), reason="File does not exist")

    console.print("Loading data [bold yellow]📂[/bold yellow] ...\n")

    # Load main collection from zip
    collection = load_collection_from_zip(zip_path)

    # Try to merge bookmarklet data if available
    bookmarklet_json = find_latest_bookmarklet_json()
    if bookmarklet_json:
        console.print("Found bookmarklet download, loading [bold yellow]📂[/bold yellow] ...\n")
        try:
            bookmarklet_collection = load_collection_from_json(bookmarklet_json)
            collection.update(bookmarklet_collection)
        except Exception as e:
            console.print(
                f"[bold yellow]Warning:[/bold yellow] Failed to load bookmarklet data: {e}"
            )

    output_folder = config.output_folder

    # Clean and recreate output folder
    if output_folder.exists() and output_folder.is_dir():
        rmtree(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)

    # Save markdown files
    markdown_folder = output_folder / "Markdown"
    save_collection(
        collection,
        markdown_folder,
        config.conversation,
        config.message.author_headers,
        progress_bar=True,
    )
    console.print(
        f"\nDone [bold green]✅[/bold green] ! "
        f"Check the output [bold blue]📄[/bold blue] here: {markdown_folder.as_uri()} 🔗\n"
    )

    # Generate graphs
    graph_folder = output_folder / "Graphs"
    graph_folder.mkdir(parents=True, exist_ok=True)
    generate_week_barplots(
        collection,
        graph_folder,
        config.graph,
        progress_bar=True,
    )
    console.print(
        f"\nDone [bold green]✅[/bold green] ! "
        f"Check the output [bold blue]📈[/bold blue] here: {graph_folder.as_uri()} 🔗\n"
    )

    # Generate word clouds
    wordcloud_folder = output_folder / "Word Clouds"
    wordcloud_folder.mkdir(parents=True, exist_ok=True)
    generate_wordclouds(
        collection,
        wordcloud_folder,
        config.wordcloud,
        progress_bar=True,
    )
    console.print(
        f"\nDone [bold green]✅[/bold green] ! "
        f"Check the output [bold blue]🔡☁️[/bold blue] here: {wordcloud_folder.as_uri()} 🔗\n"
    )

    # Save custom instructions
    console.print("Writing custom instructions [bold blue]📝[/bold blue] ...\n")
    instructions_path = output_folder / "custom_instructions.json"
    save_custom_instructions(collection, instructions_path)
    console.print(
        f"\nDone [bold green]✅[/bold green] ! "
        f"Check the output [bold blue]📝[/bold blue] here: {instructions_path.as_uri()} 🔗\n"
    )

    console.print(
        "ALL DONE [bold green]🎉🎉🎉[/bold green] !\n\n"
        f"Explore the full gallery [bold yellow]🖼️[/bold yellow] at: {output_folder.as_uri()} 🔗\n\n"
        "I hope you enjoy the outcome 🤞.\n\n"
        "If you appreciate it, kindly give the project a star 🌟 on GitHub:\n\n"
        "➡️ https://github.com/mohamed-chs/chatgpt-history-export-to-md 🔗\n\n"
    )
