"""Node class and methods for the node object in a conversation.

object path : conversations.json -> conversation -> mapping -> mapping node

will implement methods to handle conversation branches, like
counting the number of branches,
get the branch of a given node,
and some other version control stuff
"""

from __future__ import annotations

from typing import Any, ClassVar

from .message import Message


class Node:
    """Node class for representing a node in a conversation tree."""

    configuration: ClassVar[dict[str, Any]] = {}

    def __init__(
        self,
        n_id: str,
        msg: Message | None,
        parent: Node | None,
        children: list[Node] | None,
    ) -> None:
        """Initialize Node object."""
        self.id: str = n_id
        self.message: Message | None = msg
        self.parent: Node | None = parent
        self.children: list[Node] = children if children else []

    def add_child(self, node: Node) -> None:
        """Add a child to the node."""
        self.children.append(node)
        node.parent = self

    @staticmethod
    def nodes_from_mapping(mapping: dict[str, Any]) -> dict[str, Node]:
        """Return a dictionary of connected Node objects, based on the mapping."""
        nodes: dict[str, Node] = {}

        # First pass: Create nodes
        for key, value in mapping.items():
            message: Message | None = (
                Message(message=value["message"]) if value.get("message") else None
            )
            nodes[key] = Node(n_id=key, msg=message, parent=None, children=None)

        # Second pass: Connect nodes
        for key, value in mapping.items():
            for child_id in value["children"]:
                nodes[key].add_child(node=nodes[child_id])

        return nodes

    def header(self) -> str:
        """Get the header of the node message, containing a link to its parent."""
        if self.message is None:
            return ""

        parent_link: str = (
            f"[parent ⬆️](#{self.parent.id})\n"
            if self.parent and self.parent.message
            else ""
        )
        return f"###### {self.id}\n{parent_link}{self.message.author_header()}\n"

    def footer(self) -> str:
        """Get the footer of the node message, containing links to its children."""
        if len(self.children) == 0:
            return ""
        if len(self.children) == 1:
            return f"\n[child ⬇️](#{self.children[0].id})\n"

        footer: str = "\n" + " | ".join(
            [
                f"[child {i+1} ⬇️](#{child.id})"
                for i, child in enumerate(iterable=self.children)
            ],
        )
        return footer + "\n"
