"""YAML frontmatter rendering for conversations."""

from __future__ import annotations

import re
from datetime import datetime
from typing import TYPE_CHECKING, Any

import yaml

if TYPE_CHECKING:
    from convoviz.config import YAMLConfig
    from convoviz.models import Conversation

from convoviz.utils import sanitize

_TAG_SAFE_RE = re.compile(r"[^a-z0-9/_\-]+")


def _normalize_yaml_value(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, dict):
        return {k: _normalize_yaml_value(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_normalize_yaml_value(item) for item in value]
    return value


class _YamlDumper(yaml.SafeDumper):
    _in_key = False

    def represent_mapping(
        self,
        tag: str,
        mapping: Any,
        flow_style: bool | None = None,
    ) -> yaml.nodes.MappingNode:
        value = []
        node = yaml.nodes.MappingNode(tag, value, flow_style=flow_style)
        if self.alias_key is not None:
            self.represented_objects[self.alias_key] = node
        best_style = True
        for item_key, item_value in mapping.items():
            self._in_key = True
            node_key = self.represent_data(item_key)
            self._in_key = False
            node_value = self.represent_data(item_value)
            if not (
                isinstance(node_key, yaml.nodes.ScalarNode) and node_key.style is None
            ):
                best_style = False
            if not (
                isinstance(node_value, yaml.nodes.ScalarNode)
                and node_value.style is None
            ):
                best_style = False
            value.append((node_key, node_value))
        if flow_style is None:
            if self.default_flow_style is not None:
                node.flow_style = self.default_flow_style
            else:
                node.flow_style = best_style
        return node


def _represent_str(dumper: _YamlDumper, data: str) -> yaml.nodes.ScalarNode:
    if getattr(dumper, "_in_key", False):
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style=None)
    if "\n" in data:
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style='"')


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


def render_yaml_header(
    conversation: Conversation,
    config: YAMLConfig,
) -> str:
    """Render the YAML frontmatter for a conversation.

    Args:
        conversation: The conversation to render
        config: YAML configuration specifying which fields to include
    Returns:
        YAML frontmatter string with --- delimiters, or empty string if
        no fields enabled
    """
    yaml_fields: dict[str, object] = {}

    if config.title:
        sanitized_title = sanitize(conversation.title)
        yaml_fields["title"] = sanitized_title
        if config.aliases and sanitized_title != conversation.title:
            yaml_fields["aliases"] = [conversation.title]
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
    if config.is_starred:
        yaml_fields["is_starred"] = conversation.is_starred
    if config.voice:
        yaml_fields["voice"] = conversation.voice
    if config.conversation_id:
        yaml_fields["conversation_id"] = conversation.conversation_id

    yaml_fields = {k: v for k, v in yaml_fields.items() if v is not None}

    if not yaml_fields:
        return ""

    normalized = _normalize_yaml_value(yaml_fields)
    _YamlDumper.add_representer(str, _represent_str)
    body = yaml.dump(
        normalized,
        Dumper=_YamlDumper,
        sort_keys=False,
        default_flow_style=False,
        allow_unicode=True,
    ).rstrip()
    return f"---\n{body}\n---\n"
