"""Tests for the io/loaders module."""

from pathlib import Path

import pytest

from convoviz.exceptions import InvalidZipError
from convoviz.io.loaders import (
    load_collection_from_json,
    load_collection_from_zip,
    validate_zip,
)


class TestValidateZip:
    """Tests for the validate_zip function."""

    def test_valid_zip(self, mock_zip_file: Path) -> None:
        """Test validation of valid zip file."""
        assert validate_zip(mock_zip_file) is True

    def test_invalid_zip_no_conversations(self, tmp_path: Path) -> None:
        """Test validation of zip without conversations.json."""
        from zipfile import ZipFile

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


class TestLoadCollectionFromZip:
    """Tests for the load_collection_from_zip function."""

    def test_load_valid_zip(self, mock_zip_file: Path) -> None:
        """Test loading a valid zip file."""
        collection = load_collection_from_zip(mock_zip_file)
        assert len(collection.conversations) == 1

    def test_load_invalid_zip(self, tmp_path: Path) -> None:
        """Test loading an invalid zip file raises error."""
        from zipfile import ZipFile

        zip_path = tmp_path / "invalid.zip"
        with ZipFile(zip_path, "w") as zf:
            zf.writestr("other.txt", "content")

        with pytest.raises(InvalidZipError):
            load_collection_from_zip(zip_path)
