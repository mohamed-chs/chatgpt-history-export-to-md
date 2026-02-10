"""Tests for the io/loaders module."""

import json
import time
from pathlib import Path
from zipfile import ZipFile

import orjson
import pytest

from convoviz.exceptions import InvalidZipError
from convoviz.io.loaders import (
    find_latest_valid_zip,
    find_script_export,
    load_collection,
    load_collection_from_json,
    load_collection_from_zip,
    validate_zip,
)


class TestLoadCollection:
    """Tests for the load_collection helper."""

    def test_load_from_directory(self, tmp_path: Path) -> None:
        """Test loading from a directory containing conversations.json."""
        dir_path = tmp_path / "data"
        dir_path.mkdir()
        json_path = dir_path / "conversations.json"
        json_path.write_text("[]")

        collection = load_collection(dir_path, tmp_path / "tmp")
        assert len(collection.conversations) == 0
        assert collection.source_path == dir_path

    def test_load_from_json_file(
        self, mock_conversations_json: Path, tmp_path: Path
    ) -> None:
        """Test loading from a JSON file."""
        collection = load_collection(mock_conversations_json, tmp_path / "tmp")
        assert len(collection.conversations) == 1
        assert collection.source_path == mock_conversations_json.parent

    def test_load_from_zip_file(self, mock_zip_file: Path, tmp_path: Path) -> None:
        """Test loading from a ZIP file."""
        collection = load_collection(mock_zip_file, tmp_path / "tmp")
        assert len(collection.conversations) == 1

    def test_invalid_directory_raises(self, tmp_path: Path) -> None:
        """Test that a directory without conversations.json raises error."""
        with pytest.raises(
            InvalidZipError, match=r"Directory must contain conversations.json"
        ):
            load_collection(tmp_path, tmp_path / "tmp")


class TestValidateZip:
    """Tests for the validate_zip function."""

    def test_valid_zip(self, mock_zip_file: Path) -> None:
        """Test validation of valid zip file."""
        assert validate_zip(mock_zip_file) is True

    def test_invalid_zip_no_conversations(self, tmp_path: Path) -> None:
        """Test validation of zip without conversations.json."""
        zip_path = tmp_path / "invalid.zip"
        with ZipFile(zip_path, "w") as zf:
            zf.writestr("other.txt", "content")

        assert validate_zip(zip_path) is False

    def test_nonexistent_file(self, tmp_path: Path) -> None:
        """Test validation of nonexistent file."""
        assert validate_zip(tmp_path / "nonexistent.zip") is False

    def test_not_a_zip(self, tmp_path: Path) -> None:
        """Test validation of non-zip file."""
        text_file = tmp_path / "file.txt"
        text_file.write_text("not a zip")
        assert validate_zip(text_file) is False


class TestLoadCollectionFromJson:
    """Tests for the load_collection_from_json function."""

    def test_load_valid_json(self, mock_conversations_json: Path) -> None:
        """Test loading a valid conversations JSON file."""
        collection = load_collection_from_json(mock_conversations_json)
        assert len(collection.conversations) == 1
        assert collection.conversations[0].title == "conversation 111"

    def test_load_invalid_json_raises(self, tmp_path: Path) -> None:
        """Invalid JSON should raise a decode error."""
        json_path = tmp_path / "invalid.json"
        json_path.write_text("{not: valid", encoding="utf-8")

        with pytest.raises(orjson.JSONDecodeError):
            load_collection_from_json(json_path)


class TestLoadCollectionFromZip:
    """Tests for the load_collection_from_zip function."""

    def test_load_valid_zip(self, mock_zip_file: Path, tmp_path: Path) -> None:
        """Test loading a valid zip file."""
        collection = load_collection_from_zip(mock_zip_file, tmp_path / "extracted")
        assert len(collection.conversations) == 1

    def test_load_invalid_zip(self, tmp_path: Path) -> None:
        """Test loading an invalid zip file raises error."""
        zip_path = tmp_path / "invalid.zip"
        with ZipFile(zip_path, "w") as zf:
            zf.writestr("other.txt", "content")

        with pytest.raises(InvalidZipError):
            load_collection_from_zip(zip_path, tmp_path / "extracted_invalid")


