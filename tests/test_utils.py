"""Tests for the utils module."""

from convoviz.utils import (
    sanitize,
    validate_header,
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
