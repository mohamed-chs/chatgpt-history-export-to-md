"""
Main file for running the program from the command line."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from typing_extensions import Annotated

from .config import DEFAULT_USER_CONFIGS
from .interactive import run_interactive_config
from .process import run_process

app = typer.Typer(add_completion=False)


@app.callback(invoke_without_command=True)
def run(
    ctx: typer.Context,    zip_path: Annotated[
        Optional[Path],
        typer.Option(
            "--zip",
            "-z",
            help="Path to the ChatGPT export zip file.",
        ),
    ] = None,
    output_dir: Annotated[
        Optional[Path],
        typer.Option(
            "--output",
            "-o",
            help="Path to the output directory.",
        ),
    ] = None,
    interactive: Annotated[
        Optional[bool],
        typer.Option(
            "--interactive/--no-interactive",
            "-i/-I",
            help="Force interactive mode.",
        ),
    ] = None,
) -> None:
    """
    ChatGPT Data Visualizer 📊
    """
    if ctx.invoked_subcommand is not None:
        return

    # Start with default configs
    from copy import deepcopy
    configs = deepcopy(DEFAULT_USER_CONFIGS)

    # Override with CLI args if provided
    if zip_path:
        configs["zip_filepath"] = str(zip_path)
    if output_dir:
        configs["output_folder"] = str(output_dir)

    # Decision logic for interactive mode
    # 1. If --interactive is explicitly True, run interactive.
    # 2. If --no-interactive is explicitly False, run non-interactive.
    # 3. If None (default):
    #    - If zip_path is provided, assume non-interactive (batch mode).
    #    - Else, assume interactive.
    
    if interactive is True:
        mode_interactive = True
    elif interactive is False:
        mode_interactive = False
    else:
        # Default behavior
        mode_interactive = zip_path is None

    if mode_interactive:
        print("Welcome to ChatGPT Data Visualizer ✨📊!\n")
        configs = run_interactive_config(configs)
    else:
        # Non-interactive mode validation
        # If zip path is not provided/valid, we must fail (or try to find default, but batch mode should be explicit)
        if not configs["zip_filepath"]:
             # Try to find default
             from .utils import latest_zip
             try:
                 found = latest_zip()
                 print(f"No zip file specified, using latest found: {found}")
                 configs["zip_filepath"] = str(found)
             except FileNotFoundError:
                 print("Error: No zip file provided and none found in Downloads.")
                 raise typer.Exit(code=1)
        
        # We also need to resolve the font path if it's empty in defaults
        if not configs["wordcloud"]["font_path"]:
             from .utils import default_font_path
             configs["wordcloud"]["font_path"] = str(default_font_path())

    run_process(configs)

def main_entry() -> None:
    app()