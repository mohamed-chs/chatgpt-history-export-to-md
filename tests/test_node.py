"""Tests for the Node class."""

from typing import Any

from models.message import Message
from models.node import Node


def test_node_initialization() -> None:
    """Test initialization of Node object."""

    node_id = "node_id_123"
    msg = Message(message={"id": "msg_id_123", "author": {"role": "user"}})
    node = Node(n_id=node_id, msg=msg, parent=None, children=None)

    assert node.id == node_id
    assert node.message == msg
    assert node.parent is None
    assert len(node.children) == 0


def test_add_child() -> None:
    """Test add_child method."""

    parent_node = Node(n_id="parent_node_id", msg=None, parent=None, children=None)
    child_node = Node(n_id="child_node_id", msg=None, parent=None, children=None)

    parent_node.add_child(node=child_node)

    assert len(parent_node.children) == 1
    assert parent_node.children[0] == child_node
    assert child_node.parent == parent_node


def test_nodes_from_mapping() -> None:
    """Test nodes_from_mapping method."""

    mapping: dict[str, Any] = {
        "node1": {
            "message": {
                "id": "msg1",
                "author": {"role": "user"},
            },
            "children": ["node2"],
        },
        "node2": {
            "message": {
                "id": "msg2",
                "author": {"role": "assistant"},
            },
            "children": [],
        },
    }

    nodes: dict[str, Node] = Node.nodes_from_mapping(mapping=mapping)
    assert "node1" in nodes
    assert "node2" in nodes
    assert nodes["node1"].children[0] == nodes["node2"]


def test_header_with_root_sys_and_user() -> None:
    """Test header method with root, system and user nodes."""

    root = Node(n_id="root_id", msg=None, parent=None, children=None)
    system_msg = Message(message={"id": "sys_msg_id", "author": {"role": "system"}})
    sys_node = Node(n_id="sys_node_id", msg=system_msg, parent=root, children=None)
    user_msg = Message(message={"id": "user_msg_id", "author": {"role": "user"}})
    user_node = Node(n_id="user_node_id", msg=user_msg, parent=sys_node, children=None)
    header: str = user_node.header()

    assert "node_id" in header
    assert "parent ⬆️" in header
    assert "# User" in header


def test_footer_with_multiple_children() -> None:
    """Test footer method with multiple children."""

    node = Node(n_id="node_id", msg=None, parent=None, children=None)
    child1 = Node(n_id="child1_id", msg=None, parent=None, children=None)
    child2 = Node(n_id="child2_id", msg=None, parent=None, children=None)

    node.add_child(node=child1)
    node.add_child(node=child2)

    footer: str = node.footer()

    assert "child 1 ⬇️" in footer
    assert "child 2 ⬇️" in footer
