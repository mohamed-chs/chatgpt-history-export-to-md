"""YAML frontmatter rendering for conversations."""

from convoviz.config import YAMLConfig
from convoviz.models import Conversation


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

    lines = [f"{key}: {value}" for key, value in yaml_fields.items()]
    return f"---\n{chr(10).join(lines)}\n---\n"
