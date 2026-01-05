"""Node model - pure data class.

Object path: conversations.json -> conversation -> mapping -> mapping node

Nodes form a tree structure representing conversation branches.
"""

from pydantic import BaseModel, Field

from convoviz.models.message import Message


class Node(BaseModel):
    """A node in the conversation tree.

    Each node can have a message and links to parent/children nodes.
    This is a pure data model - rendering logic is in the renderers module.
    """

    id: str
    message: Message | None = None
    parent: str | None = None
    children: list[str] = Field(default_factory=list)

    # Runtime-populated references (not from JSON)
    parent_node: "Node | None" = None
    children_nodes: list["Node"] = Field(default_factory=list)

    def add_child(self, node: "Node") -> None:
        """Add a child node and set up bidirectional references."""
        self.children_nodes.append(node)
        node.parent_node = self

    @property
    def has_message(self) -> bool:
        """Check if this node contains a message."""
        return self.message is not None

    @property
    def is_leaf(self) -> bool:
        """Check if this node is a leaf (no children)."""
        return len(self.children_nodes) == 0


def build_node_tree(mapping: dict[str, Node]) -> dict[str, Node]:
    """Build the node tree by connecting parent/child references.

    Args:
        mapping: Dictionary of node_id -> Node

    Returns:
        The same dictionary with nodes connected via parent_node/children_nodes
    """
    # Reset connections to avoid duplicates on repeated calls
    for node in mapping.values():
        node.children_nodes = []
        node.parent_node = None

    # Build connections
    for node in mapping.values():
        for child_id in node.children:
            if child_id in mapping:
                child_node = mapping[child_id]
                node.add_child(child_node)

    return mapping
