"""Tests for attachment renaming functionality."""

from pathlib import Path

from convoviz.config import AuthorHeaders
from convoviz.io.assets import copy_asset
from convoviz.models import (
    Message,
    MessageAuthor,
    MessageContent,
    MessageMetadata,
    Node,
)
from convoviz.renderers.markdown import render_node

# --- Test Data ---


def create_message_with_attachment(
    msg_id: str,
    attachment_id: str,
    attachment_name: str | None = None,
) -> Message:
    """Create a mock message with an attachment."""
    content = MessageContent(
        content_type="text",
        parts=[
            {
                "content_type": "image_asset_pointer",
                "asset_pointer": f"file-service://{attachment_id}",
            },
        ],
    )

    metadata = MessageMetadata()
    if attachment_name:
        metadata.attachments = [{"id": attachment_id, "name": attachment_name}]

    return Message(
        id=msg_id,
        author=MessageAuthor(role="user"),
        content=content,
        status="finished_successfully",
        weight=1.0,
        metadata=metadata,
    )


def test_render_node_renames_attachment() -> None:
    """Test that render_node passes the correct target name to the asset resolver."""
    # Setup
    attachment_id = "file-123"
    target_name = "cool_image.png"
    message = create_message_with_attachment("msg-1", attachment_id, target_name)
    node = Node(id="node-1", message=message, parent=None, children=[])

    # Mock asset resolver
    resolver_calls = []

    def mock_resolver(asset_id: str, name: str | None = None) -> str | None:
        resolver_calls.append((asset_id, name))
        return f"assets/{name or asset_id}"

    headers = AuthorHeaders()

    # Execute
    result = render_node(node, headers, asset_resolver=mock_resolver)

    # Verify
    assert len(resolver_calls) == 1
    assert resolver_calls[0] == (attachment_id, target_name)
    assert f"assets/{target_name}" in result


def test_render_node_no_rename_if_no_metadata() -> None:
    """Test that render_node passes None as name if metadata is missing."""
    # Setup
    attachment_id = "file-456"
    message = create_message_with_attachment("msg-2", attachment_id, None)
    node = Node(id="node-2", message=message, parent=None, children=[])

    # Mock asset resolver
    resolver_calls = []

    def mock_resolver(asset_id: str, name: str | None = None) -> str | None:
        resolver_calls.append((asset_id, name))
        return f"assets/{asset_id}"

    headers = AuthorHeaders()

    # Execute
    render_node(node, headers, asset_resolver=mock_resolver)

    # Verify
    assert len(resolver_calls) == 1
    assert resolver_calls[0] == (attachment_id, None)


def test_copy_asset_uses_target_name(tmp_path: Path) -> None:
    """Test that copy_asset uses the target name for the destination file."""
    # Setup
    source_file = tmp_path / "original.png"
    source_file.write_bytes(b"DATA")

    dest_dir = tmp_path / "output"
    target_name = "renamed.png"

    # Execute
    path = copy_asset(source_file, dest_dir, target_name=target_name)

    # Verify result path
    assert path == f"assets/{target_name}"

    # Verify file existence and content
    expected_file = dest_dir / "assets" / target_name
    assert expected_file.exists()
    assert expected_file.read_bytes() == b"DATA"

    # Verify original name is NOT used
    assert not (dest_dir / "assets" / "original.png").exists()


def test_copy_asset_defaults_to_source_name(tmp_path: Path) -> None:
    """Test that copy_asset uses source name if target_name is None."""
    # Setup
    source_file = tmp_path / "original.png"
    source_file.write_bytes(b"DATA")

    dest_dir = tmp_path / "output"

    # Execute
    path = copy_asset(source_file, dest_dir)

    # Verify result path
    assert path == "assets/original.png"

    # Verify file existence
    assert (dest_dir / "assets" / "original.png").exists()


def test_render_node_encodes_spaces() -> None:
    """Test that render_node URL-encodes asset paths with spaces."""
    # Setup
    attachment_id = "file-123"
    target_name = "image with spaces.png"
    message = create_message_with_attachment("msg-1", attachment_id, target_name)
    node = Node(id="node-1", message=message, parent=None, children=[])

    # Mock asset resolver (simulating what writers.py does)
    def mock_resolver(_asset_id: str, name: str | None = None) -> str | None:
        return f"assets/{name}"

    headers = AuthorHeaders()

    # Execute
    result = render_node(node, headers, asset_resolver=mock_resolver)

    # Verify: "image with spaces.png" -> "image%20with%20spaces.png"
    expected_encoded = "assets/image%20with%20spaces.png"
    assert f"![Image]({expected_encoded})" in result


def test_copy_asset_sanitizes_name(tmp_path: Path) -> None:
    """Test that copy_asset sanitizes the target name."""
    # Setup
    source_file = tmp_path / "original.png"
    source_file.write_bytes(b"DATA")

    dest_dir = tmp_path / "output"
    target_name = "image/with:invalid*chars.png"
    sanitized_name = "image with invalid chars.png"

    # Execute
    path = copy_asset(source_file, dest_dir, target_name=target_name)

    # Verify result path
    assert path == f"assets/{sanitized_name}"

    # Verify file existence
    assert (dest_dir / "assets" / sanitized_name).exists()


def test_non_image_attachment_not_rendered() -> None:
    """Non-image attachments should not be rendered as images."""
    content = MessageContent(content_type="text", text="Hello")
    metadata = MessageMetadata(
        attachments=[
            {"id": "file-999", "name": "report.pdf", "mime_type": "application/pdf"},
        ],
    )
    message = Message(
        id="msg-3",
        author=MessageAuthor(role="user"),
        content=content,
        status="finished_successfully",
        weight=1.0,
        metadata=metadata,
    )
    node = Node(id="node-3", message=message, parent=None, children=[])

    resolver_calls: list[tuple[str, str | None]] = []

    def mock_resolver(asset_id: str, name: str | None = None) -> str | None:
        resolver_calls.append((asset_id, name))
        return f"assets/{name or asset_id}"

    headers = AuthorHeaders()
    result = render_node(node, headers, asset_resolver=mock_resolver)

    assert resolver_calls == []
    assert "![Image]" not in result
