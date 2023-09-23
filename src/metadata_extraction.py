# metadata_extraction.py

import json
import os
from typing import Any

from .utils import replace_delimiters, timestamp_to_str

# Load the configuration JSON file
with open("config.json") as f:
    config = json.load(f)


def extract_metadata_values(
    messages_mapping: dict[str, dict[str, Any]], key_path: str
) -> str | Any:
    """Extract metadata values from a mapping using the specified key path.

    Args:
        messages_mapping (dict[str, dict[str, Any]]): The mapping of messages to extract metadata from
        key_path (str): The dot-separated key path to follow in the extraction

    Returns:
        str | Any: The extracted metadata value, or "-" if no data is found
    """

    keys: list[str] = key_path.split(".")
    data: list[Any] = [
        value["message"]
        for _, value in messages_mapping.items()
        if value.get("message")
    ]
    for key in keys:
        data = [item.get(key, None) for item in data if item and key in item]
    return data[0] if data else "-"


def extract_metadata(conversation: dict[str, Any]) -> dict[str, Any]:
    """Extract metadata from a conversation dictionary.

    Args:
        conversation (dict[str, Any]): The conversation data

    Returns:
        dict[str, Any]: A dictionary with extracted metadata
    """

    messages_mapping = conversation.get("mapping", {})

    def get_text_content_messages(messages_mapping: dict[str, dict[str, Any]]) -> int:
        """Helper function to get text content messages count."""
        return sum(
            1
            for _, value in messages_mapping.items()
            if value.get("message")
            and value["message"].get("content")
            and value["message"]["content"].get("content_type") == "text"
            and value["message"]["content"].get("parts")[0] != ""
        )

    return {
        "id": conversation.get("conversation_id", ""),
        "title": conversation.get("title", ""),
        "create_time": conversation.get("create_time", ""),
        "update_time": conversation.get("update_time", ""),
        "total_messages": get_text_content_messages(messages_mapping),
        "code_messages": sum(
            1
            for _, value in messages_mapping.items()
            if value.get("message")
            and value["message"].get("content")
            and value["message"]["content"].get("content_type") == "code"
        ),
        "message_types": list(
            set(
                value["message"]["content"]["content_type"]
                for _, value in messages_mapping.items()
                if value.get("message") and value["message"].get("content")
            )
        ),
        "about_model_message": extract_metadata_values(
            messages_mapping, "metadata.user_context_message_data.about_model_message"
        ),
        "about_user_message": extract_metadata_values(
            messages_mapping, "metadata.user_context_message_data.about_user_message"
        ),
        "model_slug": extract_metadata_values(messages_mapping, "metadata.model_slug"),
    }


def sanitize_yaml_value(value: Any) -> str | int:
    """Sanitize a value for inclusion in YAML by escaping problematic characters and wrapping the value in quotes.

    Args:
        value (Any): The value to sanitize

    Returns:
        str | int: The sanitized value
    """

    if value is None:
        return '"-"'
    if isinstance(value, int):
        return value
    # Escape double quotes and wrap the value in double quotes
    sanitized: str = '"' + str(value).replace('"', r"\"") + '"'
    return sanitized


def build_metadata_block(metadata: dict[str, Any]) -> str:
    """Build a markdown block containing metadata information.

    Args:
        metadata (dict[str, Any]): The metadata dictionary

    Returns:
        str: A string representing a markdown block
    """

    return f"""---
chat_link: "https://chat.openai.com/c/{metadata["id"]}"
title: {sanitize_yaml_value(metadata["title"])}
time_created: {sanitize_yaml_value(timestamp_to_str(metadata["create_time"]))}
time_updated: {sanitize_yaml_value(timestamp_to_str(metadata["update_time"]))}
model: {sanitize_yaml_value(metadata["model_slug"])}
total_messages: {sanitize_yaml_value(metadata["total_messages"])}
code_messages: {sanitize_yaml_value(metadata["code_messages"])}
message_types: {sanitize_yaml_value(', '.join(metadata["message_types"]))}
custom_instructions:
  about_user_message: {sanitize_yaml_value(metadata.get("about_user_message"))}
  about_model_message: {sanitize_yaml_value(metadata.get("about_model_message"))}
---

"""


def save_conversation_to_md(
    title: str,
    conversation_text: str,
    title_occurrences: dict[str, int],
    path: str,
    metadata: dict[str, Any],
) -> None:
    """Save a conversation along with its metadata to a markdown file.

    Args:
        title (str): The title of the conversation
        conversation_text (str): The conversation text
        title_occurrences (dict[str, int]): A dictionary to keep track of title occurrences
        path (str): The path where the markdown file should be saved
        metadata (dict[str, Any]): The metadata dictionary
    """

    occurrence: int = title_occurrences[title]
    filename: str = title + (f" ({occurrence})" if occurrence > 0 else "")
    title_occurrences[title] += 1
    file_path: str = os.path.join(path, f"{filename}.md")

    metadata_block: str = build_metadata_block(metadata)

    try:
        with open(file_path, "w", encoding="utf-8") as md_file:
            md_file.write(metadata_block)
            md_file.write(f"# {title}\n\n")
            md_file.write(conversation_text)

        # Replace all the LaTeX bracket delimiters in the MD file with dollar sign ones.
        delimiters_default: bool = config.get("delimiters_default", True)
        if not delimiters_default:
            replace_delimiters(file_path)

        # Set the file's modification time based on 'Time Updated'
        os.utime(file_path, (metadata["update_time"], metadata["update_time"]))
    except FileNotFoundError:
        print(f"Directory not found: {path}. Please ensure it exists.")
    except PermissionError:
        print(f"Permission denied to write to {file_path}. Check your permissions.")
    except Exception as e:
        print(f"Failed to write to file {file_path}. Error: {e}")
