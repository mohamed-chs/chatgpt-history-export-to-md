"""Command-line interface for convoviz."""

import logging
from pathlib import Path

import typer
from rich.console import Console
from rich.markup import escape

from convoviz.config import FolderOrganization, OutputKind, get_default_config
from convoviz.exceptions import ConfigurationError, InvalidZipError
from convoviz.interactive import run_interactive_config
from convoviz.io.loaders import find_latest_zip
from convoviz.logging_config import setup_logging
from convoviz.pipeline import run_pipeline
from convoviz.utils import default_font_path

app = typer.Typer(
    add_completion=False,
    help="ChatGPT Data Visualizer 📊 - Convert and visualize your ChatGPT history",
)
console = Console()


@app.callback(invoke_without_command=True)
def run(
    ctx: typer.Context,
    input_path: Path | None = typer.Option(
        None,
        "--input",
        "--zip",
        "-z",
        help="Path to the ChatGPT export zip file, JSON file, or extracted directory.",
        exists=True,
        file_okay=True,
        dir_okay=True,
    ),
    output_dir: Path | None = typer.Option(
        None,
        "--output",
        "-o",
        help="Path to the output directory.",
    ),
    outputs: list[OutputKind] | None = typer.Option(
        None,
        "--outputs",
        help="Output types to generate (repeatable). Options: markdown, graphs, wordclouds. "
        "If not specified, all outputs are generated.",
    ),
    flat: bool = typer.Option(
        False,
        "--flat",
        "-f",
        help="Put all markdown files in a single folder (disables date organization).",
    ),
    interactive: bool | None = typer.Option(
        None,
        "--interactive/--no-interactive",
        "-i/-I",
        help="Force interactive mode on or off.",
    ),
    verbose: int = typer.Option(
        0,
        "--verbose",
        "-v",
        help="Increase verbosity. Use -vv for debug.",
        count=True,
    ),
    log_file: Path | None = typer.Option(
        None,
        "--log-file",
        help="Path to log file. Defaults to a temporary file.",
    ),
) -> None:
    """Convert ChatGPT export data to markdown and generate visualizations."""
    # Setup logging immediately
    log_path = setup_logging(verbose, log_file)
    logger = logging.getLogger("convoviz.cli")
    console.print(f"[dim]Logging to: {log_path}[/dim]")
    logger.debug(f"Logging initialized. Output: {log_path}")

    if ctx.invoked_subcommand is not None:
        return

    # Start with default config
    config = get_default_config()

    # Override with CLI args
    if input_path:
        config.input_path = input_path
    if output_dir:
        config.output_folder = output_dir
    if outputs:
        config.outputs = set(outputs)
    if flat:
        config.folder_organization = FolderOrganization.FLAT

    # Determine mode: interactive if explicitly requested or no input provided
    use_interactive = interactive if interactive is not None else (input_path is None)

    if use_interactive:
        console.print("Welcome to ChatGPT Data Visualizer ✨📊!\n")
        try:
            config = run_interactive_config(config)
        except KeyboardInterrupt:
            console.print("\n[yellow]Cancelled by user.[/yellow]")
            raise typer.Exit(code=0) from None
    else:
        # Non-interactive mode: validate we have what we need
        if not config.input_path:
            # Try to find a default
            latest = find_latest_zip()
            if latest:
                console.print(f"No input specified, using latest zip found: {latest}")
                config.input_path = latest
            else:
                console.print(
                    "[bold red]Error:[/bold red] No input file provided and none found in Downloads."
                )
                raise typer.Exit(code=1)

        # Validate the input (basic check)
        if not config.input_path.exists():
            console.print(
                f"[bold red]Error:[/bold red] Input path does not exist: {config.input_path}"
            )
            raise typer.Exit(code=1)

        # Set default font if not set
        if not config.wordcloud.font_path:
            config.wordcloud.font_path = default_font_path()

    # Run the pipeline
    try:
        run_pipeline(config)
    except (InvalidZipError, ConfigurationError) as e:
        logger.error(f"Known error: {e}")
        console.print(f"[bold red]Error:[/bold red] {escape(str(e))}")
        raise typer.Exit(code=1) from None
    except Exception as e:
        logger.exception("Unexpected error occurred")
        console.print(f"[bold red]Unexpected error:[/bold red] {escape(str(e))}")
        console.print(f"[dim]See log file for details: {log_path}[/dim]")
        raise typer.Exit(code=1) from None


def main_entry() -> None:
    """Entry point for the CLI."""
    app()
