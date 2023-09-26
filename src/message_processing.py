"""Message Processing
    
Todo:
    - [x] Format more content data, for example : plugin use
"""

import json
from typing import Any, Optional

# Load the configuration JSON file
with open("config.json", encoding="utf-8") as f:
    config = json.load(f)


def extract_content_from_message(message: dict[str, Any]) -> Optional[str]:
    """Extract content from a message.

    Args:
        message (dict[str, Any]): The message dictionary.

    Returns:
        Optional[str]: The content extracted from the message.
    """

    content_data = message["content"]

    content: str | None = content_data.get("parts", [None])[0]
    if content is None:
        text = content_data.get("text")
        content = f"```python\n{text}\n```"

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

    role_mapping: dict[str, Any] = {
        "system": config["system_title"],
        "user": config["user_title"],
        "assistant": config["assistant_title"],
        "tool": config["tool_title"],
    }

    heading = (
        role_mapping[author_role]
        if author_role in role_mapping
        else "(message author unknown)"
    )

    content: str | None = extract_content_from_message(message)

    if "text" in message.get("content", {}):
        heading += "\n### Code Environment :"

    return f"# {heading}\n{content}\n\n"
