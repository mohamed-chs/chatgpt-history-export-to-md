"""Markdown rendering for conversations."""

import re
from collections.abc import Callable
from datetime import datetime
from typing import Any
from urllib.parse import quote

from convoviz.config import AuthorHeaders, ConversationConfig
from convoviz.exceptions import MessageContentError
from convoviz.models import Conversation, Node
from convoviz.renderers.yaml import render_yaml_header


def replace_citations(
    text: str,
    citations: list[dict[str, Any]] | None = None,
    citation_map: dict[str, dict[str, str | None]] | None = None,
    flavor: str = "standard",
) -> str:
    """Replace citation placeholders in text with markdown links.

    Supports two formats:
    1. Tether v4 (metadata.citations): Placed at specific indices (【...】 placeholders).
    2. Embedded (Tether v3?): Unicode markers citeturnXsearchY.

    Args:
        text: The original message text
        citations: List of tether v4 citation objects (start_ix/end_ix)
        citation_map: Map of internal citation IDs to metadata (turnXsearchY -> {title, url})
        flavor: Markdown flavor for link formatting ("standard", "obsidian", "pandoc")

    Returns:
        Text with all placeholders replaced by markdown links
    """
    # 1. Handle Tether v4 (Index-based replacements)
    if citations:
        # Sort citations by start_ix descending to replace safely from end
        sorted_citations = sorted(citations, key=lambda c: c.get("start_ix", 0), reverse=True)

        for cit in sorted_citations:
            start = cit.get("start_ix")
            end = cit.get("end_ix")
            meta = cit.get("metadata", {})

            if start is None or end is None:
                continue

            replacement = _format_link(meta.get("title"), meta.get("url"), flavor)

            # Only replace if strictly positive indices and bounds check
            if 0 <= start < end <= len(text):
                text = text[:start] + replacement + text[end:]

    # 2. Handle Embedded Citations (Regex-based)
    # Pattern: cite (key)+ 
    # Codepoints: \uE200 (Start), \uE202 (Sep), \uE201 (End)
    if citation_map is not None:
        pattern = re.compile(r"\uE200cite((?:\uE202[a-zA-Z0-9]+)+)\uE201")

        def replacer(match: re.Match) -> str:
            # Group 1 contains string like: turn0search18turn0search3
            # Split by separator \uE202 (first item will be empty string)
            raw_keys = match.group(1).split("\ue202")
            keys = [k for k in raw_keys if k]

            links = []
            for key in keys:
                if key in citation_map:
                    data = citation_map[key]
                    link = _format_link(data.get("title"), data.get("url"), flavor)
                    if link:
                        links.append(link)

            return "".join(links)

        text = pattern.sub(replacer, text)

    return text


def _format_link(title: str | None, url: str | None, flavor: str = "standard") -> str:
    """Format a title and URL into a concise markdown link."""
    if flavor in ("pandoc", "standard"):
        if title and url:
            return f" [{title}]({url})"
        if url:
            return f" [Source]({url})"
        if title:
            return f" {title}"
        return ""

    # Obsidian/wiki-style link variant
    if title and url:
        return f" [[{title}]({url})]"
    if url:
        return f" [[Source]({url})]"
    if title:
        return f" [{title}]"
    return ""


