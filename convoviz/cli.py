"""Command-line interface for convoviz."""

import logging
from importlib.metadata import version as get_version
from pathlib import Path

import typer
from rich.console import Console
from rich.markup import escape

from convoviz.config import (
    FolderOrganization,
    OutputKind,
    get_user_config_path,
    load_config,
    write_default_config,
)
from convoviz.exceptions import ConfigurationError, InvalidZipError
from convoviz.interactive import run_interactive_config
from convoviz.io.loaders import find_latest_valid_zip
from convoviz.logging_config import setup_logging
from convoviz.pipeline import run_pipeline
from convoviz.utils import default_font_path, expand_path, validate_writable_dir

app = typer.Typer(
    add_completion=False,
    help="ChatGPT Data Visualizer 📊 - Convert and visualize your ChatGPT history",
)
console = Console()
config_app = typer.Typer(help="Manage convoviz configuration.")
app.add_typer(config_app, name="config")


def _version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        console.print(f"convoviz {get_version('convoviz')}")
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def run(
    ctx: typer.Context,
    input_path: str | None = typer.Option(
        None,
        "--input",
        "--zip",
        "-z",
        help="Path to the ChatGPT export ZIP, JSON file, or extracted directory.",
    ),
    output_dir: str | None = typer.Option(
        None,
        "--output",
        "-o",
        help="Path to the output directory.",
    ),
    outputs: list[OutputKind] | None = typer.Option(
        None,
        "--outputs",
        help="Output types to generate (repeatable). "
        "Options: markdown, graphs, wordclouds. "
        "If not specified, all outputs are generated.",
    ),
    flat: bool = typer.Option(
        False,
        "--flat",
        "-f",
        help="Put all markdown files in a single folder (disables date organization).",
    ),
    timestamp: bool = typer.Option(
        False,
        "--timestamp",
        "-t",
        help="Prepend conversation timestamp to the filename "
        "(e.g., 2024-03-21_15-30-05 - Title.md).",
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
    quiet: bool = typer.Option(
        False,
        "--quiet",
        "-q",
        help="Reduce console output (still logs to file).",
    ),
    config_path: str | None = typer.Option(
        None,
        "--config",
        help="Path to a TOML config file. Defaults to the user config if present.",
    ),
    _version: bool = typer.Option(
        False,
        "--version",
        "-V",
        help="Show version and exit.",
        callback=_version_callback,
        is_eager=True,
    ),
) -> None:
    """Convert ChatGPT export data to markdown and generate visualizations."""
    # Setup logging immediately
    log_path = setup_logging(verbose, log_file)
    logger = logging.getLogger("convoviz.cli")
    if not quiet:
        console.print(f"[dim]Logging to: {log_path}[/dim]")
    logger.debug(f"Logging initialized. Output: {log_path}")

    if ctx.invoked_subcommand is not None:
        return

    config_path_obj: Path | None = None
    if config_path:
        config_path_obj = expand_path(config_path)
        if not config_path_obj.exists() or not config_path_obj.is_file():
            console.print(
                f"[bold red]Error:[/bold red] Config file not found: {config_path_obj}"
            )
            raise typer.Exit(code=1)

    try:
        config = load_config(config_path_obj)
    except ConfigurationError as e:
        console.print(f"[bold red]Error:[/bold red] {escape(str(e))}")
        raise typer.Exit(code=1) from None

    # Override with CLI args
    if input_path:
        config.input_path = expand_path(input_path)
    if output_dir:
        config.output_folder = expand_path(output_dir)
    if quiet:
        config.quiet = True
    if outputs:
        config.outputs = set(outputs)
    if flat:
        config.folder_organization = FolderOrganization.FLAT
    if timestamp:
        config.prepend_timestamp_to_filename = True

    # Determine mode: interactive if explicitly requested or no input provided
    use_interactive = interactive if interactive is not None else (input_path is None)

    if use_interactive:
        if not config.quiet:
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
            latest = find_latest_valid_zip()
            if latest:
                if not config.quiet:
                    console.print(
                        f"No input specified, using latest zip found: {latest}"
                    )
                config.input_path = latest
            else:
                console.print(
                    "[bold red]Error:[/bold red] No input file provided and "
                    "none found in Downloads."
                )
                raise typer.Exit(code=1)

        # Validate the input (basic check)
        if not config.input_path.exists():
            console.print(
                "[bold red]Error:[/bold red] Input path does not exist: "
                f"{config.input_path}"
            )
            raise typer.Exit(code=1)

        # Set default font if not set
        if not config.wordcloud.font_path:
            config.wordcloud.font_path = default_font_path()

    try:
        validate_writable_dir(config.output_folder, create=True)
    except ConfigurationError as e:
        console.print(f"[bold red]Error:[/bold red] {escape(str(e))}")
        raise typer.Exit(code=1) from None

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


@config_app.command("init")
def init_config(
    path: Path | None = typer.Option(
        None,
        "--path",
        "-p",
        help="Write config to a custom path instead of the user config path.",
        dir_okay=False,
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Overwrite the config file if it already exists.",
    ),
) -> None:
    """Write the default config file to the user config location."""
    destination = path or get_user_config_path()
    try:
        written = write_default_config(destination, overwrite=force)
    except ConfigurationError as e:
        console.print(f"[bold red]Error:[/bold red] {escape(str(e))}")
        raise typer.Exit(code=1) from None

    console.print(f"[green]Wrote config:[/green] {written}")
