"""Message Processing

Attributes:
    config (dict[str, Any]): Configuration loaded from "config.json", providing 
    default titles and other settings.

Functions:
    determine_heading(author_role: Optional[str]) -> str:
        Determines a heading based on the author's role, referring to `config`.

    format_code(content_data: dict[str, Any]) -> Optional[str]:
        Formats content data containing Python code as markdown.

    extract_content_from_message(message: dict[str, Any]) -> Optional[str]:
        Extracts content (normal or Python code) from a given message.

    format_message_as_md(message: dict[str, Any]) -> str:
        Converts a message dictionary into a markdown formatted string.

Note:
    This module assumes the presence of a 'config.json' in the same directory, 
    which should be in valid JSON format.
    
Todo:
    - Format more content data, for example : plugin use
"""

import json
from typing import Any, Optional

# Load the configuration JSON file
with open("config.json", encoding="utf-8") as f:
    config = json.load(f)


def determine_heading(author_role: Optional[str]) -> str:
    """Determine the heading based on the author's role.

    Args:
        author_role (Optional[str]): The role of the author.

    Returns:
        str: A version of the author's role based on a configuration file.
    """

    role_mapping: dict[str, Any] = {
        "system": config.get("system_title", "System"),
        "user": config.get("user_title", "User"),
        "assistant": config.get("assistant_title", "Assistant"),
        "tool": config.get("tool_title", "Tool"),
    }

    # Determine the heading based on the role mapping
    if author_role in role_mapping:
        return role_mapping[author_role]

    return author_role.capitalize() if author_role else "(other)"


def format_code(content_data: dict[str, Any]) -> Optional[str]:
    """Format content data containing Python code as markdown.

    Args:
        content_data (dict[str, Any]): The content data dictionary.

    Returns:
        Optional[str]: Formatted Python code as markdown or None if not present.
    """

    text: Any | None = content_data.get("text")
    return f"```python\n{text}\n```" if text else None


def extract_content_from_message(message: dict[str, Any]) -> Optional[str]:
    """Extract content from a message.

    Args:
        message (dict[str, Any]): The message dictionary.

    Returns:
        Optional[str]: The content extracted from the message.
    """

    content_data = message.get("content", {})

    content: str | None = content_data.get("parts", [None])[0]
    if content is None:
        content = format_code(content_data)

    return content


def format_message_as_md(message: dict[str, Any]) -> str:
    """Format a message as markdown.

    Args:
        message (dict[str, Any]): The message dictionary.

    Returns:
        str: The message formatted as markdown.
    """

    if not message or not message.get("author"):
        return ""

    author_role = message["author"].get("role")
    if author_role == "system":
        return ""

    heading: str = determine_heading(author_role)
    content: str | None = extract_content_from_message(message)

    if "text" in message.get("content", {}):
        heading += "\n### Code Environment :"

    return f"# {heading}\n{content}\n\n"
