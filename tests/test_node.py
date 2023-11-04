"""Tests for the Node class."""

from __future__ import annotations

from convoviz.models import Node

from .mocks import MAPPING_111


def test_nodes_from_mapping() -> None:
    """Test nodes_from_mapping method."""
    nodes = Node.mapping(MAPPING_111)
    assert "user_node_111" in nodes
    assert "assistant_node_111" in nodes
    assert nodes["root_node_111"].children[0] == nodes["system_node_111"]


def test_header_with_root_sys_and_user() -> None:
    """Test header method with root, system and user nodes."""
    nodes = Node.mapping(MAPPING_111)
    user_node = nodes["user_node_111"]
    header = user_node.header

    assert "user_node_111" in header
    assert "parent ⬆️" in header
    assert "# Me" in header
