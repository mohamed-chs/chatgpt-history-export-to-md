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
    1. Tether v4 (metadata.citations): Placed at specific indices
       (【...】 placeholders).
    2. Embedded (Tether v3?): Unicode markers citeturnXsearchY.

    Args:
        text: The original message text
        citations: List of tether v4 citation objects (start_ix/end_ix)
        citation_map: Map of internal citation IDs to metadata
            (turnXsearchY -> {title, url})
        flavor: Markdown flavor for link formatting ("standard", "obsidian")

    Returns:
        Text with all placeholders replaced by markdown links
    """

    def maybe_prefix_space(original: str, start_idx: int, replacement: str) -> str:
        if not replacement:
            return replacement
        if start_idx <= 0:
            return replacement
        if original[start_idx - 1].isspace():
            return replacement
        return f" {replacement}"

    # 1. Handle Tether v4 (Index-based replacements)
    if citations:
        # Sort citations by start_ix descending to replace safely from end
        sorted_citations = sorted(
            citations, key=lambda c: c.get("start_ix", 0), reverse=True
        )

        for cit in sorted_citations:
            start = cit.get("start_ix")
            end = cit.get("end_ix")
            meta = cit.get("metadata", {})

            if start is None or end is None:
                continue

            replacement = _format_link(meta.get("title"), meta.get("url"), flavor)

            # Only replace if strictly positive indices and bounds check
            if 0 <= start < end <= len(text):
                replacement = maybe_prefix_space(text, start, replacement)
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

            replacement = " ".join(links)
            return maybe_prefix_space(text, match.start(), replacement)

        text = pattern.sub(replacer, text)

    return text


def _format_link(title: str | None, url: str | None, flavor: str = "standard") -> str:
    """Format a title and URL into a concise markdown link."""
    if flavor in ("standard", "obsidian"):
        if title and url:
            return f"[{title}]({url})"
        if url:
            return f"[Source]({url})"
        if title:
            return title
        return ""

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
        closures = "\n".join(
            f"{char * length}" for char, length in reversed(open_fences)
        )
        text += f"\n{closures}"

    return text


def replace_latex_delimiters(text: str) -> str:
    r"""Replace LaTeX bracket delimiters with dollar sign delimiters.

    Args:
        text: Text with \\[ \\] \\( \\) delimiters

    Returns:
        Text with $$ and $ delimiters
    """

    def replace_outside_inline_code(line: str) -> str:
        result: list[str] = []
        i = 0
        in_code = False
        code_len = 0
        segment_start = 0

        while i < len(line):
            if line[i] == "`" and (i == 0 or line[i - 1] != "\\"):
                run_len = 1
                while i + run_len < len(line) and line[i + run_len] == "`":
                    run_len += 1
                if in_code:
                    if run_len == code_len:
                        if segment_start < i:
                            result.append(line[segment_start:i])
                        result.append(line[i : i + run_len])
                        i += run_len
                        in_code = False
                        code_len = 0
                        segment_start = i
                        continue
                else:
                    if segment_start < i:
                        segment = line[segment_start:i]
                        segment = re.sub(r"\\\[", "$$", segment)
                        segment = re.sub(r"\\\]", "$$", segment)
                        segment = re.sub(r"\\\(", "$", segment)
                        segment = re.sub(r"\\\)", "$", segment)
                        result.append(segment)
                    result.append(line[i : i + run_len])
                    i += run_len
                    in_code = True
                    code_len = run_len
                    segment_start = i
                    continue
                i += run_len
                continue
            i += 1

        if segment_start < len(line):
            tail = line[segment_start:]
            if not in_code:
                tail = re.sub(r"\\\[", "$$", tail)
                tail = re.sub(r"\\\]", "$$", tail)
                tail = re.sub(r"\\\(", "$", tail)
                tail = re.sub(r"\\\)", "$", tail)
            result.append(tail)
        return "".join(result)

    lines = text.split("\n")
    fence_pattern = re.compile(r"^[ \t]{0,3}(`{3,}|~{3,})(.*)$")
    open_fences: list[tuple[str, int]] = []
    output_lines: list[str] = []

    for line in lines:
        match = fence_pattern.match(line)
        if match:
            fence = match.group(1)
            rest = match.group(2)
            fence_char = fence[0]
            fence_len = len(fence)

            if open_fences:
                open_char, open_len = open_fences[-1]
                if (
                    fence_char == open_char
                    and fence_len >= open_len
                    and rest.strip() == ""
                ):
                    open_fences.pop()
            else:
                open_fences.append((fence_char, fence_len))
            output_lines.append(line)
            continue

        if open_fences:
            output_lines.append(line)
            continue

        output_lines.append(replace_outside_inline_code(line))

    return "\n".join(output_lines)


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


def _render_timestamp(
    msg_time: datetime | None,
    last_time: datetime | None,
    enabled: bool,
) -> str:
    """Format the message timestamp."""
    if not enabled or not msg_time:
        return ""
    # Show full date if it's the first message or if the date has changed
    fmt = (
        "%Y-%m-%d %H:%M:%S"
        if (not last_time or msg_time.date() != last_time.date())
        else "%H:%M:%S"
    )
    return f"*{msg_time.strftime(fmt)}*\n"


def _render_images(
    message: Any,
    asset_resolver: Callable[[str, str | None], str | None] | None,
) -> str:
    """Format images as markdown."""
    if not asset_resolver or not message.images:
        return ""

    attachment_map = {}
    if message.metadata.attachments:
        attachment_map = {
            att["id"]: att["name"]
            for att in message.metadata.attachments
            if isinstance(att, dict) and att.get("id") and att.get("name")
        }

    image_markdown = []
    for image_id in message.images:
        target_name = attachment_map.get(image_id)
        if rel_path := asset_resolver(image_id, target_name):
            encoded_path = quote(rel_path)
            image_markdown.append(f"\n![Image]({encoded_path})\n")

    return "".join(image_markdown)


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
    """Render a complete node as markdown."""
    if (message := node.message) is None:
        return ""

    content_type = message.content.content_type

    # 1. Obsidian-specific collapsible callouts for "hidden" reasoning types
    if flavor == "obsidian" and (
        callout_info := OBSIDIAN_COLLAPSIBLE_TYPES.get(content_type)
    ):
        try:
            text = message.text
            if text.strip():
                ctype, title = callout_info
                return f"\n{render_obsidian_callout(text, title, ctype, True)}\n"
        except MessageContentError:
            pass

    if message.is_hidden:
        return ""

    # 2. Main message rendering
    header = render_node_header(node, headers)
    timestamp = _render_timestamp(message.create_time, last_timestamp, show_timestamp)

    try:
        text = message.text
    except MessageContentError:
        text = ""

    # Process Citations
    effective_map = citation_map or message.internal_citation_map
    if message.metadata.citations or effective_map:
        text = replace_citations(
            text,
            citations=message.metadata.citations,
            citation_map=effective_map,
            flavor=flavor,
        )

    content = close_code_blocks(text)
    if content:
        content = f"\n{content}\n"
        if use_dollar_latex:
            content = replace_latex_delimiters(content)

    images = _render_images(message, asset_resolver)

    return f"\n{header}{timestamp}{content}{images}\n***\n"


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
    yaml_header = render_yaml_header(conversation, config.yaml)
    markdown = yaml_header
    markdown += f"<!-- conversation_id={conversation.conversation_id} -->\n"

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
