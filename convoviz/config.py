"""Configuration definitions and defaults."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal, TypedDict

# default configs


class AuthorHeaders(TypedDict):
    """Type hint for the author headers configs."""

    system: str
    user: str
    assistant: str
    tool: str


class MessageConfigs(TypedDict):
    """Type hint for the message configs."""

    author_headers: AuthorHeaders


DEFAULT_MESSAGE_CONFIGS: MessageConfigs = {
    "author_headers": {
        "system": "### System",
        "user": "# Me",
        "assistant": "# ChatGPT",
        "tool": "### Tool output",
    },
}


class MarkdownConfigs(TypedDict):
    """Type hint for the markdown configs."""

    latex_delimiters: Literal["default", "dollars"]


class YAMLConfigs(TypedDict):
    """Type hint for the yaml configs."""

    title: bool
    tags: bool
    chat_link: bool
    create_time: bool
    update_time: bool
    model: bool
    used_plugins: bool
    message_count: bool
    content_types: bool
    custom_instructions: bool


class ConversationConfigs(TypedDict):
    """Type hint for the conversation configs."""

    markdown: MarkdownConfigs
    yaml: YAMLConfigs


DEFAULT_CONVERSATION_CONFIGS: ConversationConfigs = {
    "markdown": {"latex_delimiters": "default"},
    "yaml": {
        "title": True,
        "tags": False,
        "chat_link": True,
        "create_time": True,
        "update_time": True,
        "model": True,
        "used_plugins": True,
        "message_count": True,
        "content_types": True,
        "custom_instructions": True,
    },
}


class GraphKwargs(TypedDict, total=False):
    """Type hint for the graph configs."""


class WordCloudKwargs(TypedDict, total=False):
    """Type hint for the wordcloud configs."""

    font_path: str
    colormap: str
    custom_stopwords: str
    background_color: str | None
    mode: Literal["RGB", "RGBA"]
    include_numbers: bool
    width: int
    height: int


# We need to resolve paths dynamically or passed in, but for defaults we can keep them simple
# or handle the path resolution at runtime/in the interactive module.
# For now, I'll put placeholders or move the path logic here if it's dependency-free.
# The original utils had font_path logic. I'll move that helper here or keep it in utils.
# I'll keep the path resolution logic in utils for now to avoid circular deps if utils needs config.
# Wait, utils needed config types? No, utils DEFINED them.
# So I can move types here.

DEFAULT_WORDCLOUD_CONFIGS: WordCloudKwargs = {
    "font_path": "", # Resolved at runtime
    "colormap": "magma",
    "custom_stopwords": "use, file, ",
    "background_color": None,
    "mode": "RGBA",
    "include_numbers": False,
    "width": 1000,
    "height": 1000,
}


class AllConfigs(TypedDict):
    """Type hint for the user config JSON file."""

    zip_filepath: str
    output_folder: str
    message: MessageConfigs
    conversation: ConversationConfigs
    wordcloud: WordCloudKwargs
    graph: GraphKwargs
    node: dict[str, Any]
    conversation_set: dict[str, Any]


DEFAULT_USER_CONFIGS: AllConfigs = {
    "zip_filepath": "", # Resolved at runtime
    "output_folder": str(Path.home() / "Documents" / "ChatGPT Data"),
    "message": DEFAULT_MESSAGE_CONFIGS,
    "conversation": DEFAULT_CONVERSATION_CONFIGS,
    "wordcloud": DEFAULT_WORDCLOUD_CONFIGS,
    "graph": {},
    "node": {},
    "conversation_set": {},
}
