"""Main processing pipeline for convoviz."""

import logging
from pathlib import Path

from rich.console import Console

from convoviz.config import ConvovizConfig, OutputKind
from convoviz.exceptions import ConfigurationError, InvalidZipError
from convoviz.io.loaders import (
    cleanup_temp_dirs,
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
    if not config.quiet:
        console.print(f"Loading data from {input_path} [bold yellow]📂[/bold yellow] ...\n")

    output_dir_map: dict[OutputKind, str] = {
        OutputKind.MARKDOWN: "Markdown",
        OutputKind.GRAPHS: "Graphs",
        OutputKind.WORDCLOUDS: "Wordclouds",
    }

    try:
        # Load collection based on input type
        if input_path.is_dir():
            # Check for conversations.json inside
            json_path = input_path / "conversations.json"
            if not json_path.exists():
                raise InvalidZipError(
                    str(input_path), reason="Directory must contain conversations.json"
                )
            collection = load_collection_from_json(json_path)
        elif input_path.suffix.lower() == ".json":
            collection = load_collection_from_json(input_path)
        else:
            # Assume zip
            collection = load_collection_from_zip(input_path)
        logger.info(f"Loaded collection with {len(collection.conversations)} conversations")

        # Try to merge script export if explicitly specified
        if config.bookmarklet_path:
            script_path = config.bookmarklet_path
            if not config.quiet:
                console.print(
                    "Merging convoviz script export: "
                    f"[bold yellow]{script_path}[/bold yellow] ...\n"
                )
            try:
                if script_path.suffix.lower() == ".json":
                    script_collection = load_collection_from_json(script_path)
                else:
                    script_collection = load_collection_from_zip(script_path)

                collection.update(script_collection)
                logger.info(f"Merged script data from {script_path}")
            except Exception as e:
                console.print(
                    f"[bold yellow]Warning:[/bold yellow] Failed to load script export data: {e}"
                )

        output_folder = config.output_folder
        output_folder.mkdir(parents=True, exist_ok=True)

        # Determine which outputs are selected
        selected_outputs = config.outputs
        if (
            not selected_outputs
            and not config.export_canvas
            and not config.export_custom_instructions
        ):
            if not config.quiet:
                console.print(
                    "[bold yellow]Warning:[/bold yellow] "
                    "No outputs selected and no extra exports enabled. Nothing to do."
                )
            return

        # Clean only specific sub-directories we manage (only for selected outputs)
        for output_kind, dir_name in output_dir_map.items():
            if output_kind not in selected_outputs:
                continue
            sub_dir = output_folder / dir_name
            sub_dir.mkdir(parents=True, exist_ok=True)

        # Save markdown files (if selected)
        if OutputKind.MARKDOWN in selected_outputs:
            markdown_folder = output_folder / output_dir_map[OutputKind.MARKDOWN]
            save_collection(
                collection,
                markdown_folder,
                config.conversation,
                config.message.author_headers,
                folder_organization=config.folder_organization,
                prepend_timestamp=config.prepend_timestamp_to_filename,
                progress_bar=not config.quiet,
            )

            logger.info("Markdown generation complete")
            if not config.quiet:
                console.print(
                    f"\nDone [bold green]✅[/bold green] ! "
                    f"Check the output [bold blue]📄[/bold blue] here: {_safe_uri(markdown_folder)} 🔗\n"
                )

        # Save collection-level metadata if requested
        if config.export_custom_instructions:
            from convoviz.io import save_custom_instructions

            save_custom_instructions(collection, output_folder / "custom_instructions.json")
            logger.info("Custom instructions exported")
            if not config.quiet:
                console.print(
                    "Custom instructions saved to "
                    f"[bold blue]{_safe_uri(output_folder / 'custom_instructions.json')}[/bold blue]\n"
                )

        # Extract Canvas documents if requested
        if config.export_canvas:
            from convoviz.io import save_canvas_documents

            count = save_canvas_documents(collection, output_folder)
            if count > 0:
                logger.info(f"Extracted {count} Canvas documents")
                if not config.quiet:
                    console.print(
                        f"Canvas documents saved to [bold blue]{_safe_uri(output_folder / 'canvas')}[/bold blue]\n"
                    )

        # Generate graphs (if selected)
        if OutputKind.GRAPHS in selected_outputs:
            # Lazy import to allow markdown-only usage without matplotlib
            try:
                from convoviz.analysis.graphs import generate_graphs
            except ModuleNotFoundError as e:
                raise ConfigurationError(
                    "Graph generation requires matplotlib. "
                    'Install with `pip install "convoviz[viz]"` '
                    'or `uv pip install "convoviz[viz]"`.'
                ) from e

            graph_folder = output_folder / output_dir_map[OutputKind.GRAPHS]
            graph_folder.mkdir(parents=True, exist_ok=True)
            generate_graphs(
                collection,
                graph_folder,
                config.graph,
                progress_bar=not config.quiet,
            )
            logger.info("Graph generation complete")
            if not config.quiet:
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
                    'Install with `pip install "convoviz[viz]"` '
                    'or `uv pip install "convoviz[viz]"`.'
                ) from e

            wordcloud_folder = output_folder / output_dir_map[OutputKind.WORDCLOUDS]
            wordcloud_folder.mkdir(parents=True, exist_ok=True)
            generate_wordclouds(
                collection,
                wordcloud_folder,
                config.wordcloud,
                progress_bar=not config.quiet,
            )
            logger.info("Wordcloud generation complete")
            if not config.quiet:
                console.print(
                    f"\nDone [bold green]✅[/bold green] ! "
                    f"Check the output [bold blue]🔡☁️[/bold blue] here: {_safe_uri(wordcloud_folder)} 🔗\n"
                )

        if not config.quiet:
            console.print(
                "ALL DONE [bold green]🎉🎉🎉[/bold green] !\n\n"
                f"Explore the full gallery [bold yellow]🖼️[/bold yellow] at: {_safe_uri(output_folder)} 🔗\n\n"
                "I hope you enjoy the outcome 🤞.\n\n"
                "If you appreciate it, kindly give the project a star ⭐ on GitHub:\n\n"
                "➡️ https://github.com/mohamed-chs/convoviz 🔗\n\n"
            )
    finally:
        cleanup_temp_dirs()
