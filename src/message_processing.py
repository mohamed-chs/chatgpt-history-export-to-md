"""Message Processing
    
Todo:
    - [x] Format more content data, for example : plugin use
"""

from typing import Any, Dict, Optional, Union


def extract_content_from_message(message: Dict[str, Any]) -> Optional[str]:
    """Extract content from a message.

    Args:
        message (dict[str, Any]): The message dictionary.

    Returns:
        Optional[str]: The content extracted from the message.
    """

    content_data = message["content"]

    content: Union[str, None] = content_data.get("parts", [None])[0]
    if content is None:
        text = content_data.get("text")
        content = f"```python\n{text}\n```"

    return content


def format_message_as_md(message: Dict[str, Any], roles: Dict[str, str]) -> str:
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

    role_mapping: Dict[str, Any] = {
        "system": roles["system_title"],
        "user": roles["user_title"],
        "assistant": roles["assistant_title"],
        "tool": roles["tool_title"],
    }

    heading = (
        role_mapping[author_role]
        if author_role in role_mapping
        else "(message author unknown)"
    )

    content: Union[str, None] = extract_content_from_message(message)

    if "text" in message.get("content", {}):
        heading += "\n### Code Environment :"

    return f"# {heading}\n{content}\n\n"
