# metadata_extraction.py

import os
from .utils import timestamp_to_str


def extract_metadata_values(messages_mapping, key_path):
    """Extract metadata values following the specified key path from the messages mapping."""
    keys = key_path.split(".")
    data = [
        value["message"]
        for _, value in messages_mapping.items()
        if value.get("message")
    ]
    for key in keys:
        data = [item.get(key, None) for item in data if item and key in item]
    return data[0] if data else "-"


def extract_metadata(conversation):
    """Extract metadata from a conversation."""
    messages_mapping = conversation.get("mapping", {})

    return {
        "id": conversation.get("conversation_id", ""),
        "title": conversation.get("title", ""),
        "create_time": conversation.get("create_time", ""),
        "update_time": conversation.get("update_time", ""),
        "total_messages": sum(
            1
            for _, value in messages_mapping.items()
            if value.get("message")
            and value["message"].get("content")
            and value["message"]["content"].get("content_type") == "text"
            and value["message"]["content"].get("parts")[0] != ""
        ),
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


def sanitize_yaml_value(value):
    """Escape problematic characters and wrap the value in quotes."""
    if value is None:
        return '"-"'
    if isinstance(value, int):
        return value
    # Escape double quotes and wrap the value in double quotes
    sanitized = '"' + str(value).replace('"', r"\"") + '"'
    return sanitized


def build_metadata_block(metadata):
    """Build a markdown block containing metadata."""
    return f"""---
"link": "https://chat.openai.com/c/{metadata["id"]}"
"title": {sanitize_yaml_value(metadata["title"])}
"time_created": {sanitize_yaml_value(timestamp_to_str(metadata["create_time"]))}
"time_updated": {sanitize_yaml_value(timestamp_to_str(metadata["update_time"]))}
"model": {sanitize_yaml_value(metadata["model_slug"])}
"total_messages": {sanitize_yaml_value(metadata["total_messages"])}
"code_messages": {sanitize_yaml_value(metadata["code_messages"])}
"message_types": {sanitize_yaml_value(', '.join(metadata["message_types"]))}
"custom_instructions":
  "about_user_message": {sanitize_yaml_value(metadata.get("about_user_message"))}
  "about_model_message": {sanitize_yaml_value(metadata.get("about_model_message"))}
---

"""


def save_conversation_to_md(
    title, conversation_text, title_occurrences, path, metadata
):
    """Save the conversation to a markdown file."""
    occurrence = title_occurrences[title]
    filename = title + (f" ({occurrence})" if occurrence > 0 else "")
    title_occurrences[title] += 1
    file_path = os.path.join(path, f"{filename}.md")

    metadata_block = build_metadata_block(metadata)

    try:
        with open(file_path, "w", encoding="utf-8") as md_file:
            md_file.write(metadata_block)
            md_file.write(f"# {title}\n\n")
            md_file.write(conversation_text)

        # Set the file's modification time based on 'Time Updated'
        os.utime(file_path, (metadata["update_time"], metadata["update_time"]))
    except FileNotFoundError:
        print(f"Directory not found: {path}. Please ensure it exists.")
    except PermissionError:
        print(f"Permission denied to write to {file_path}. Check your permissions.")
    except Exception as e:
        print(f"Failed to write to file {file_path}. Error: {e}")
