"""Tests for the CLI."""

from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from convoviz.cli import app

runner = CliRunner()


def test_main_with_args(mock_zip_file: Path, tmp_path: Path) -> None:
    """Test running with arguments calls run_pipeline."""
    output_dir = tmp_path / "output"

    with patch("convoviz.cli.run_pipeline") as mock_run:
        result = runner.invoke(
            app,
            ["--zip", str(mock_zip_file), "--output", str(output_dir)],
        )

        assert result.exit_code == 0
        mock_run.assert_called_once()
        config = mock_run.call_args[0][0]
        assert config.input_path == mock_zip_file
        assert config.output_folder == output_dir


def test_main_missing_zip_non_interactive() -> None:
    """Test failing when zip is missing in non-interactive mode."""
    with (
        patch("convoviz.cli.find_latest_zip", return_value=None),
        patch("convoviz.cli.run_pipeline") as mock_run,
    ):
        result = runner.invoke(app, ["--output", "foo", "--no-interactive"])
        assert result.exit_code == 1
        mock_run.assert_not_called()


def test_interactive_flag_respected() -> None:
    """Test that --interactive flag triggers interactive mode."""
    with (
        patch("convoviz.cli.run_interactive_config") as mock_interactive,
        patch("convoviz.cli.run_pipeline") as mock_run,
    ):
        # Return a valid config from interactive mock
        from convoviz.config import get_default_config

        mock_config = get_default_config()
        mock_config.input_path = Path("dummy.zip")
        mock_interactive.return_value = mock_config

        result = runner.invoke(app, ["--interactive"])
        assert result.exit_code == 0
        mock_interactive.assert_called_once()
        mock_run.assert_called_once()
