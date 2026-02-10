"""Asset management functions."""

import hashlib
import logging
import shutil
from dataclasses import dataclass
from pathlib import Path

from convoviz.utils import sanitize

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AssetIndex:
    """Pre-scanned asset index for faster lookups."""

    root_files: tuple[Path, ...]
    dalle_files: tuple[Path, ...]
    user_files_by_dir: dict[Path, tuple[Path, ...]]
    root_prefix_map: dict[str, Path]
    dalle_prefix_map: dict[str, Path]
    user_prefix_map_by_dir: dict[Path, dict[str, Path]]


def build_asset_index(source_dir: Path) -> AssetIndex:
    """Scan asset directories once and return an index."""
    root_files: list[Path] = []
    dalle_files: list[Path] = []
    user_files_by_dir: dict[Path, tuple[Path, ...]] = {}
    root_prefix_map: dict[str, Path] = {}
    dalle_prefix_map: dict[str, Path] = {}
    user_prefix_map_by_dir: dict[Path, dict[str, Path]] = {}

    if not source_dir.exists():
        return AssetIndex((), (), {}, {}, {}, {})

    source_dir = source_dir.resolve()

    try:
        root_files = [p.resolve() for p in source_dir.iterdir() if p.is_file()]
    except Exception:
        root_files = []

    dalle_dir = source_dir / "dalle-generations"
    if dalle_dir.exists() and dalle_dir.is_dir():
        try:
            dalle_files = [p.resolve() for p in dalle_dir.iterdir() if p.is_file()]
        except Exception:
            dalle_files = []

    try:
        for user_dir in source_dir.glob("user-*"):
            if user_dir.is_dir():
                try:
                    files = tuple(
                        p.resolve() for p in user_dir.iterdir() if p.is_file()
                    )
                    user_files_by_dir[user_dir.resolve()] = files
                    user_prefix_map_by_dir[user_dir.resolve()] = _build_prefix_map(
                        files
                    )
                except Exception:
                    continue
    except Exception:
        user_files_by_dir = {}
        user_prefix_map_by_dir = {}

    root_prefix_map = _build_prefix_map(root_files)
    dalle_prefix_map = _build_prefix_map(dalle_files)

    return AssetIndex(
        tuple(root_files),
        tuple(dalle_files),
        user_files_by_dir,
        root_prefix_map,
        dalle_prefix_map,
        user_prefix_map_by_dir,
    )


def _extract_prefix(name: str) -> str | None:
    """Extract a stable asset prefix from a filename."""
    if not name:
        return None
    base = name
    if "_" in base:
        base = base.split("_", 1)[0]
    if "." in base:
        base = base.split(".", 1)[0]
    return base or None


def _build_prefix_map(files: list[Path] | tuple[Path, ...]) -> dict[str, Path]:
    """Build a prefix -> path map for fast asset lookups."""
    prefix_map: dict[str, Path] = {}
    for path in sorted(files, key=lambda p: p.name):
        prefix = _extract_prefix(path.name)
        if not prefix:
            continue
        prefix_map.setdefault(prefix, path)
    return prefix_map


def _prefix_match(files: tuple[Path, ...], asset_id: str, root: Path) -> Path | None:
    for path in files:
        if path.name.startswith(asset_id) and path.is_relative_to(root):
            return path
    return None


