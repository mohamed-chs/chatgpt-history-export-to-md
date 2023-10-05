"""
Just a placeholder for now.
a bunch of classes and functions to handle conversations, messages, stats, etc.

object path : conversations.json -> conversation (one of the list items)
"""

import os
import re
import time
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from .node import Node

# from .node import Node

used_file_names: Set[str] = set()


def ensure_closed_code_blocks(string: str) -> str:
    """Ensure that all code blocks are closed."""
    # A code block can be opened with triple backticks, possibly followed by a language name.
    # It can only be closed however with triple backticks, with nothing else on the line.

    open_code_block = False

    lines = string.split("\n")

    for line in lines:
        if line.startswith("```") and not open_code_block:
            open_code_block = True
            continue

        if line == "```" and open_code_block:
            open_code_block = False

    if open_code_block:
        string += "\n```"

    return string


def replace_latex_delimiters(string: str) -> str:
    """Replace all the LaTeX bracket delimiters in the string with dollar sign ones."""

    string = re.sub(r"\\\[", "$$", string)
    string = re.sub(r"\\\]", "$$", string)
    string = re.sub(r"\\\(", "$", string)
    string = re.sub(r"\\\)", "$", string)

    return string


class Conversation:
    """Stores the conversation object from the conversations.json file."""

    def __init__(
        self,
        title: str,
        create_time: float,
        update_time: float,
        mapping: Dict[str, Any],
        moderation_results: List[Any],
        current_node: str,
        plugin_ids: Optional[List[str]],
        conversation_id: str,
        conversation_template_id: Optional[str],
        id: str,
        configuration: Optional[Dict[str, Any]] = None,
    ):
        self.title = title
        self.create_time = create_time
        self.update_time = update_time
        nodes: Dict[str, Node] = Node.tree_from_mapping(mapping)
        self.mapping = nodes
        self.moderation_results = moderation_results
        self.current_node = nodes[current_node]
        self.plugin_ids = plugin_ids
        self.conversation_id = conversation_id
        self.conversation_template_id = conversation_template_id
        self.id = id
        if configuration is None:
            self.configuration: Dict[str, Any] = {}

    @property
    def chat_link(self) -> str:
        """Chat URL.

        Links to the original chat, not a 'shared' one. Needs user's login to chat.openai.com.
        """
        return f"https://chat.openai.com/c/{self.id}"

    @property
    def main_branch_nodes(self) -> List[Node]:
        """List of all nodes that have a message in the current 'main' branch."""

        nodes: List[Node] = []
        curr_node = self.current_node
        curr_parent = curr_node.parent

        while curr_parent:
            if curr_node.message:
                curr_node.message.configuration = self.configuration.get("message", {})
                nodes.append(curr_node)
            curr_node = curr_parent
            curr_parent = curr_node.parent

        nodes.reverse()

        return nodes

    @property
    def all_nodes(self) -> List[Node]:
        """List of all nodes that have a message in the conversation, including all branches."""

        nodes: List[Node] = []
        for _, node in self.mapping.items():
            if node.message:
                message = node.message
                message.configuration = self.configuration.get("message", {})
                nodes.append(node)

        return nodes

    @property
    def has_multiple_branches(self) -> bool:
        """Check if the conversation has multiple branches."""
        return len(self.all_nodes) > len(self.main_branch_nodes)

    @property
    def leaf_count(self) -> int:
        """Number of leaves in the conversation."""
        return sum(1 for node in self.all_nodes if not node.children)

    @property
    def content_types(self) -> List[str]:
        """List of all content types in the conversation. (all branches)

        (e.g. text, code, execution_output, etc.)"""
        return list(
            set(node.message.content_type for node in self.all_nodes if node.message)
        )

    @property
    def message_count(self) -> int:
        """Number of 'user' and 'assistant' messages in the conversation. (all branches)"""
        return sum(
            1
            for node in self.all_nodes
            if node.message and node.message.author_role in ("user", "assistant")
        )

    @property
    def system_nodes(self) -> List[Node]:
        """List of all 'system' nodes in the conversation. (all branches)"""
        return [
            node
            for node in self.all_nodes
            if node.message and node.message.author_role == "system"
        ]

    @property
    def user_nodes(self) -> List[Node]:
        """List of all 'user' nodes in the conversation. (all branches)"""
        return [
            node
            for node in self.all_nodes
            if node.message and node.message.author_role == "user"
        ]

    @property
    def assistant_nodes(self) -> List[Node]:
        """List of all 'assistant' nodes in the conversation. (all branches)"""
        return [
            node
            for node in self.all_nodes
            if node.message and node.message.author_role == "assistant"
        ]

    @property
    def tool_nodes(self) -> List[Node]:
        """List of all 'tool' nodes in the conversation. (all branches)"""
        return [
            node
            for node in self.all_nodes
            if node.message and node.message.author_role == "tool"
        ]

    @property
    def entire_user_text(self) -> str:
        """Entire raw 'user' text in the conversation. (all branches)

        Useful for generating word clouds."""
        return "\n".join(
            node.message.content_text for node in self.user_nodes if node.message
        )

    @property
    def entire_assistant_text(self) -> str:
        """Entire raw 'assistant' text in the conversation. (all branches)

        Useful for generating word clouds."""
        return "\n".join(
            node.message.content_text for node in self.assistant_nodes if node.message
        )

    @property
    def model_slug(self) -> Optional[str]:
        """ChatGPT model used for the conversation."""
        return (
            self.assistant_nodes[0].message.model_slug
            if self.assistant_nodes and self.assistant_nodes[0].message
            else None
        )

    @property
    def used_plugins(self) -> Optional[List[str]]:
        """List of all plugins used in the conversation."""
        plugins: set[str] = set(
            node.message.metadata["invoked_plugin"]["namespace"]
            for node in self.assistant_nodes
            if node.message and node.message.metadata.get("invoked_plugin")
        )

        if len(plugins) > 0:
            return list(plugins)
        else:
            return None

    @property
    def custom_instructions(self) -> Optional[Dict[str, str]]:
        """Custom instructions used for the conversation."""
        if len(self.system_nodes) < 2:
            return None
        context_message = self.system_nodes[1].message
        if context_message and context_message.metadata.get(
            "is_user_system_message", None
        ):
            return context_message.metadata.get("user_context_message_data", None)

    @property
    def yaml_header(self) -> str:
        """YAML metadata header for the conversation."""
        yaml_config = self.configuration.get("yaml", {})

        yaml_map = {
            "title": self.title,
            "chat_link": self.chat_link,
            "create_time": time.ctime(self.create_time),
            "update_time": time.ctime(self.update_time),
            "model": self.model_slug,
            "used_plugins": self.used_plugins,
            "message_count": self.message_count,
            "content_types": self.content_types,
            "custom_instructions": self.custom_instructions,
        }

        yaml = "---\n"

        for key, value in yaml_map.items():
            if yaml_config.get(key, True):
                yaml += f"{key}: {value}\n"

        yaml += "---\n"

        return yaml

    def branch_indicator(self, node: Node) -> str:
        """Get the branch indicator for the given node."""
        if node in self.main_branch_nodes:
            return "(main branch ⎇)"
        else:
            return "(other branch ⎇)"

        # placeholder for now, to be implemented later

    @property
    def markdown(self) -> str:
        """Markdown formatted text of the conversation. (all branches)

        Included authors : user, assistant, tool"""
        markdown_config = self.configuration.get("markdown", {})
        latex_delimiters = markdown_config.get("latex_delimiters", "default")

        markdown = self.yaml_header

        for node in self.all_nodes:
            if node.message:
                content = ensure_closed_code_blocks(node.message.content_text)
                # prevent empty messages from taking up white space
                content = f"\n{content}\n" if content else ""
                if latex_delimiters == "dollar sign":
                    content = replace_latex_delimiters(content)
                markdown += f"""
{self.branch_indicator(node)}
{node.header}{content}{node.footer}
---
"""
        return markdown

    @property
    def stats(self) -> Dict[str, Any]:
        """Get diverse insightful stats on the conversation."""
        return {}

    @property
    def sanitized_title(self) -> str:
        """Sanitized title of the conversation, compatible with file names."""
        filename_pattern = re.compile(r'[<>:"/\\|?*\n\r\t\f\v]')
        return filename_pattern.sub("_", self.title) if self.title else "untitled"

    def save_to_dir(self, folder_path: Path) -> None:
        """Save the conversation to the given folder path."""

        base_file_name = f"{self.sanitized_title}.md"
        file_path = folder_path / base_file_name

        # Check if the file already exists in the memory set
        counter = 1
        while str(file_path) in used_file_names:
            new_file_name = f"{self.sanitized_title} ({counter}).md"
            file_path = folder_path / new_file_name
            counter += 1

        used_file_names.add(str(file_path))

        with open(file_path, "w", encoding="utf-8") as file:
            file.write(self.markdown)
        os.utime(file_path, (self.update_time, self.update_time))

    @property
    def start_of_year(self) -> datetime:
        """Start of year as a datetime object."""
        return datetime(datetime.fromtimestamp(self.create_time).year, 1, 1)

    @property
    def start_of_month(self) -> datetime:
        """Start of month as a datetime object."""
        return datetime(
            datetime.fromtimestamp(self.create_time).year,
            datetime.fromtimestamp(self.create_time).month,
            1,
        )

    @property
    def start_of_week(self) -> datetime:
        """Start of week as a datetime object."""
        start_of_week = datetime.fromtimestamp(self.create_time) - timedelta(
            days=datetime.fromtimestamp(self.create_time).weekday()
        )
        return start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)


# (ADD THESE AS METHODS TO THE CONVERSATION CLASS)


def group_by_week(
    conversations: List[Conversation],
) -> Dict[datetime, List[Conversation]]:
    """Group the conversations by week."""
    grouped: defaultdict[datetime, List[Conversation]] = defaultdict(list)

    for conversation in conversations:
        grouped[conversation.start_of_week].append(conversation)

    return dict(grouped)


def group_by_month(
    conversations: List[Conversation],
) -> Dict[datetime, List[Conversation]]:
    """Group the conversations by month."""
    grouped: defaultdict[datetime, List[Conversation]] = defaultdict(list)

    for conversation in conversations:
        grouped[conversation.start_of_month].append(conversation)

    return dict(grouped)


def group_by_year(
    conversations: List[Conversation],
) -> Dict[datetime, List[Conversation]]:
    """Group the conversations by year."""
    grouped: defaultdict[datetime, List[Conversation]] = defaultdict(list)

    for conversation in conversations:
        grouped[conversation.start_of_year].append(conversation)

    return dict(grouped)
