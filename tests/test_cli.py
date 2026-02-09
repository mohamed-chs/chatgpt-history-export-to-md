"""Tests for the CLI."""

from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from convoviz.cli import app
from convoviz.config import OutputKind

runner = CliRunner()


@pytest.fixture(autouse=True)
def _isolate_user_config(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        "convoviz.config.get_user_config_path",
        lambda: tmp_path / "convoviz.toml",
    )


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
        patch("convoviz.cli.find_latest_valid_zip", return_value=None),
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


def test_interactive_ctrl_c_exits_cleanly() -> None:
    """Test Ctrl+C in interactive mode exits without running pipeline."""
    with (
        patch("convoviz.cli.run_interactive_config", side_effect=KeyboardInterrupt),
        patch("convoviz.cli.run_pipeline") as mock_run,
    ):
        result = runner.invoke(app, ["--interactive"])
        assert result.exit_code == 0
        mock_run.assert_not_called()


def test_outputs_flag_single(mock_zip_file: Path, tmp_path: Path) -> None:
    """Test --outputs flag with single value."""
    output_dir = tmp_path / "output"

    with patch("convoviz.cli.run_pipeline") as mock_run:
        result = runner.invoke(
            app,
            [
                "--zip",
                str(mock_zip_file),
                "--output",
                str(output_dir),
                "--outputs",
                "markdown",
            ],
        )

        assert result.exit_code == 0
        mock_run.assert_called_once()
        config = mock_run.call_args[0][0]
        assert config.outputs == {OutputKind.MARKDOWN}


def test_outputs_flag_multiple(mock_zip_file: Path, tmp_path: Path) -> None:
    """Test --outputs flag with multiple values."""
    output_dir = tmp_path / "output"

    with patch("convoviz.cli.run_pipeline") as mock_run:
        result = runner.invoke(
            app,
            [
                "--zip",
                str(mock_zip_file),
                "--output",
                str(output_dir),
                "--outputs",
                "markdown",
                "--outputs",
                "graphs",
            ],
        )

        assert result.exit_code == 0
        mock_run.assert_called_once()
        config = mock_run.call_args[0][0]
        assert config.outputs == {OutputKind.MARKDOWN, OutputKind.GRAPHS}


def test_outputs_flag_default_all(mock_zip_file: Path, tmp_path: Path) -> None:
    """Test that without --outputs flag, all outputs are selected."""
    output_dir = tmp_path / "output"

    with patch("convoviz.cli.run_pipeline") as mock_run:
        result = runner.invoke(
            app,
            ["--zip", str(mock_zip_file), "--output", str(output_dir)],
        )

        assert result.exit_code == 0
        mock_run.assert_called_once()
        config = mock_run.call_args[0][0]
        assert config.outputs == {
            OutputKind.MARKDOWN,
            OutputKind.GRAPHS,
            OutputKind.WORDCLOUDS,
        }


def test_timestamp_flag(mock_zip_file: Path, tmp_path: Path) -> None:
    """Test --timestamp flag sets prepend_timestamp_to_filename."""
    output_dir = tmp_path / "output"

    with patch("convoviz.cli.run_pipeline") as mock_run:
        result = runner.invoke(
            app,
            [
                "--zip",
                str(mock_zip_file),
                "--output",
                str(output_dir),
                "--timestamp",
            ],
        )

        assert result.exit_code == 0
        mock_run.assert_called_once()
        config = mock_run.call_args[0][0]
        assert config.prepend_timestamp_to_filename is True


def test_config_init_writes_default(tmp_path: Path) -> None:
    path = tmp_path / "config.toml"
    result = runner.invoke(app, ["config", "init", "--path", str(path)])
    assert result.exit_code == 0
    assert path.exists()
    assert "Convoviz default configuration" in path.read_text(encoding="utf-8")


def test_config_init_refuses_overwrite(tmp_path: Path) -> None:
    path = tmp_path / "config.toml"
    path.write_text("test", encoding="utf-8")
    result = runner.invoke(app, ["config", "init", "--path", str(path)])
    assert result.exit_code == 1