class TestLoadCollectionFromJsonFormats:
    """Tests for different JSON format support."""

    def test_load_wrapped_format(self, tmp_path: Path) -> None:
        """Test loading JSON with { conversations: [...] } wrapper."""
        data = {
            "conversations": [
                {
                    "title": "Test",
                    "create_time": 1704067200.0,
                    "update_time": 1704067200.0,
                    "mapping": {
                        "root": {
                            "id": "root",
                            "message": None,
                            "parent": None,
                            "children": [],
                        },
                    },
                    "current_node": "root",
                    "conversation_id": "test_id",
                },
            ],
        }
        json_path = tmp_path / "wrapped.json"
        json_path.write_text(json.dumps(data))

        collection = load_collection_from_json(json_path)
        assert len(collection.conversations) == 1
        assert collection.conversations[0].title == "Test"

    def test_source_path_set(self, mock_conversations_json: Path) -> None:
        """Test that source_path is set correctly."""
        collection = load_collection_from_json(mock_conversations_json)
        assert collection.source_path == mock_conversations_json.parent


class TestFindLatestValidZip:
    """Tests for the find_latest_valid_zip function."""

    def test_ignores_invalid_zips(self, tmp_path: Path) -> None:
        """Test that invalid ZIPs are ignored."""
        invalid_zip = tmp_path / "invalid.zip"
        with ZipFile(invalid_zip, "w") as zf:
            zf.writestr("other.txt", "content")

        valid_zip = tmp_path / "valid.zip"
        with ZipFile(valid_zip, "w") as zf:
            zf.writestr("conversations.json", "[]")

        result = find_latest_valid_zip(tmp_path)
        assert result == valid_zip

    def test_returns_none_when_no_valid_zips(self, tmp_path: Path) -> None:
        """Test that None is returned when no valid ZIP files exist."""
        invalid_zip = tmp_path / "invalid.zip"
        with ZipFile(invalid_zip, "w") as zf:
            zf.writestr("other.txt", "content")

        result = find_latest_valid_zip(tmp_path)
        assert result is None


class TestFindScriptExport:
    """Tests for the find_script_export function."""

    def test_finds_script_export_json(self, tmp_path: Path) -> None:
        """Test finding a script export JSON file."""
        export = tmp_path / "convoviz_export.json"
        export.write_text("[]")

        result = find_script_export(tmp_path)
        assert result == export

    def test_finds_script_export_zip(self, tmp_path: Path) -> None:
        """Test finding a script export ZIP file."""
        export = tmp_path / "convoviz_export.zip"
        export.write_text("[]")

        result = find_script_export(tmp_path)
        assert result == export

    def test_finds_most_recent_export(self, tmp_path: Path) -> None:
        """Test that the most recent export file is found."""
        old_file = tmp_path / "convoviz_export_old.json"
        old_file.write_text("[]")

        time.sleep(0.01)

        new_file = tmp_path / "convoviz_export_new.zip"
        new_file.write_text("[]")

        result = find_script_export(tmp_path)
        assert result == new_file

    def test_ignores_non_export_convoviz_files(self, tmp_path: Path) -> None:
        """Test that files with 'convoviz' but not starting with 'convoviz_export' are ignored."""
        # Contains convoviz but doesn't start with convoviz_export
        wrong_name = tmp_path / "my_convoviz.zip"
        wrong_name.write_text("[]")

        result = find_script_export(tmp_path)
        assert result is None

    def test_returns_none_when_none_found(self, tmp_path: Path) -> None:
        """Test that None is returned when no export files exist."""
        result = find_script_export(tmp_path)
        assert result is None

    def test_case_insensitive_matching(self, tmp_path: Path) -> None:
        """Test that matching is case-insensitive."""
        upper = tmp_path / "CONVOVIZ_EXPORT.json"
        upper.write_text("[]")

        result = find_script_export(tmp_path)
        assert result == upper
