"""Utility functions for convoviz."""

import re
from pathlib import Path


def sanitize(filename: str) -> str:
    """Sanitize a string to be safe for use as a filename.

    Replaces invalid characters with underscores, handles reserved names,
    and prevents path traversal characters.

    Args:
        filename: The string to sanitize

    Returns:
        A filename-safe string, or "untitled" if empty or invalid
    """
    # Replace invalid characters
    pattern = re.compile(r'[<>:"/\\|?*\n\r\t\f\v]+')
    result = pattern.sub("_", filename.strip())

    # Prevent path traversal
    result = result.replace("..", "_")

    # Windows reserved names
    reserved = {
        "CON",
        "PRN",
        "AUX",
        "NUL",
        "COM1",
        "COM2",
        "COM3",
        "COM4",
        "COM5",
        "COM6",
        "COM7",
        "COM8",
        "COM9",
        "LPT1",
        "LPT2",
        "LPT3",
        "LPT4",
        "LPT5",
        "LPT6",
        "LPT7",
        "LPT8",
        "LPT9",
    }
    if result.upper() in reserved:
        result = f"_{result}_"

    # Enforce length limit (255 is common for many filesystems)
    if len(result) > 255:
        result = result[:255]

    return result or "untitled"


def validate_header(text: str) -> bool:
    """Check if text is a valid markdown header.

    Args:
        text: The text to validate

    Returns:
        True if it's a valid header (1-6 # followed by space and content)
    """
    max_header_level = 6
    if not text.startswith("#"):
        return False

    parts = text.split(maxsplit=1)
    if len(parts) < 2:
        return False

    hashes = parts[0]
    return hashes == "#" * len(hashes) and 1 <= len(hashes) <= max_header_level


def root_dir() -> Path:
    """Get the path to the convoviz package directory.

    Returns:
        Path to the package root
    """
    return Path(__file__).parent


def get_asset_path(relative_path: str) -> Path:
    """Get the absolute path to an asset file.

    Args:
        relative_path: Path relative to convoviz root (e.g., "assets/fonts/foo.ttf")

    Returns:
        Absolute Path to the asset
    """
    return root_dir() / relative_path


def font_dir() -> Path:
    """Get the path to the fonts directory.

    Returns:
        Path to the assets/fonts directory
    """
    return root_dir() / "assets" / "fonts"


def font_names() -> list[str]:
    """Get available font names.

    Returns:
        List of font names (without .ttf extension)
    """
    fonts_path = font_dir()
    if not fonts_path.exists():
        return []
    return [font.stem for font in fonts_path.glob("*.ttf")]


def font_path(font_name: str) -> Path:
    """Get the path to a font file.

    Args:
        font_name: Name of the font (without extension)

    Returns:
        Path to the font file
    """
    return font_dir() / f"{font_name}.ttf"


def default_font_path() -> Path:
    """Get the path to the default font.

    Returns:
        Path to Kalam-Regular.ttf
    """
    return font_path("Kalam-Regular")


def colormaps() -> list[str]:
    """Get available colormap names.

    Returns:
        List of colormap names from colormaps.txt
    """
    colormaps_path = root_dir() / "assets" / "colormaps.txt"
    if not colormaps_path.exists():
        return []
    with colormaps_path.open(encoding="utf-8") as f:
        return f.read().splitlines()
