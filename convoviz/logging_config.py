"""Logging configuration for convoviz."""

import logging
import tempfile
from pathlib import Path

from rich.logging import RichHandler


def setup_logging(
    verbosity: int = 0,
    log_file: Path | None = None,
) -> Path:
    """Set up logging configuration.

    Args:
        verbosity: Level of verbosity (0=WARNING, 1=INFO, 2=DEBUG)
        log_file: Path to log file. If None, a temporary file is created.

    Returns:
        Path to the log file used.
    """
    # clear existing handlers
    root_logger = logging.getLogger()
    root_logger.handlers.clear()

    # Determine log level for console
    if verbosity >= 2:
        console_level = logging.DEBUG
    elif verbosity >= 1:
        console_level = logging.INFO
    else:
        console_level = logging.WARNING

    # Console handler (Rich)
    console_handler = RichHandler(
        rich_tracebacks=True,
        markup=True,
        show_time=False,
        show_path=False,
    )
    console_handler.setLevel(console_level)

    # File handler
    if log_file is None:
        # Create temp file if not specified
        with tempfile.NamedTemporaryFile(prefix="convoviz_", suffix=".log", delete=False) as tf:
            log_file = Path(tf.name)

    # Ensure parent dir exists
    if not log_file.parent.exists():
        log_file.parent.mkdir(parents=True, exist_ok=True)

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)  # Always log DEBUG to file
    file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(file_formatter)

    # Configure root logger
    # We set root level to DEBUG so that the handlers can filter as they please
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    # Reduce noise from explicit libraries if necessary
    logging.getLogger("matplotlib").setLevel(logging.WARNING)
    logging.getLogger("PIL").setLevel(logging.WARNING)

    return log_file
