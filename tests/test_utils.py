"""Tests for the utils module."""

from pathlib import Path

import pytest

from convoviz.exceptions import ConfigurationError
from convoviz.utils import (
    deep_merge_dicts,
    expand_path,
    normalize_optional_path,
    sanitize,
    sanitize_title,
    validate_header,
    validate_writable_dir,
)


class TestSanitize:
    """Tests for the sanitize function."""

    def test_sanitize_normal_string(self) -> None:
        """Test sanitizing a normal string."""
        assert sanitize("Hello World") == "Hello World"

    def test_sanitize_with_special_chars(self) -> None:
        """Test sanitizing strings with special characters."""
        assert sanitize("Hello<World>") == "Hello_World_"
        assert sanitize("file:name") == "file_name"
        assert sanitize("path/to\\file") == "path_to_file"
        assert sanitize("test?query*") == "test_query_"

    def test_sanitize_with_newlines(self) -> None:
        """Test sanitizing strings with newlines."""
        assert sanitize("Hello\nWorld") == "Hello_World"
        assert sanitize("Hello\r\nWorld") == "Hello_World"

    def test_sanitize_empty_string(self) -> None:
        """Test sanitizing an empty string."""
        assert sanitize("") == "untitled"

    def test_sanitize_whitespace_only(self) -> None:
        """Test sanitizing whitespace-only string."""
        assert sanitize("   ") == "untitled"

    def test_sanitize_preserves_valid_chars(self) -> None:
        """Test that sanitize preserves valid characters."""
        assert sanitize("file-name_123") == "file-name_123"


class TestValidateHeader:
    """Tests for the validate_header function."""

    def test_valid_h1(self) -> None:
        """Test valid H1 header."""
        assert validate_header("# Title") is True

    def test_valid_h2(self) -> None:
        """Test valid H2 header."""
        assert validate_header("## Subtitle") is True

    def test_valid_h6(self) -> None:
        """Test valid H6 header."""
        assert validate_header("###### Small") is True

    def test_invalid_no_hash(self) -> None:
        """Test invalid header without hash."""
        assert validate_header("Title") is False

    def test_invalid_no_space(self) -> None:
        """Test invalid header without space after hash."""
        assert validate_header("#Title") is False

    def test_invalid_too_many_hashes(self) -> None:
        """Test invalid header with too many hashes."""
        assert validate_header("####### Too many") is False

    def test_invalid_empty(self) -> None:
        """Test empty string is invalid."""
        assert validate_header("") is False

    def test_invalid_hash_only(self) -> None:
        """Test hash-only string is invalid."""
        assert validate_header("#") is False


class TestSanitizeTitle:
    """Tests for the sanitize_title function."""

    def test_sanitize_title_strips_problem_chars(self) -> None:
        """Test sanitizing a title with problematic characters."""
        assert sanitize_title("My @Title: (Hello)") == "My Title Hello"

    def test_sanitize_title_preserves_valid_chars(self) -> None:
        """Test sanitize_title preserves allowed characters."""
        assert sanitize_title("Weird---Title__") == "Weird---Title__"

    def test_sanitize_title_empty(self) -> None:
        """Test sanitize_title returns untitled on empty result."""
        assert sanitize_title("$$$") == "untitled"


class TestDeepMergeDicts:
    """Tests for deep_merge_dicts."""

    def test_shallow_override(self) -> None:
        base = {"a": 1, "b": 2}
        override = {"b": 3}
        assert deep_merge_dicts(base, override) == {"a": 1, "b": 3}

    def test_nested_override(self) -> None:
        base = {"a": {"x": 1, "y": 2}, "b": 1}
        override = {"a": {"y": 99}}
        assert deep_merge_dicts(base, override) == {"a": {"x": 1, "y": 99}, "b": 1}


class TestPathNormalization:
    """Tests for path helpers."""

    def test_expand_path_env_and_home(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("CONVOVIZ_TEST", "abc")
        result = expand_path("~/$CONVOVIZ_TEST")
        assert str(result).endswith("/abc")

    def test_normalize_optional_path_none_or_empty(self) -> None:
        assert normalize_optional_path(None) is None
        assert normalize_optional_path("") is None
        assert normalize_optional_path("   ") is None

    def test_normalize_optional_path_expands(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("CONVOVIZ_TEST", "xyz")
        result = normalize_optional_path("$CONVOVIZ_TEST")
        assert isinstance(result, Path)
        assert result.name == "xyz"


class TestWritableDirChecks:
    """Tests for writable directory validation helpers."""

    def test_validate_writable_dir_creates(self, tmp_path: Path) -> None:
        target = tmp_path / "new" / "out"
        validate_writable_dir(target, create=True)
        assert target.exists()
        assert target.is_dir()

    def test_validate_writable_dir_existing(self, tmp_path: Path) -> None:
        target = tmp_path / "existing"
        target.mkdir()
        validate_writable_dir(target)

    def test_validate_writable_dir_does_not_create(self, tmp_path: Path) -> None:
        target = tmp_path / "new" / "out"
        validate_writable_dir(target, create=False)
        assert not target.exists()

    def test_validate_writable_dir_rejects_file(self, tmp_path: Path) -> None:
        target = tmp_path / "file.txt"
        target.write_text("nope", encoding="utf-8")
        with pytest.raises(ConfigurationError):
            validate_writable_dir(target)