def close_code_blocks(text: str) -> str:
    """Ensure all code blocks in the text are properly closed.

    Args:
        text: Markdown text that may have unclosed code blocks

    Returns:
        Text with all code blocks properly closed
    """
    open_fences: list[tuple[str, int]] = []
    lines = text.split("\n")
    fence_pattern = re.compile(r"^[ \t]{0,3}(`{3,}|~{3,})(.*)$")

    for line in lines:
        match = fence_pattern.match(line)
        if not match:
            continue

        fence = match.group(1)
        rest = match.group(2)
        fence_char = fence[0]
        fence_len = len(fence)

        if open_fences:
            open_char, open_len = open_fences[-1]
            if fence_char == open_char and fence_len >= open_len and rest.strip() == "":
                open_fences.pop()
            continue

        open_fences.append((fence_char, fence_len))

    if open_fences:
        closures = "\n".join(f"{char * length}" for char, length in reversed(open_fences))
        text += f"\n{closures}"

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
    asset_resolver: Callable[[str, str | None], str | None] | None = None,
    flavor: str = "standard",
    citation_map: dict[str, dict[str, str | None]] | None = None,
    show_timestamp: bool = True,
    last_timestamp: datetime | None = None,
) -> str:
    """Render a complete node as markdown.

    Args:
        node: The node to render
        headers: Configuration for author headers
        use_dollar_latex: Whether to convert LaTeX delimiters to dollars
        asset_resolver: Function to resolve asset IDs to paths, optionally renaming them
        flavor: Markdown flavor ("standard", "obsidian", or "pandoc")
        citation_map: Global map of citations
        show_timestamp: Whether to show the message timestamp
        last_timestamp: The timestamp of the previous message (for conditional date display)
    """
    if node.message is None:
        return ""

    content_type = node.message.content.content_type

    # For Obsidian flavor, render certain hidden types as collapsible callouts
    # No separator (***) since these are visually distinct and may appear consecutively
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

    # Add timestamp if enabled and available
    timestamp_str = ""
    if show_timestamp and node.message.create_time:
        curr_time = node.message.create_time
        # Show full date if it's the first message or if the date has changed
        if last_timestamp is None or curr_time.date() != last_timestamp.date():
            timestamp_str = f"*{curr_time.strftime('%Y-%m-%d %H:%M:%S')}*\n"
        else:
            timestamp_str = f"*{curr_time.strftime('%H:%M:%S')}*\n"

    # Get and process content
    try:
        text = node.message.text
    except MessageContentError:
        # Some message types only contain non-text parts; those still may have images.
        text = ""

    # Process citations if present (Tether v4 metadata or Embedded v3)
    # Use global citation_map if provided, merging/falling back to local if needed.
    # Actually, local internal map is subset of global map if we aggregated correctly.
    # So we prefer the passed global map.
    effective_map = citation_map or node.message.internal_citation_map

    if node.message.metadata.citations or effective_map:
        text = replace_citations(
            text,
            citations=node.message.metadata.citations,
            citation_map=effective_map,
            flavor=flavor,
        )

    content = close_code_blocks(text)
    content = f"\n{content}\n" if content else ""
    if use_dollar_latex:
        content = replace_latex_delimiters(content)

    # Append images if resolver is provided and images exist
    if asset_resolver and node.message.images:
        # Build map of file-id -> desired name from metadata.attachments
        attachment_map = {}
        if node.message.metadata.attachments:
            for att in node.message.metadata.attachments:
                if (att_id := att.get("id")) and (name := att.get("name")):
                    attachment_map[att_id] = name

        for image_id in node.message.images:
            # Pass the desired name if we have one for this ID
            target_name = attachment_map.get(image_id)
            rel_path = asset_resolver(image_id, target_name)
            if rel_path:
                # URL-encode the path to handle spaces/special characters in Markdown links
                # We only encode the filename part if we want to be safe, but rel_path is "assets/..."
                # quote() by default doesn't encode / which is good.
                encoded_path = quote(rel_path)
                # Using standard markdown image syntax.
                # Obsidian handles this well.
                content += f"\n![Image]({encoded_path})\n"

    return f"\n{header}{timestamp_str}{content}\n***\n"


def _ordered_nodes_full(conversation: Conversation) -> list[Node]:
    """Return nodes in a deterministic depth-first traversal order.

    ChatGPT exports store nodes in a mapping; dict iteration order is not a
    reliable semantic ordering. For markdown output, we traverse from roots.
    """
    mapping = conversation.node_mapping

    def sort_key(node: Node) -> tuple[float, str]:
        if node.message and node.message.create_time:
            try:
                ts = node.message.create_time.timestamp()
            except Exception:
                ts = 0.0
        else:
            ts = 0.0
        return (ts, node.id)

    roots = sorted((n for n in mapping.values() if n.parent is None), key=sort_key)

    visited: set[str] = set()
    ordered: list[Node] = []

    def dfs(node: Node) -> None:
        if node.id in visited:
            return
        visited.add(node.id)
        ordered.append(node)
        for child in sorted(node.children_nodes, key=sort_key):
            dfs(child)

    for root in roots:
        dfs(root)

    # Include any disconnected/orphan nodes deterministically at the end.
    for node in sorted(mapping.values(), key=sort_key):
        dfs(node)

    return ordered


def _ordered_nodes_active(conversation: Conversation) -> list[Node]:
    """Return nodes in the active branch order."""
    return conversation.ordered_nodes


def render_conversation(
    conversation: Conversation,
    config: ConversationConfig,
    headers: AuthorHeaders,
    asset_resolver: Callable[[str, str | None], str | None] | None = None,
) -> str:
    """Render a complete conversation as markdown.

    Args:
        conversation: The conversation to render
        config: Conversation rendering configuration
        headers: Configuration for author headers
        asset_resolver: Function to resolve asset IDs to paths, optionally renaming them

    Returns:
        Complete markdown document string
    """
    use_dollar_latex = config.markdown.latex_delimiters == "dollars"
    flavor = config.markdown.flavor
    show_timestamp = config.markdown.show_timestamp

    # Start with YAML header
    markdown = render_yaml_header(
        conversation,
        config.yaml,
        pandoc_pdf=config.pandoc_pdf,
        markdown_flavor=flavor,
    )

    # Pre-calculate citation map for the conversation
    citation_map = conversation.citation_map

    # Render message nodes based on configured order.
    last_timestamp = None
    if config.markdown.render_order == "active":
        nodes = _ordered_nodes_active(conversation)
    else:
        nodes = _ordered_nodes_full(conversation)

    for node in nodes:
        if node.message:
            markdown += render_node(
                node,
                headers,
                use_dollar_latex,
                asset_resolver=asset_resolver,
                flavor=flavor,
                citation_map=citation_map,
                show_timestamp=show_timestamp,
                last_timestamp=last_timestamp,
            )
            if node.message.create_time and not node.message.is_hidden:
                last_timestamp = node.message.create_time

    return markdown
