"""Markdown rendering for conversations."""

import re

from convoviz.config import AuthorHeaders, ConversationConfig
from convoviz.models import Conversation, Node
from convoviz.renderers.yaml import render_yaml_header


def close_code_blocks(text: str) -> str:
    """Ensure all code blocks in the text are properly closed.

    Args:
        text: Markdown text that may have unclosed code blocks

    Returns:
        Text with all code blocks properly closed
    """
    open_code_block = False
    lines = text.split("\n")

    for line in lines:
        if line.startswith("```") and not open_code_block:
            open_code_block = True
            continue
        if line == "```" and open_code_block:
            open_code_block = False

    if open_code_block:
        text += "\n```"

    return text


def replace_latex_delimiters(text: str) -> str:
    """Replace LaTeX bracket delimiters with dollar sign delimiters.

    Args:
        text: Text with \\[ \\] \\( \\) delimiters

    Returns:
        Text with $$ and $ delimiters
    """
    text = re.sub(r"\\\[", "$$", text)
    text = re.sub(r"\\\]", "$$", text)
    text = re.sub(r"\\\(", "$", text)
    return re.sub(r"\\\)", "$", text)


def code_block(text: str, lang: str = "python") -> str:
    """Wrap text in a markdown code block.

    Args:
        text: The code to wrap
        lang: The language for syntax highlighting

    Returns:
        Markdown code block string
    """
    return f"```{lang}\n{text}\n```"


def render_message_header(role: str, headers: AuthorHeaders) -> str:
    """Get the markdown header for a message author.

    Args:
        role: The author role (user, assistant, system, tool)
        headers: Configuration for author headers

    Returns:
        The markdown header string
    """
    header_map = {
        "system": headers.system,
        "user": headers.user,
        "assistant": headers.assistant,
        "tool": headers.tool,
    }
    return header_map.get(role, f"### {role.title()}")


def render_node_header(node: Node, headers: AuthorHeaders) -> str:
    """Render the header section of a node.

    Includes the node ID, parent link, and message author header.

    Args:
        node: The node to render
        headers: Configuration for author headers

    Returns:
        The header markdown string
    """
    if node.message is None:
        return ""

    parts = [f"###### {node.id}"]

    # Add parent link if parent has a message
    if node.parent_node and node.parent_node.message:
        parts.append(f"[parent ⬆️](#{node.parent_node.id})")

    parts.append(render_message_header(node.message.author.role, headers))

    return "\n".join(parts) + "\n"


def render_node_footer(node: Node) -> str:
    """Render the footer section of a node with child links.

    Args:
        node: The node to render

    Returns:
        The footer markdown string with child navigation links
    """
    if not node.children_nodes:
        return ""

    if len(node.children_nodes) == 1:
        return f"\n[child ⬇️](#{node.children_nodes[0].id})\n"

    links = " | ".join(
        f"[child {i + 1} ⬇️](#{child.id})" for i, child in enumerate(node.children_nodes)
    )
    return f"\n{links}\n"


def render_node(node: Node, headers: AuthorHeaders, use_dollar_latex: bool = False) -> str:
    """Render a complete node as markdown.

    Args:
        node: The node to render
        headers: Configuration for author headers
        use_dollar_latex: Whether to convert LaTeX delimiters to dollars

    Returns:
        Complete markdown string for the node
    """
    if node.message is None:
        return ""

    header = render_node_header(node, headers)

    # Get and process content
    try:
        content = close_code_blocks(node.message.text)
        content = f"\n{content}\n" if content else ""
        if use_dollar_latex:
            content = replace_latex_delimiters(content)
    except Exception:
        content = ""

    footer = render_node_footer(node)

    return f"\n{header}{content}{footer}\n---\n"


def render_conversation(
    conversation: Conversation, config: ConversationConfig, headers: AuthorHeaders
) -> str:
    """Render a complete conversation as markdown.

    Args:
        conversation: The conversation to render
        config: Conversation rendering configuration
        headers: Configuration for author headers

    Returns:
        Complete markdown document string
    """
    use_dollar_latex = config.markdown.latex_delimiters == "dollars"

    # Start with YAML header
    markdown = render_yaml_header(conversation, config.yaml)

    # Render all message nodes
    for node in conversation.all_message_nodes:
        if node.message:
            markdown += render_node(node, headers, use_dollar_latex)

    return markdown
