"""Tests for the pipeline module."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from convoviz.config import OutputKind, get_default_config
from convoviz.exceptions import ConfigurationError, InvalidZipError
from convoviz.pipeline import run_pipeline


def test_run_pipeline(mock_zip_file: Path, tmp_path: Path) -> None:
    """Test the main process flow."""
    output_dir = tmp_path / "output"

    config = get_default_config()
    config.input_path = mock_zip_file
    config.output_folder = output_dir

    # Mock long-running tasks (patching where they are actually called, since lazy import)
    with (
        patch("convoviz.analysis.graphs.generate_graphs") as mock_graphs,
        patch("convoviz.analysis.wordcloud.generate_wordclouds") as mock_clouds,
    ):
        run_pipeline(config)

        # Check mocks were called
        mock_graphs.assert_called_once()
        mock_clouds.assert_called_once()

        # Check if directories were created
        assert output_dir.exists()
        assert (output_dir / "Markdown").exists()
        assert (output_dir / "Graphs").exists()
        assert (output_dir / "Wordclouds").exists()

        # Check if markdown file was created (in date folder by default)
        # The mock conversation is dated July 29, 2023 -> 2023/07-July/
        assert (
            output_dir / "Markdown" / "2023" / "07-July" / "conversation 111.md"
        ).exists()

        # Check that index files were generated
        assert (output_dir / "Markdown" / "_index.md").exists()
        assert (output_dir / "Markdown" / "2023" / "_index.md").exists()
        assert (output_dir / "Markdown" / "2023" / "07-July" / "_index.md").exists()


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


def test_run_pipeline_markdown_only(mock_zip_file: Path, tmp_path: Path) -> None:
    """Test pipeline with markdown-only output selection."""
    output_dir = tmp_path / "output"

    config = get_default_config()
    config.input_path = mock_zip_file
    config.output_folder = output_dir
    config.outputs = {OutputKind.MARKDOWN}  # Only markdown

    run_pipeline(config)

    # Check markdown output was created
    assert output_dir.exists()
    assert (output_dir / "Markdown").exists()

    # Check that graphs and wordclouds were NOT created
    assert not (output_dir / "Graphs").exists()
    assert not (output_dir / "Wordclouds").exists()

    # Check markdown file exists
    assert (
        output_dir / "Markdown" / "2023" / "07-July" / "conversation 111.md"
    ).exists()


def test_run_pipeline_graphs_only(mock_zip_file: Path, tmp_path: Path) -> None:
    """Test pipeline with graphs-only output selection."""
    output_dir = tmp_path / "output"

    config = get_default_config()
    config.input_path = mock_zip_file
    config.output_folder = output_dir
    config.outputs = {OutputKind.GRAPHS}  # Only graphs

    run_pipeline(config)

    # Check graphs output was created
    assert output_dir.exists()
    assert (output_dir / "Graphs").exists()

    # Check that markdown and wordclouds were NOT created
    assert not (output_dir / "Markdown").exists()
    assert not (output_dir / "Wordclouds").exists()


def test_run_pipeline_no_outputs(mock_zip_file: Path, tmp_path: Path) -> None:
    """Test pipeline with no outputs selected."""
    output_dir = tmp_path / "output"

    config = get_default_config()
    config.input_path = mock_zip_file
    config.output_folder = output_dir
    config.outputs = set()  # No outputs

    run_pipeline(config)

    # Only the output folder should exist, no sub-directories
    assert output_dir.exists()
    assert not (output_dir / "Markdown").exists()
    assert not (output_dir / "Graphs").exists()
    assert not (output_dir / "Wordclouds").exists()


def test_run_pipeline_additive_output(mock_zip_file: Path, tmp_path: Path) -> None:
    """Test that existing files in output directory are preserved."""
    output_dir = tmp_path / "output"
    markdown_dir = output_dir / "Markdown"
    markdown_dir.mkdir(parents=True)

    # Create a "foreign" file that should be preserved
    preserved_file = markdown_dir / "preserved.txt"
    preserved_file.write_text("keep me")

    config = get_default_config()
    config.input_path = mock_zip_file
    config.output_folder = output_dir
    config.outputs = {OutputKind.MARKDOWN}

    run_pipeline(config)

    # Check that new files were created
    assert (markdown_dir / "2023" / "07-July" / "conversation 111.md").exists()

    # Check that the old file still exists
    assert preserved_file.exists()
    assert preserved_file.read_text() == "keep me"


def test_run_pipeline_extras_without_outputs(tmp_path: Path) -> None:
    """Extras should run even when outputs list is empty."""
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    conversations = [
        {
            "title": "Canvas + Instructions",
            "create_time": 1700000000.0,
            "update_time": 1700000000.0,
            "mapping": {
                "root": {
                    "id": "root",
                    "message": None,
                    "parent": None,
                    "children": ["sys", "canvas"],
                },
                "sys": {
                    "id": "sys",
                    "message": {
                        "id": "sys",
                        "author": {"role": "system", "metadata": {}},
                        "create_time": 1700000000.0,
                        "update_time": 1700000000.0,
                        "content": {
                            "content_type": "text",
                            "parts": ["Custom instructions"],
                        },
                        "status": "finished_successfully",
                        "end_turn": True,
                        "weight": 1.0,
                        "metadata": {
                            "is_user_system_message": True,
                            "user_context_message_data": {"about_user": "test"},
                        },
                        "recipient": "all",
                    },
                    "parent": "root",
                    "children": [],
                },
                "canvas": {
                    "id": "canvas",
                    "message": {
                        "id": "canvas",
                        "author": {"role": "assistant", "metadata": {}},
                        "create_time": 1700000000.0,
                        "update_time": 1700000000.0,
                        "content": {
                            "content_type": "text",
                            "parts": [
                                {"name": "doc", "type": "text/plain", "content": "hi"}
                            ],
                        },
                        "status": "finished_successfully",
                        "end_turn": True,
                        "weight": 1.0,
                        "metadata": {},
                        "recipient": "canmore.create_textdoc",
                    },
                    "parent": "root",
                    "children": [],
                },
            },
            "moderation_results": [],
            "current_node": "canvas",
            "conversation_id": "conv_extras",
        }
    ]
    (input_dir / "conversations.json").write_text(
        json.dumps(conversations), encoding="utf-8"
    )

    output_dir = tmp_path / "output"
    config = get_default_config()
    config.input_path = input_dir
    config.output_folder = output_dir
    config.outputs = set()
    config.export_canvas = True
    config.export_custom_instructions = True

    run_pipeline(config)

    assert (output_dir / "custom_instructions.json").exists()
    assert (output_dir / "canvas").exists()
    assert any((output_dir / "canvas").glob("*.txt"))


def test_run_pipeline_missing_graph_dependency(
    mock_zip_file: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output_dir = tmp_path / "output"
    config = get_default_config()
    config.input_path = mock_zip_file
    config.output_folder = output_dir
    config.outputs = {OutputKind.GRAPHS}

    real_import = __import__

    def fake_import(name, *args, **kwargs):
        if name == "convoviz.analysis.graphs":
            raise ModuleNotFoundError("matplotlib")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr("builtins.__import__", fake_import)

    with pytest.raises(ConfigurationError):
        run_pipeline(config)


def test_run_pipeline_missing_wordcloud_dependency(
    mock_zip_file: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output_dir = tmp_path / "output"
    config = get_default_config()
    config.input_path = mock_zip_file
    config.output_folder = output_dir
    config.outputs = {OutputKind.WORDCLOUDS}

    real_import = __import__

    def fake_import(name, *args, **kwargs):
        if name == "convoviz.analysis.wordcloud":
            raise ModuleNotFoundError("wordcloud")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr("builtins.__import__", fake_import)

    with pytest.raises(ConfigurationError):
        run_pipeline(config)