def resolve_asset_path(
    source_dir: Path,
    asset_id: str,
    *,
    index: AssetIndex | None = None,
) -> Path | None:
    """Find the actual file for a given asset ID in the source directory.

    Args:
        source_dir: Directory to search in
        asset_id: The asset ID (e.g., "file-uuid")

    Returns:
        Path to the found file, or None

    """
    if not source_dir.exists():
        return None

    source_dir = source_dir.resolve()

    # Safety check for asset_id
    if ".." in asset_id or "/" in asset_id or "\\" in asset_id:
        return None

    # 1. Try exact match
    exact_path = (source_dir / asset_id).resolve()
    if (
        exact_path.exists()
        and exact_path.is_file()
        and exact_path.is_relative_to(source_dir)
    ):
        logger.debug(f"Resolved asset (exact): {asset_id} -> {exact_path}")
        return exact_path

    # 2. Try prefix match in root
    if index:
        match = index.root_prefix_map.get(asset_id)
        if not match:
            match = _prefix_match(index.root_files, asset_id, source_dir)
        if match:
            logger.debug(f"Resolved asset (prefix root): {asset_id} -> {match}")
            return match
    else:
        try:
            candidates = list(source_dir.glob(f"{asset_id}*"))
            files = [
                p.resolve()
                for p in candidates
                if p.is_file() and p.resolve().is_relative_to(source_dir)
            ]
            if files:
                logger.debug(f"Resolved asset (prefix root): {asset_id} -> {files[0]}")
                return files[0]
        except Exception:
            pass

    # 3. Try prefix match in dalle-generations
    dalle_dir = source_dir / "dalle-generations"
    if dalle_dir.exists() and dalle_dir.is_dir():
        dalle_dir = dalle_dir.resolve()
        if index:
            match = index.dalle_prefix_map.get(asset_id)
            if not match:
                match = _prefix_match(index.dalle_files, asset_id, dalle_dir)
            if match:
                logger.debug(f"Resolved asset (dalle): {asset_id} -> {match}")
                return match
        else:
            try:
                candidates = list(dalle_dir.glob(f"{asset_id}*"))
                files = [
                    p.resolve()
                    for p in candidates
                    if p.is_file() and p.resolve().is_relative_to(dalle_dir)
                ]
                if files:
                    logger.debug(f"Resolved asset (dalle): {asset_id} -> {files[0]}")
                    return files[0]
            except Exception:
                pass

    # 4. Try prefix match in user-* directories (new 2025 format)
    if index:
        for user_dir, files in index.user_files_by_dir.items():
            user_map = index.user_prefix_map_by_dir.get(user_dir, {})
            match = user_map.get(asset_id)
            if not match:
                match = _prefix_match(files, asset_id, user_dir)
            if match:
                logger.debug(f"Resolved asset (user dir): {asset_id} -> {match}")
                return match
    else:
        try:
            for user_dir in source_dir.glob("user-*"):
                if user_dir.is_dir():
                    user_dir = user_dir.resolve()
                    candidates = list(user_dir.glob(f"{asset_id}*"))
                    files = [
                        p.resolve()
                        for p in candidates
                        if p.is_file() and p.resolve().is_relative_to(user_dir)
                    ]
                    if files:
                        logger.debug(
                            f"Resolved asset (user dir): {asset_id} -> {files[0]}"
                        )
                        return files[0]
        except Exception:
            pass

    return None


def _hash_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def _resolve_unique_dest(
    dest_dir: Path,
    filename: str,
    source_path: Path,
) -> Path:
    """Resolve a destination path that avoids collisions with differing content."""
    base = Path(filename).stem
    suffix = Path(filename).suffix
    candidate = dest_dir / filename
    counter = 1

    while candidate.exists():
        try:
            if candidate.stat().st_size == source_path.stat().st_size and _hash_file(
                candidate
            ) == _hash_file(source_path):
                return candidate
        except Exception:
            pass
        candidate = dest_dir / f"{base} ({counter}){suffix}"
        counter += 1

    return candidate


def copy_asset(
    source_path: Path,
    dest_dir: Path,
    target_name: str | None = None,
) -> str:
    """Copy an asset to the destination directory.

    Args:
        source_path: The source file path
        dest_dir: The root output directory (assets will be in dest_dir/assets)
        target_name: Optional name to rename the file to
    Returns:
        Relative path to the asset (e.g., "assets/image.png")

    """
    assets_dir = dest_dir / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)

    filename = sanitize(target_name) if target_name else source_path.name
    dest_path = _resolve_unique_dest(assets_dir, filename, source_path)

    if not dest_path.exists():
        try:
            shutil.copy2(source_path, dest_path)
            logger.debug(f"Copied asset: {source_path.name} -> {dest_path.name}")
        except Exception as e:
            logger.warning(f"Failed to copy asset {source_path}: {e}")

    # Return forward-slash path for Markdown compatibility even on Windows
    return f"assets/{dest_path.name}"
