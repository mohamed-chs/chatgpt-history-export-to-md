"""Node class and methods for the node object in a conversation.

object path : conversations.json -> conversation -> mapping -> mapping node

will implement methods to handle conversation branches, like
counting the number of branches,
get the branch of a given node,
and some other version control stuff
"""

from __future__ import annotations

from pydantic import BaseModel

from ._message import Message  # noqa: TCH001


class Node(BaseModel):
    """Wrapper class for a `node` in the `mapping` field of a `conversation`."""

    id: str  # noqa: A003
    message: Message | None = None
    parent: str | None = None
    children: list[str]
    parent_node: Node | None = None
    children_nodes: list[Node] = []

    def add_child(self, node: Node) -> None:
        """Add a child to the node."""
        self.children_nodes.append(node)
        node.parent_node = self

    @classmethod
    def mapping(cls, mapping: dict[str, Node]) -> dict[str, Node]:
        """Return a dictionary of connected Node objects, based on the mapping."""
        # Initialize connections
        for node in mapping.values():
            node.children_nodes = []  # Ensure list is empty to avoid duplicates
            node.parent_node = None  # Ensure parent_node is None

        # Connect nodes
        for node in mapping.values():
            for child_id in node.children:
                child_node = mapping[child_id]
                node.add_child(child_node)

        return mapping

    @property
    def header(self) -> str:
        """Get the header of the node message, containing a link to its parent."""
        if self.message is None:
            return ""

        parent_link = (
            f"[parent ⬆️](#{self.parent_node.id})\n"
            if self.parent_node and self.parent_node.message
            else ""
        )
        return f"###### {self.id}\n{parent_link}{self.message.header}\n"

    @property
    def footer(self) -> str:
        """Get the footer of the node message, containing links to its children."""
        if len(self.children_nodes) == 0:
            return ""
        if len(self.children_nodes) == 1:
            return f"\n[child ⬇️](#{self.children_nodes[0].id})\n"

        footer = "\n" + " | ".join(
            f"[child {i+1} ⬇️](#{child.id})"
            for i, child in enumerate(self.children_nodes)
        )
        return footer + "\n"
