"""Tests for the process module."""

from __future__ import annotations

from unittest.mock import patch

from convoviz.config import DEFAULT_USER_CONFIGS
from convoviz.process import run_process


def test_run_process(mock_zip_file, tmp_path):
    """Test the main process flow."""
    output_dir = tmp_path / "output"
    
    # Setup minimal config
    configs = DEFAULT_USER_CONFIGS.copy()
    configs["zip_filepath"] = str(mock_zip_file)
    configs["output_folder"] = str(output_dir)
    # Ensure font path is valid or mocked. Defaults are usually fine if assets exist.
    
    # Mock long running tasks
    with patch("convoviz.process.generate_week_barplots") as mock_graphs, \
         patch("convoviz.process.generate_wordclouds") as mock_clouds:
        
        run_process(configs)
        
        # Check if directories were created
        assert output_dir.exists()
        assert (output_dir / "Markdown").exists()
        assert (output_dir / "Graphs").exists()
        assert (output_dir / "Word Clouds").exists()
        assert (output_dir / "custom_instructions.json").exists()
        
        # Check if markdown file was created
        # conversation title is "conversation 111", sanitized -> "conversation 111.md" (sanitize doesn't remove spaces)
        assert (output_dir / "Markdown" / "conversation 111.md").exists()
        
        mock_graphs.assert_called_once()
        mock_clouds.assert_called_once()
