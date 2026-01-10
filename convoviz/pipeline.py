"""Main processing pipeline for convoviz."""

from pathlib import Path
from shutil import rmtree

from rich.console import Console

from convoviz.analysis.graphs import generate_graphs
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


def _safe_uri(path: Path) -> str:
    """Best-effort URI for printing.

    ``Path.as_uri()`` requires an absolute path; users often provide relative
    output paths, so we resolve first and fall back to string form.
    """
    try:
        return path.resolve().as_uri()
    except Exception:
        return str(path)


def run_pipeline(config: ConvovizConfig) -> None:
    """Run the main processing pipeline.

    Args:
        config: Complete configuration for the pipeline

    Raises:
        InvalidZipError: If the input is invalid
        ConfigurationError: If configuration is incomplete
    """
    if not config.input_path:
        raise InvalidZipError("", reason="No input path specified")

    input_path = Path(config.input_path)
    if not input_path.exists():
        raise InvalidZipError(str(input_path), reason="File does not exist")

    console.print(f"Loading data from {input_path} [bold yellow]📂[/bold yellow] ...\n")

    # Load collection based on input type
    if input_path.is_dir():
        # Check for conversations.json inside
        json_path = input_path / "conversations.json"
        if not json_path.exists():
            raise InvalidZipError(
                str(input_path), reason="Directory must contain conversations.json"
            )
        collection = load_collection_from_json(json_path)
    elif input_path.suffix == ".json":
        collection = load_collection_from_json(input_path)
    else:
        # Assume zip
        collection = load_collection_from_zip(input_path)

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
    output_folder.mkdir(parents=True, exist_ok=True)

    # Clean only specific sub-directories we manage
    managed_dirs = ["Markdown", "Graphs", "Word-Clouds"]
    for d in managed_dirs:
        sub_dir = output_folder / d
        if sub_dir.exists():
            # Never follow symlinks; just unlink them.
            if sub_dir.is_symlink():
                sub_dir.unlink()
            elif sub_dir.is_dir():
                rmtree(sub_dir)
            else:
                sub_dir.unlink()
        sub_dir.mkdir(exist_ok=True)

    # Clean specific files we manage
    managed_files = ["custom_instructions.json"]
    for f in managed_files:
        managed_file = output_folder / f
        if managed_file.exists():
            if managed_file.is_symlink() or managed_file.is_file():
                managed_file.unlink()
            elif managed_file.is_dir():
                rmtree(managed_file)
            else:
                managed_file.unlink()

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
        f"Check the output [bold blue]📄[/bold blue] here: {_safe_uri(markdown_folder)} 🔗\n"
    )

    # Generate graphs
    graph_folder = output_folder / "Graphs"
    graph_folder.mkdir(parents=True, exist_ok=True)
    generate_graphs(
        collection,
        graph_folder,
        config.graph,
        progress_bar=True,
    )
    console.print(
        f"\nDone [bold green]✅[/bold green] ! "
        f"Check the output [bold blue]📈[/bold blue] here: {_safe_uri(graph_folder)} 🔗\n"
    )

    # Generate word clouds
    wordcloud_folder = output_folder / "Word-Clouds"
    wordcloud_folder.mkdir(parents=True, exist_ok=True)
    generate_wordclouds(
        collection,
        wordcloud_folder,
        config.wordcloud,
        progress_bar=True,
    )
    console.print(
        f"\nDone [bold green]✅[/bold green] ! "
        f"Check the output [bold blue]🔡☁️[/bold blue] here: {_safe_uri(wordcloud_folder)} 🔗\n"
    )

    # Save custom instructions
    console.print("Writing custom instructions [bold blue]📝[/bold blue] ...\n")
    instructions_path = output_folder / "custom_instructions.json"
    save_custom_instructions(collection, instructions_path)
    console.print(
        f"\nDone [bold green]✅[/bold green] ! "
        f"Check the output [bold blue]📝[/bold blue] here: {_safe_uri(instructions_path)} 🔗\n"
    )

    console.print(
        "ALL DONE [bold green]🎉🎉🎉[/bold green] !\n\n"
        f"Explore the full gallery [bold yellow]🖼️[/bold yellow] at: {_safe_uri(output_folder)} 🔗\n\n"
        "I hope you enjoy the outcome 🤞.\n\n"
        "If you appreciate it, kindly give the project a star 🌟 on GitHub:\n\n"
        "➡️ https://github.com/mohamed-chs/chatgpt-history-export-to-md 🔗\n\n"
    )
