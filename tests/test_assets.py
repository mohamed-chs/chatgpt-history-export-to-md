"""Tests for asset management functions."""

from pathlib import Path

from convoviz.io.assets import copy_asset, resolve_asset_path


def test_resolve_asset_path_exact_match(tmp_path: Path) -> None:
    """Test finding an asset with an exact name match."""
    (tmp_path / "file-123.png").touch()
    result = resolve_asset_path(tmp_path, "file-123.png")
    assert result == tmp_path / "file-123.png"


def test_resolve_asset_path_prefix_match(tmp_path: Path) -> None:
    """Test finding an asset with a prefix match."""
    (tmp_path / "file-123-longname.png").touch()
    result = resolve_asset_path(tmp_path, "file-123")
    assert result == tmp_path / "file-123-longname.png"


def test_resolve_asset_path_dalle_generation(tmp_path: Path) -> None:
    """Test finding an asset in the dalle-generations subdirectory."""
    dalle_dir = tmp_path / "dalle-generations"
    dalle_dir.mkdir()
    (dalle_dir / "file-456-generated.webp").touch()

    result = resolve_asset_path(tmp_path, "file-456")
    assert result == dalle_dir / "file-456-generated.webp"


def test_resolve_asset_path_not_found(tmp_path: Path) -> None:
    """Test that None is returned when asset is not found."""
    assert resolve_asset_path(tmp_path, "nonexistent") is None


def test_resolve_asset_path_security(tmp_path: Path) -> None:
    """Test path traversal attempts are rejected."""
    assert resolve_asset_path(tmp_path, "../outside") is None
    assert resolve_asset_path(tmp_path, "dir/inside") is None
    assert resolve_asset_path(tmp_path, "dir\\inside") is None


def test_copy_asset(tmp_path: Path) -> None:
    """Test copying an asset to the destination."""
    src_file = tmp_path / "source.png"
    src_file.touch()

    dest_dir = tmp_path / "output"
    dest_dir.mkdir()

    rel_path = copy_asset(src_file, dest_dir)

    assert rel_path == "assets/source.png"
    assert (dest_dir / "assets" / "source.png").exists()
