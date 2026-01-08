"""Tests for the exceptions module."""

from convoviz.exceptions import (
    ConfigurationError,
    ConvovizError,
    InvalidZipError,
    MessageContentError,
    RenderingError,
)


class TestConvovizError:
    """Tests for the base ConvovizError."""

    def test_is_exception(self) -> None:
        """Test that ConvovizError is an Exception."""
        assert issubclass(ConvovizError, Exception)


class TestInvalidZipError:
    """Tests for InvalidZipError."""

    def test_message_format(self) -> None:
        """Test error message format."""
        error = InvalidZipError("/path/to/file.zip")
        assert "/path/to/file.zip" in str(error)
        assert "missing conversations.json" in str(error)

    def test_custom_reason(self) -> None:
        """Test error with custom reason."""
        error = InvalidZipError("/path/to/file.zip", reason="corrupted")
        assert "corrupted" in str(error)

    def test_attributes(self) -> None:
        """Test error attributes."""
        error = InvalidZipError("/path/to/file.zip", reason="test")
        assert error.path == "/path/to/file.zip"
        assert error.reason == "test"


class TestConfigurationError:
    """Tests for ConfigurationError."""

    def test_message(self) -> None:
        """Test error message."""
        error = ConfigurationError("Invalid config")
        assert str(error) == "Invalid config"

    def test_with_field(self) -> None:
        """Test error with field attribute."""
        error = ConfigurationError("Invalid value", field="colormap")
        assert error.field == "colormap"


class TestRenderingError:
    """Tests for RenderingError."""

    def test_message(self) -> None:
        """Test error message."""
        error = RenderingError("Render failed")
        assert str(error) == "Render failed"

    def test_with_conversation_id(self) -> None:
        """Test error with conversation_id."""
        error = RenderingError("Failed", conversation_id="conv123")
        assert error.conversation_id == "conv123"


class TestMessageContentError:
    """Tests for MessageContentError."""

    def test_message_format(self) -> None:
        """Test error message format."""
        error = MessageContentError("msg123")
        assert "msg123" in str(error)
        assert error.message_id == "msg123"
