"""Tests for logging configuration."""

import logging
from pathlib import Path

from convoviz.logging_config import setup_logging


def _cleanup_convoviz_handlers() -> None:
    root_logger = logging.getLogger()
    for handler in list(root_logger.handlers):
        if getattr(handler, "_convoviz_handler", False):
            root_logger.removeHandler(handler)


def test_setup_logging_creates_file(tmp_path: Path) -> None:
    log_path = tmp_path / "convoviz.log"
    result = setup_logging(log_file=log_path)
    assert result == log_path
    assert log_path.exists()
    _cleanup_convoviz_handlers()


def test_setup_logging_replaces_handlers(tmp_path: Path) -> None:
    log_path = tmp_path / "convoviz.log"
    setup_logging(log_file=log_path)
    first_handlers = [
        h
        for h in logging.getLogger().handlers
        if getattr(h, "_convoviz_handler", False)
    ]

    setup_logging(log_file=log_path)
    second_handlers = [
        h
        for h in logging.getLogger().handlers
        if getattr(h, "_convoviz_handler", False)
    ]

    assert len(second_handlers) == 2
    assert len(first_handlers) == 2
    _cleanup_convoviz_handlers()
