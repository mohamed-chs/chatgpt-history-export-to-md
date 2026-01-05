"""Tests for the CLI."""

from __future__ import annotations

from unittest.mock import patch

from typer.testing import CliRunner

from convoviz.cli import app

runner = CliRunner()

def test_main_with_args(mock_zip_file, tmp_path):
    """Test running with arguments calls run_process."""
    output_dir = tmp_path / "output"
    
    with patch("convoviz.cli.run_process") as mock_run:
        result = runner.invoke(app, ["--zip", str(mock_zip_file), "--output", str(output_dir)])
        
        assert result.exit_code == 0
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert call_args["zip_filepath"] == str(mock_zip_file)
        assert call_args["output_folder"] == str(output_dir)

def test_main_missing_zip_non_interactive():
    """Test failing when zip is missing in non-interactive mode (implied by default with no args? No, implied by args)."""
    # If we pass --output but no zip, it should fail in non-interactive mode if we can't find default.
    # But wait, logic says "If zip path is not provided... try to find default". 
    # If I mock `latest_zip` to fail, it should exit.
    
    with patch("convoviz.utils.latest_zip", side_effect=FileNotFoundError), \
         patch("convoviz.cli.run_process") as mock_run:
        result = runner.invoke(app, ["--output", "foo", "--no-interactive"])
        assert result.exit_code == 1
        mock_run.assert_not_called()

def test_interactive_flag_respected():
    """Test that --interactive flag triggers interactive mode."""
    with patch("convoviz.cli.run_interactive_config") as mock_interactive, \
         patch("convoviz.cli.run_process") as mock_run:
        
        # We need to return a valid config from interactive mock to avoid run_process failure if it checks
        mock_interactive.return_value = {
            "zip_filepath": "dummy.zip",
            "output_folder": "dummy_out",
            "wordcloud": {"font_path": "arial.ttf"}, 
            # add other necessary keys if validated strictly
        }
        
        result = runner.invoke(app, ["--interactive"])
        assert result.exit_code == 0
        mock_interactive.assert_called_once()
        mock_run.assert_called_once()
