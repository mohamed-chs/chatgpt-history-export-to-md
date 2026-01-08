"Asset management functions."

import shutil
from pathlib import Path


def resolve_asset_path(source_dir: Path, asset_id: str) -> Path | None:
    """Find the actual file for a given asset ID in the source directory.

    Args:
        source_dir: Directory to search in
        asset_id: The asset ID (e.g., "file-uuid")

    Returns:
        Path to the found file, or None
    """
    if not source_dir.exists():
        return None

    # Safety check
    if ".." in asset_id or "/" in asset_id or "\\" in asset_id:
        return None

    # 1. Try exact match
    exact_path = source_dir / asset_id
    if exact_path.exists() and exact_path.is_file():
        return exact_path

    # 2. Try prefix match in root
    try:
        candidates = list(source_dir.glob(f"{asset_id}*"))
        files = [p for p in candidates if p.is_file()]
        if files:
            return files[0]
    except Exception:
        pass

    # 3. Try prefix match in dalle-generations
    dalle_dir = source_dir / "dalle-generations"
    if dalle_dir.exists() and dalle_dir.is_dir():
        try:
            candidates = list(dalle_dir.glob(f"{asset_id}*"))
            files = [p for p in candidates if p.is_file()]
            if files:
                return files[0]
        except Exception:
            pass

    return None


def copy_asset(source_path: Path, dest_dir: Path) -> str:
    """Copy an asset to the destination directory.

    Args:
        source_path: The source file path
        dest_dir: The root output directory (assets will be in dest_dir/assets)

    Returns:
        Relative path to the asset (e.g., "assets/image.png")
    """
    assets_dir = dest_dir / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)

    dest_path = assets_dir / source_path.name

    if not dest_path.exists():
        shutil.copy2(source_path, dest_path)

    # Return forward-slash path for Markdown compatibility even on Windows
    return f"assets/{source_path.name}"
