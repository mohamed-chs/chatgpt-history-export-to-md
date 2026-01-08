"""Tests for the pipeline module."""

from pathlib import Path
from unittest.mock import patch

import pytest

from convoviz.config import get_default_config
from convoviz.exceptions import InvalidZipError
from convoviz.pipeline import run_pipeline


def test_run_pipeline(mock_zip_file: Path, tmp_path: Path) -> None:
    """Test the main process flow."""
    output_dir = tmp_path / "output"

    config = get_default_config()
    config.input_path = mock_zip_file
    config.output_folder = output_dir

    # Mock long-running tasks
    with (
        patch("convoviz.analysis.graphs.generate_graphs") as mock_graphs,
        patch("convoviz.analysis.wordcloud.generate_wordclouds") as mock_clouds,
        patch("convoviz.pipeline.generate_graphs", mock_graphs),
        patch("convoviz.pipeline.generate_wordclouds", mock_clouds),
    ):
        run_pipeline(config)

        # Check if directories were created
        assert output_dir.exists()
        assert (output_dir / "Markdown").exists()
        assert (output_dir / "Graphs").exists()
        assert (output_dir / "Word-Clouds").exists()
        assert (output_dir / "custom_instructions.json").exists()

        # Check if markdown file was created
        assert (output_dir / "Markdown" / "conversation 111.md").exists()


def test_run_pipeline_invalid_zip(tmp_path: Path) -> None:
    """Test that run_pipeline raises InvalidZipError for invalid zip."""
    config = get_default_config()
    config.input_path = tmp_path / "nonexistent.zip"

    with pytest.raises(InvalidZipError):
        run_pipeline(config)


def test_run_pipeline_no_zip() -> None:
    """Test that run_pipeline raises error when no zip specified."""
    config = get_default_config()
    config.input_path = None

    with pytest.raises(InvalidZipError):
        run_pipeline(config)
