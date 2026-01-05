"""Custom exceptions for convoviz."""


class ConvovizError(Exception):
    """Base exception for all convoviz errors."""


class InvalidZipError(ConvovizError):
    """Raised when a ZIP file is invalid or missing conversations.json."""

    def __init__(self, path: str, reason: str = "missing conversations.json") -> None:
        self.path = path
        self.reason = reason
        super().__init__(f"Invalid ZIP file '{path}': {reason}")


class ConfigurationError(ConvovizError):
    """Raised for configuration-related errors."""

    def __init__(self, message: str, field: str | None = None) -> None:
        self.field = field
        super().__init__(message)


class RenderingError(ConvovizError):
    """Raised when rendering fails."""

    def __init__(self, message: str, conversation_id: str | None = None) -> None:
        self.conversation_id = conversation_id
        super().__init__(message)


class MessageContentError(ConvovizError):
    """Raised when message content cannot be extracted."""

    def __init__(self, message_id: str) -> None:
        self.message_id = message_id
        super().__init__(f"No valid content found in message: {message_id}")


class FileNotFoundError(ConvovizError):
    """Raised when a required file is not found."""

    def __init__(self, path: str, file_type: str = "file") -> None:
        self.path = path
        self.file_type = file_type
        super().__init__(f"{file_type.capitalize()} not found: {path}")
