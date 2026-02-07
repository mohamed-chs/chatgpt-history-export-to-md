"""Tests for asset management functions."""

from pathlib import Path

import pytest

from convoviz.io.assets import copy_asset, resolve_asset_path


class TestResolveAssetPath:
    """Tests for the resolve_asset_path function."""

    def test_exact_match(self, tmp_path: Path) -> None:
        """Test finding an asset with an exact name match."""
        (tmp_path / "file-123.png").touch()
        result = resolve_asset_path(tmp_path, "file-123.png")
        assert result == tmp_path / "file-123.png"

    def test_prefix_match(self, tmp_path: Path) -> None:
        """Test finding an asset with a prefix match."""
        (tmp_path / "file-123-longname.png").touch()
        result = resolve_asset_path(tmp_path, "file-123")
        assert result == tmp_path / "file-123-longname.png"

    def test_dalle_generation_folder(self, tmp_path: Path) -> None:
        """Test finding an asset in the dalle-generations subdirectory."""
        dalle_dir = tmp_path / "dalle-generations"
        dalle_dir.mkdir()
        (dalle_dir / "file-456-generated.webp").touch()

        result = resolve_asset_path(tmp_path, "file-456")
        assert result == dalle_dir / "file-456-generated.webp"

    def test_user_folder_2025_format(self, tmp_path: Path) -> None:
        """Test finding an asset in user-* folders (2025 export format)."""
        user_dir = tmp_path / "user-abc123"
        user_dir.mkdir()
        (user_dir / "file-789-system.png").touch()

        result = resolve_asset_path(tmp_path, "file-789")
        assert result == user_dir / "file-789-system.png"

    def test_user_folder_multiple_users(self, tmp_path: Path) -> None:
        """Test finding asset when multiple user-* folders exist."""
        user_dir_1 = tmp_path / "user-111"
        user_dir_2 = tmp_path / "user-222"
        user_dir_1.mkdir()
        user_dir_2.mkdir()
        # Asset is in the second user folder
        (user_dir_2 / "target-asset.png").touch()

        result = resolve_asset_path(tmp_path, "target-asset")
        # Should find it in one of the user folders
        assert result is not None
        assert result.name == "target-asset.png"

    def test_priority_root_over_subfolders(self, tmp_path: Path) -> None:
        """Test that root folder takes priority over subfolders."""
        # Create same-prefix file in both root and dalle folder
        (tmp_path / "file-100.png").touch()
        dalle_dir = tmp_path / "dalle-generations"
        dalle_dir.mkdir()
        (dalle_dir / "file-100-other.webp").touch()

        result = resolve_asset_path(tmp_path, "file-100")
        # Root should be checked first
        assert result == tmp_path / "file-100.png"

    def test_not_found(self, tmp_path: Path) -> None:
        """Test that None is returned when asset is not found."""
        assert resolve_asset_path(tmp_path, "nonexistent") is None

    def test_nonexistent_directory(self, tmp_path: Path) -> None:
        """Test that None is returned for nonexistent source directory."""
        fake_dir = tmp_path / "does_not_exist"
        assert resolve_asset_path(fake_dir, "file") is None

    def test_security_path_traversal(self, tmp_path: Path) -> None:
        """Test path traversal attempts are rejected."""
        assert resolve_asset_path(tmp_path, "../outside") is None
        assert resolve_asset_path(tmp_path, "..\\outside") is None

    def test_security_slash_in_asset_id(self, tmp_path: Path) -> None:
        """Test that slashes in asset IDs are rejected."""
        assert resolve_asset_path(tmp_path, "dir/inside") is None
        assert resolve_asset_path(tmp_path, "dir\\inside") is None


class TestCopyAsset:
    """Tests for the copy_asset function."""

    def test_basic_copy(self, tmp_path: Path) -> None:
        """Test copying an asset to the destination."""
        src_file = tmp_path / "source.png"
        src_file.write_bytes(b"PNG data")

        dest_dir = tmp_path / "output"
        dest_dir.mkdir()

        rel_path = copy_asset(src_file, dest_dir)

        assert rel_path == "assets/source.png"
        assert (dest_dir / "assets" / "source.png").exists()
        assert (dest_dir / "assets" / "source.png").read_bytes() == b"PNG data"

    def test_creates_assets_directory(self, tmp_path: Path) -> None:
        """Test that assets directory is created if it doesn't exist."""
        src_file = tmp_path / "image.webp"
        src_file.touch()

        dest_dir = tmp_path / "output"
        dest_dir.mkdir()

        copy_asset(src_file, dest_dir)

        assert (dest_dir / "assets").is_dir()

    def test_skip_existing_file(self, tmp_path: Path) -> None:
        """Test that existing files are not overwritten."""
        src_file = tmp_path / "image.png"
        src_file.write_bytes(b"NEW")

        dest_dir = tmp_path / "output"
        assets_dir = dest_dir / "assets"
        assets_dir.mkdir(parents=True)
        existing = assets_dir / "image.png"
        existing.write_bytes(b"OLD")

        copy_asset(src_file, dest_dir)

        # Original file should be preserved
        assert existing.read_bytes() == b"OLD"

    def test_returns_forward_slash_path(self, tmp_path: Path) -> None:
        """Test that returned path uses forward slashes (Markdown compatible)."""
        src_file = tmp_path / "test.png"
        src_file.touch()

        dest_dir = tmp_path / "output"
        dest_dir.mkdir()

        rel_path = copy_asset(src_file, dest_dir)

        # Should use forward slashes regardless of OS
        assert "/" in rel_path
        assert "\\" not in rel_path

    def test_converts_webp_to_png_for_pandoc(self, tmp_path: Path) -> None:
        """Test converting WebP assets to PNG when requested."""
        pytest.importorskip("PIL")
        from PIL import Image, features

        if not features.check("webp"):
            pytest.skip("Pillow WebP support not available")

        src_file = tmp_path / "source.webp"
        image = Image.new("RGB", (2, 2), color=(255, 0, 0))
        image.save(src_file, format="WEBP")

        dest_dir = tmp_path / "output"
        dest_dir.mkdir()

        rel_path = copy_asset(src_file, dest_dir, convert_webp_to_png=True)

        assert rel_path == "assets/source.png"
        assert (dest_dir / "assets" / "source.png").exists()
