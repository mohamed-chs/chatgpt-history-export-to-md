"""Markdown rendering for conversations."""

import re
from collections.abc import Callable

from convoviz.config import AuthorHeaders, ConversationConfig
from convoviz.exceptions import MessageContentError
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


def render_obsidian_callout(
    content: str,
    title: str,
    callout_type: str = "NOTE",
    collapsed: bool = True,
) -> str:
    """Render content as an Obsidian collapsible callout.

    Syntax: > [!TYPE]+/- Title
    This is Obsidian-specific; on GitHub/standard markdown it renders as a blockquote.

    Args:
        content: The content to wrap
        title: The callout title
        callout_type: The callout type (NOTE, TIP, WARNING, etc.)
        collapsed: Whether to default to collapsed (-) or expanded (+)

    Returns:
        Markdown callout string
    """
    fold = "-" if collapsed else "+"
    lines = content.strip().split("\n")
    quoted_lines = [f"> {line}" for line in lines]
    return f"> [!{callout_type}]{fold} {title}\n" + "\n".join(quoted_lines)


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

    Args:
        node: The node to render
        headers: Configuration for author headers

    Returns:
        The header markdown string
    """
    if node.message is None:
        return ""

    return render_message_header(node.message.author.role, headers) + "\n"


# Content types that can be rendered as collapsible callouts in Obsidian
OBSIDIAN_COLLAPSIBLE_TYPES: dict[str, tuple[str, str]] = {
    # content_type: (callout_type, title)
    "reasoning_recap": ("NOTE", "🧠 AI Reasoning"),
    "thoughts": ("NOTE", "💭 AI Thoughts"),
}


def render_node(
    node: Node,
    headers: AuthorHeaders,
    use_dollar_latex: bool = False,
    asset_resolver: Callable[[str], str | None] | None = None,
    flavor: str = "standard",
) -> str:
    """Render a complete node as markdown.

    Args:
        node: The node to render
        headers: Configuration for author headers
        use_dollar_latex: Whether to convert LaTeX delimiters to dollars
        asset_resolver: Function to resolve asset IDs to paths
        flavor: Markdown flavor ("standard" or "obsidian")

    Returns:
        Complete markdown string for the node
    """
    if node.message is None:
        return ""

    content_type = node.message.content.content_type

    # For Obsidian flavor, render certain hidden types as collapsible callouts
    # No separator (---) since these are visually distinct and may appear consecutively
    if flavor == "obsidian" and content_type in OBSIDIAN_COLLAPSIBLE_TYPES:
        try:
            text = node.message.text
        except MessageContentError:
            text = ""

        if text.strip():
            callout_type, title = OBSIDIAN_COLLAPSIBLE_TYPES[content_type]
            callout = render_obsidian_callout(
                content=text,
                title=title,
                callout_type=callout_type,
                collapsed=True,
            )
            return f"\n{callout}\n"

    if node.message.is_hidden:
        return ""

    header = render_node_header(node, headers)

    # Get and process content
    try:
        text = node.message.text
    except MessageContentError:
        # Some message types only contain non-text parts; those still may have images.
        text = ""

    content = close_code_blocks(text)
    content = f"\n{content}\n" if content else ""
    if use_dollar_latex:
        content = replace_latex_delimiters(content)

    # Append images if resolver is provided and images exist
    if asset_resolver and node.message.images:
        for image_id in node.message.images:
            rel_path = asset_resolver(image_id)
            if rel_path:
                # Using standard markdown image syntax.
                # Obsidian handles this well.
                content += f"\n![Image]({rel_path})\n"

    return f"\n{header}{content}\n---\n"


def _ordered_nodes(conversation: Conversation) -> list[Node]:
    """Return nodes in a deterministic depth-first traversal order.

    ChatGPT exports store nodes in a mapping; dict iteration order is not a
    reliable semantic ordering. For markdown output, we traverse from roots.
    """
    mapping = conversation.node_mapping
    roots = sorted((n for n in mapping.values() if n.parent is None), key=lambda n: n.id)

    visited: set[str] = set()
    ordered: list[Node] = []

    def dfs(node: Node) -> None:
        if node.id in visited:
            return
        visited.add(node.id)
        ordered.append(node)
        for child in node.children_nodes:
            dfs(child)

    for root in roots:
        dfs(root)

    # Include any disconnected/orphan nodes deterministically at the end.
    for node in sorted(mapping.values(), key=lambda n: n.id):
        dfs(node)

    return ordered


def render_conversation(
    conversation: Conversation,
    config: ConversationConfig,
    headers: AuthorHeaders,
    asset_resolver: Callable[[str], str | None] | None = None,
) -> str:
    """Render a complete conversation as markdown.

    Args:
        conversation: The conversation to render
        config: Conversation rendering configuration
        headers: Configuration for author headers
        asset_resolver: Function to resolve asset IDs to paths

    Returns:
        Complete markdown document string
    """
    use_dollar_latex = config.markdown.latex_delimiters == "dollars"
    flavor = config.markdown.flavor

    # Start with YAML header
    markdown = render_yaml_header(conversation, config.yaml)

    # Render message nodes in a deterministic traversal order.
    for node in _ordered_nodes(conversation):
        if node.message:
            markdown += render_node(
                node,
                headers,
                use_dollar_latex,
                asset_resolver=asset_resolver,
                flavor=flavor,
            )

    return markdown
