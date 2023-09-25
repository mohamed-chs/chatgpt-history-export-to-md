"""Metadata Extraction

The module performs various tasks:
    - Loading a configuration file to aid in metadata extraction.
    - Extracting specific metadata values from a nested structure.
    - Sanitizing values to be used in YAML format.
    - Building markdown blocks for metadata.
    - Saving the conversation and its associated metadata to a markdown file.

Attributes:
    config (dict): Configuration loaded from the 'config.json' file. Determines
    specific behaviors and settings for metadata extraction and saving.

Functions:
    - extract_metadata_values: Retrieve specific metadata from nested mappings.
    - extract_metadata: Extracts essential metadata from a conversation.
    - sanitize_yaml_value: Ensures values are correctly formatted for YAML.
    - build_metadata_block: Constructs a markdown block for metadata.
    - save_conversation_to_md: Save conversation data and metadata to a markdown file.

Todo:
    - Support different formats beyond markdown
    - Extract "invoked_plugin" names
"""

import json
import os
from typing import Any

from .utils import replace_delimiters
from .utils import timestamp_to_str as tts

# Load the configuration JSON file
with open("config.json", encoding="utf-8") as file:
    config = json.load(file)


def extract_metadata_values(
    messages_mapping: dict[str, dict[str, Any]], key_path: str
) -> str | Any:
    """Extract metadata values from a mapping using the specified key path.

    Args:
        messages_mapping (dict[str, dict[str, Any]]): Mapping of messages to extract metadata from
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
        "used_plugins": list(
            set(
                value["message"]["metadata"]["invoked_plugin"]["namespace"]
                for _, value in messages_mapping.items()
                if value.get("message")
                and value["message"].get("metadata")
                and value["message"]["metadata"].get("invoked_plugin")
            )
        ),
    }


def sanitize_yaml_value(value: Any) -> str | int:
    """Escape problematic characters and wrap the value in quotes.

    Args:
        value (Any): The value to sanitize, to be included in the YAML header

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

    syv = sanitize_yaml_value

    block_parts: list[str] = ["---"]

    # longer custom instructions break the obsidian frontmatter.
    custom_instructions = json.dumps(f"""about_user_message: {syv(metadata.get('about_user_message'))}
        about_model_message: {syv(metadata.get('about_model_message'))}""")

    metadata_mapping: dict[str, str] = {
        "chat_link": f'chat_link: "https://chat.openai.com/c/{metadata["id"]}"',
        "title": f"title: {syv(metadata['title'])}",
        "time_created": f"time_created: {syv(tts(metadata['create_time']))}",
        "time_updated": f"time_updated: {syv(tts(metadata['update_time']))}",
        "model": f"model: {syv(metadata['model_slug'])}",
        "total_messages": f"total_messages: {syv(metadata['total_messages'])}",
        "code_messages": f"code_messages: {syv(metadata['code_messages'])}",
        "message_types": f"message_types: {syv(', '.join(metadata['message_types']))}",
        "used_plugins": f"used_plugins: {syv(', '.join(metadata['used_plugins']))}",
        "custom_instructions": f"custom_instructions: {custom_instructions}",
    }

    for key, value in metadata_mapping.items():
        if config["yaml_header"].get(key):
            block_parts.append(value)

    block_parts.append("---\n\n")

    return "\n".join(block_parts)


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
        title_occurrences (dict[str, int]): A dictionary to keep track of same title occurrences
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
