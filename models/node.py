"""
Node class and methods for the node object in a conversation
object path : conversations.json -> conversation -> mapping -> mapping node

will implement methods to handle conversation branches, like
counting the number of branches,
get the branch of a given node,
and some other version control stuff
"""

from typing import Any

from .message import Message


class Node:
    """Node class for representing a node in a conversation tree."""

    configuration: dict[str, Any] = {}

    def __init__(
        self,
        node_id: str,
        message: Message | None,
        parent: "Node" | None,
        children: list["Node"] | None,
    ):
        self.id = node_id
        self.message = message
        self.parent = parent
        if children is None:
            self.children: list["Node"] = []

    def add_child(self, node: "Node"):
        """Add a child to the node."""
        self.children.append(node)
        node.parent = self

    @staticmethod
    def nodes_from_mapping(mapping: dict[str, Any]) -> dict[str, "Node"]:
        """Returns a dictionary of connected Node objects, based on the mapping."""
        nodes: dict[str, Node] = {}

        # First pass: Create nodes
        for key, value in mapping.items():
            message = Message(value["message"]) if value.get("message") else None
            nodes[key] = Node(node_id=key, message=message, parent=None, children=None)

        # Second pass: Connect nodes
        for key, value in mapping.items():
            for child_id in value["children"]:
                nodes[key].add_child(nodes[child_id])

        return nodes

    def header(self) -> str | None:
        """Get the header of the node message, containing a link to its parent."""
        if self.message is None:
            return None

        parent_link = (
            f"[parent ⬆️](#{self.parent.id})\n"
            if self.parent and self.parent.message
            else ""
        )
        return f"###### {self.id}\n{parent_link}{self.message.author_header()}\n"

    def footer(self) -> str | None:
        """Get the footer of the node message, containing links to its children."""
        if self.message is None:
            return None

        if len(self.children) == 0:
            return ""
        if len(self.children) == 1:
            return f"\n[child ⬇️](#{self.children[0].id})\n"

        footer = "\n" + " | ".join(
            [f"[child {i+1} ⬇️](#{child.id})" for i, child in enumerate(self.children)]
        )
        return footer + "\n"

    # just for testing, and fun. It's not really ideal for the real thing
    def show(self, level: int = 0) -> str:
        """Return a tree representation of the node and its descendants."""

        lines = [
            (
                f"{'--'*level}lvl{level} : {self.id[:10]}... ,\n"
                f"{'--'*level} : "
                f"{self.message.author_header() if self.message else None} ,\n"
                f"{'--'*level} : "
                f"{self.message.content_text()[:50] if self.message else None}... \n\n"
            )
        ]
        for child in self.children:
            lines.append(child.show(level + 1))

        return "".join(lines)
