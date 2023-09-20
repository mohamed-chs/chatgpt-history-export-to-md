# message_processing.py

from typing import Any, Optional


def determine_heading(author_role: Optional[str]) -> str:
    """
    Determine the heading based on the author's role.

    Args:
    - author_role (Optional[str]): The role of the author.

    Returns:
    - str: A capitalized version of the author's role or "(other)" if not provided.
    """
    return author_role.capitalize() if author_role else "(other)"


def get_content_from_parts(content_data: dict[str, Any]) -> Optional[str]:
    """
    Extract the primary content from the 'parts' of content data, if available.

    Args:
    - content_data (dict[str, Any]): The content data dictionary.

    Returns:
    - Optional[str]: The primary content or None if not present.
    """
    return content_data.get("parts", [None])[0]


def format_python_script(content_data: dict[str, Any]) -> Optional[str]:
    """
    Format content data containing Python code as markdown.

    Args:
    - content_data (dict[str, Any]): The content data dictionary.

    Returns:
    - Optional[str]: Formatted Python code as markdown or None if not present.
    """
    text: Any | None = content_data.get("text")
    return f"```python\n{text}\n```" if text else None


def extract_content_from_message(message: dict[str, Any]) -> Optional[str]:
    """
    Extract content from a message.

    Args:
    - message (dict[str, Any]): The message dictionary.

    Returns:
    - Optional[str]: The content extracted from the message.
    """
    content_data = message.get("content", {})

    content: str | None = get_content_from_parts(content_data)
    if content is None:
        content = format_python_script(content_data)

    return content


def format_message_as_md(message: dict[str, Any]) -> str:
    """
    Format a message as markdown.

    Args:
    - message (dict[str, Any]): The message dictionary.

    Returns:
    - str: The message formatted as markdown.
    """
    if not message or not message.get("author"):
        return ""

    author_role = message["author"].get("role")
    if author_role == "system":
        return ""

    heading: str = determine_heading(author_role)
    content: str | None = extract_content_from_message(message)

    if "text" in message.get("content", {}):
        heading += "\n### Code Interpreter..."

    return f"# {heading}\n{content}\n\n"
