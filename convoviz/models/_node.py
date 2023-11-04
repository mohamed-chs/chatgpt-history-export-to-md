"""Node class and methods for the node object in a conversation.

object path : conversations.json -> conversation -> mapping -> mapping node

will implement methods to handle conversation branches, like
counting the number of branches,
get the branch of a given node,
and some other version control stuff
"""

from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

from ._message import Message

if TYPE_CHECKING:
    from typing import Any, ClassVar

    from typing_extensions import NotRequired, Self

    from ._message import MessageJSON


class NodeJSON(TypedDict):
    """Type of a `node` in the `mapping` field of a `conversation`."""

    id: str
    message: NotRequired[MessageJSON | None]
    parent: NotRequired[str | None]
    children: list[str]


class Node:
    """Wrapper class for a `node` in the `mapping` field of a `conversation`.

    see `NodeJSON` and `models.Conversation` for more details
    """

    __configs: ClassVar[dict[str, Any]] = {}

    def __init__(self, node: NodeJSON) -> None:
        """Initialize Node object."""
        self.__data = node
        self._parent: Self | None = None
        self._children: list[Self] = []

    @classmethod
    def update_configs(cls, configs: dict[str, Any]) -> None:
        """Set the configuration for all nodes."""
        cls.__configs.update(configs)

    @property
    def n_id(self) -> str:
        """Get the id of the node."""
        return self.__data["id"]

    @property
    def message(self) -> Message | None:
        """Get the message of the node."""
        if "message" not in self.__data or self.__data["message"] is None:
            return None
        return Message(self.__data["message"])

    @property
    def parent(self) -> Self | None:
        """Get the parent of the node."""
        return self._parent

    @parent.setter
    def parent(self, node: Self) -> None:
        """Set the parent of the node."""
        self._parent = node

    @property
    def children(self) -> list[Self]:
        """Get the children of the node."""
        return self._children

    def add_child(self, node: Self) -> None:
        """Add a child to the node."""
        self.children.append(node)
        node.parent = self

    @classmethod
    def mapping(cls, mapping: dict[str, NodeJSON]) -> dict[str, Self]:
        """Return a dictionary of connected Node objects, based on the mapping."""
        nodes: dict[str, Self] = {}

        # First pass: Create nodes
        for key, value in mapping.items():
            nodes[key] = cls(value)

        # Second pass: Connect nodes
        for key, value in mapping.items():
            for child_id in value["children"]:
                nodes[key].add_child(nodes[child_id])

        return nodes

    @property
    def header(self) -> str:
        """Get the header of the node message, containing a link to its parent."""
        if self.message is None:
            return ""

        parent_link = (
            f"[parent ⬆️](#{self.parent.n_id})\n"
            if self.parent and self.parent.message
            else ""
        )
        return f"###### {self.n_id}\n{parent_link}{self.message.author_header}\n"

    @property
    def footer(self) -> str:
        """Get the footer of the node message, containing links to its children."""
        if len(self.children) == 0:
            return ""
        if len(self.children) == 1:
            return f"\n[child ⬇️](#{self.children[0].n_id})\n"

        footer = "\n" + " | ".join(
            f"[child {i+1} ⬇️](#{child.n_id})" for i, child in enumerate(self.children)
        )
        return footer + "\n"
