"""Main processing pipeline for convoviz."""

import logging
from pathlib import Path
from shutil import rmtree

from rich.console import Console

from convoviz.config import ConvovizConfig, OutputKind
from convoviz.exceptions import ConfigurationError, InvalidZipError
from convoviz.io.loaders import (
    find_latest_bookmarklet_json,
    load_collection_from_json,
    load_collection_from_zip,
)
from convoviz.io.writers import save_collection

console = Console()
logger = logging.getLogger(__name__)


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

    logger.info(f"Starting pipeline with input: {input_path}")
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
    logger.info(f"Loaded collection with {len(collection.conversations)} conversations")

    # Try to merge bookmarklet data if available
    bookmarklet_json = find_latest_bookmarklet_json()
    if bookmarklet_json:
        console.print("Found bookmarklet download, loading [bold yellow]📂[/bold yellow] ...\n")
        try:
            bookmarklet_collection = load_collection_from_json(bookmarklet_json)
            collection.update(bookmarklet_collection)
            logger.info("Merged bookmarklet data")
        except Exception as e:
            console.print(
                f"[bold yellow]Warning:[/bold yellow] Failed to load bookmarklet data: {e}"
            )

    output_folder = config.output_folder
    output_folder.mkdir(parents=True, exist_ok=True)

    # Determine which outputs are selected
    selected_outputs = config.outputs

    # Build mapping of output kind -> directory name
    output_dir_map: dict[OutputKind, str] = {
        OutputKind.MARKDOWN: "Markdown",
        OutputKind.GRAPHS: "Graphs",
        OutputKind.WORDCLOUDS: "Word-Clouds",
    }

    # Clean only specific sub-directories we manage (only for selected outputs)
    for output_kind, dir_name in output_dir_map.items():
        if output_kind not in selected_outputs:
            continue
        sub_dir = output_folder / dir_name
        if sub_dir.exists():
            # Never follow symlinks; just unlink them.
            if sub_dir.is_symlink():
                sub_dir.unlink()
            elif sub_dir.is_dir():
                rmtree(sub_dir)
            else:
                sub_dir.unlink()
        sub_dir.mkdir(exist_ok=True)

    # Save markdown files (if selected)
    if OutputKind.MARKDOWN in selected_outputs:
        markdown_folder = output_folder / "Markdown"
        save_collection(
            collection,
            markdown_folder,
            config.conversation,
            config.message.author_headers,
            folder_organization=config.folder_organization,
            progress_bar=True,
        )
        logger.info("Markdown generation complete")
        console.print(
            f"\nDone [bold green]✅[/bold green] ! "
            f"Check the output [bold blue]📄[/bold blue] here: {_safe_uri(markdown_folder)} 🔗\n"
        )

    # Generate graphs (if selected)
    if OutputKind.GRAPHS in selected_outputs:
        # Lazy import to allow markdown-only usage without matplotlib
        try:
            from convoviz.analysis.graphs import generate_graphs
        except ModuleNotFoundError as e:
            raise ConfigurationError(
                "Graph generation requires matplotlib. "
                'Reinstall with the [viz] extra: uv tool install "convoviz[viz]"'
            ) from e

        graph_folder = output_folder / "Graphs"
        graph_folder.mkdir(parents=True, exist_ok=True)
        generate_graphs(
            collection,
            graph_folder,
            config.graph,
            progress_bar=True,
        )
        logger.info("Graph generation complete")
        console.print(
            f"\nDone [bold green]✅[/bold green] ! "
            f"Check the output [bold blue]📈[/bold blue] here: {_safe_uri(graph_folder)} 🔗\n"
        )

    # Generate word clouds (if selected)
    if OutputKind.WORDCLOUDS in selected_outputs:
        # Lazy import to allow markdown-only usage without wordcloud/nltk
        try:
            from convoviz.analysis.wordcloud import generate_wordclouds
        except ModuleNotFoundError as e:
            raise ConfigurationError(
                "Word cloud generation requires wordcloud and nltk. "
                'Reinstall with the [viz] extra: uv tool install "convoviz[viz]"'
            ) from e

        wordcloud_folder = output_folder / "Word-Clouds"
        wordcloud_folder.mkdir(parents=True, exist_ok=True)
        generate_wordclouds(
            collection,
            wordcloud_folder,
            config.wordcloud,
            progress_bar=True,
        )
        logger.info("Wordcloud generation complete")
        console.print(
            f"\nDone [bold green]✅[/bold green] ! "
            f"Check the output [bold blue]🔡☁️[/bold blue] here: {_safe_uri(wordcloud_folder)} 🔗\n"
        )

    console.print(
        "ALL DONE [bold green]🎉🎉🎉[/bold green] !\n\n"
        f"Explore the full gallery [bold yellow]🖼️[/bold yellow] at: {_safe_uri(output_folder)} 🔗\n\n"
        "I hope you enjoy the outcome 🤞.\n\n"
        "If you appreciate it, kindly give the project a star 🌟 on GitHub:\n\n"
        "➡️ https://github.com/mohamed-chs/convoviz 🔗\n\n"
    )
