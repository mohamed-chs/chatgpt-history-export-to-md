"""Utility functions for convoviz."""

import re
from pathlib import Path


def sanitize(filename: str) -> str:
    """Sanitize a string to be safe for use as a filename.

    Replaces invalid characters with underscores.

    Args:
        filename: The string to sanitize

    Returns:
        A filename-safe string, or "untitled" if empty
    """
    pattern = re.compile(r'[<>:"/\\|?*\n\r\t\f\v]+')
    result = pattern.sub("_", filename.strip())
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
        Path to RobotoSlab-Thin.ttf
    """
    return font_path("RobotoSlab-Thin")


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
