"""YAML frontmatter rendering for conversations."""

from __future__ import annotations

import re
from datetime import datetime

from convoviz.config import YAMLConfig
from convoviz.models import Conversation

_TAG_SAFE_RE = re.compile(r"[^a-z0-9/_\-]+")


def _to_yaml_scalar(value: object) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, datetime):
        # Frontmatter consumers generally expect ISO 8601 strings
        return f'"{value.isoformat()}"'
    if isinstance(value, str):
        if "\n" in value:
            # Multiline: use a block scalar
            indented = "\n".join(f"  {line}" for line in value.splitlines())
            return f"|-\n{indented}"
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'

    # Fallback: stringify and quote
    escaped = str(value).replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def _to_yaml(value: object, indent: int = 0) -> str:
    pad = " " * indent

    if isinstance(value, dict):
        lines: list[str] = []
        for k, v in value.items():
            key = str(k)
            if isinstance(v, (dict, list)):
                lines.append(f"{pad}{key}:")
                lines.append(_to_yaml(v, indent=indent + 2))
            else:
                scalar = _to_yaml_scalar(v)
                # Block scalars already include newline + indentation
                if scalar.startswith("|-"):
                    lines.append(f"{pad}{key}: {scalar.splitlines()[0]}")
                    lines.extend(f"{pad}{line}" for line in scalar.splitlines()[1:])
                else:
                    lines.append(f"{pad}{key}: {scalar}")
        return "\n".join(lines)

    if isinstance(value, list):
        lines = []
        for item in value:
            if isinstance(item, (dict, list)):
                lines.append(f"{pad}-")
                lines.append(_to_yaml(item, indent=indent + 2))
            else:
                lines.append(f"{pad}- {_to_yaml_scalar(item)}")
        return "\n".join(lines)

    return f"{pad}{_to_yaml_scalar(value)}"


def _default_tags(conversation: Conversation) -> list[str]:
    tags: list[str] = ["chatgpt"]
    tags.extend(conversation.plugins)
    # Normalize to a tag-friendly form
    normalized: list[str] = []
    for t in tags:
        t2 = _TAG_SAFE_RE.sub("-", t.strip().lower()).strip("-")
        if t2 and t2 not in normalized:
            normalized.append(t2)
    return normalized


def render_yaml_header(conversation: Conversation, config: YAMLConfig) -> str:
    """Render the YAML frontmatter for a conversation.

    Args:
        conversation: The conversation to render
        config: YAML configuration specifying which fields to include

    Returns:
        YAML frontmatter string with --- delimiters, or empty string if no fields enabled
    """
    yaml_fields: dict[str, object] = {}

    if config.title:
        yaml_fields["title"] = conversation.title
    if config.tags:
        yaml_fields["tags"] = _default_tags(conversation)
    if config.chat_link:
        yaml_fields["chat_link"] = conversation.url
    if config.create_time:
        yaml_fields["create_time"] = conversation.create_time
    if config.update_time:
        yaml_fields["update_time"] = conversation.update_time
    if config.model:
        yaml_fields["model"] = conversation.model
    if config.used_plugins:
        yaml_fields["used_plugins"] = conversation.plugins
    if config.message_count:
        yaml_fields["message_count"] = conversation.message_count("user", "assistant")
    if config.content_types:
        yaml_fields["content_types"] = conversation.content_types
    if config.custom_instructions:
        yaml_fields["custom_instructions"] = conversation.custom_instructions

    if not yaml_fields:
        return ""

    body = _to_yaml(yaml_fields)
    return f"---\n{body}\n---\n"
