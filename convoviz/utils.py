"""Utility functions for convoviz."""

from __future__ import annotations

import os
import re
import tempfile
import unicodedata
from collections.abc import Mapping
from datetime import datetime
from importlib import resources
from pathlib import Path
from typing import Any

from convoviz.exceptions import ConfigurationError

WEEKDAYS = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]


def day_start(dt: datetime) -> datetime:
    """Get the start of the day for a datetime."""
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)


def month_start(dt: datetime) -> datetime:
    """Get the start of the month for a datetime."""
    return dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def year_start(dt: datetime) -> datetime:
    """Get the start of the year for a datetime."""
    return dt.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)


def sanitize(text: str) -> str:
    """Sanitize a string to be safe for filenames and YAML titles.

    - Transliterates non-ASCII to ASCII when possible.
    - Removes non-ASCII that cannot be converted.
    - Replaces invalid characters with spaces.
    - Prevents path traversal.
    - Collapses multiple spaces and trims.

    Args:
        text: The string to sanitize

    Returns:
        A safe ASCII string, or "untitled" if empty or invalid
    """
    # 1. Transliterate to ASCII (e.g. 'é' -> 'e')
    # NFKD decomposes characters (e.g. 'é' to 'e' + '`')
    # then we encode to ascii and ignore non-ascii parts.
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")

    # 2. Replace single quotes with spaces
    ascii_text = ascii_text.replace("'", " ")

    # 3. Replace invalid characters with spaces
    # (including @ which messes with some PDF tools)
    pattern = re.compile(r'[@<>:"/\\|?*\n\r\t\f\v]+')
    result = pattern.sub(" ", ascii_text)

    # 4. Prevent path traversal by replacing dots with spaces
    result = result.replace("..", " ")

    # 5. Collapse multiple spaces and trim
    # This also "removes" trouble characters from beginning/end
    result = re.sub(r"\s+", " ", result).strip()

    # 6. Remove leading/trailing dots (can cause issues on some systems)
    result = result.strip(".")
    result = result.strip()  # Final trim in case dots left spaces

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

    # Enforce length limit
    if len(result) > 255:
        result = result[:255]

    return result or "untitled"


def validate_header(text: str) -> bool:
    """Check if text is a valid markdown header (1-6 # followed by space)."""
    if not text.startswith("#"):
        return False

    parts = text.split(maxsplit=1)
    if len(parts) < 2:
        return False

    hashes = parts[0]
    return hashes == "#" * len(hashes) and 1 <= len(hashes) <= 6


def get_resource_path(relative_path: str) -> Path:
    """Get the absolute path to a bundled resource.

    Args:
        relative_path: Path relative to convoviz root (e.g., "assets/fonts/foo.ttf")

    Returns:
        Absolute Path to the resource
    """
    pkg_path = resources.files("convoviz")
    for part in relative_path.split("/"):
        pkg_path = pkg_path.joinpath(part)

    with resources.as_file(pkg_path) as path:
        return Path(path).resolve()


def font_names() -> list[str]:
    """Get available font names (without .ttf extension)."""
    fonts_dir = resources.files("convoviz").joinpath("assets/fonts")
    if not fonts_dir.is_dir():
        return []
    return [Path(p.name).stem for p in fonts_dir.iterdir() if p.name.endswith(".ttf")]


def font_path(font_name: str) -> Path:
    """Get the path to a bundled font file."""
    return get_resource_path(f"assets/fonts/{font_name}.ttf")


def default_font_path() -> Path:
    """Get the path to the default font (Kalam-Regular)."""
    return font_path("Kalam-Regular")


def colormaps() -> list[str]:
    """Get available colormap names from colormaps.txt."""
    path = get_resource_path("assets/colormaps.txt")
    if not path.exists():
        return []
    return path.read_text(encoding="utf-8").splitlines()


def expand_path(value: str) -> Path:
    """Expand environment variables and user home in a path string."""
    expanded = os.path.expandvars(str(Path(value).expanduser()))
    return Path(expanded)


def normalize_optional_path(value: str | Path | None) -> Path | None:
    """Normalize optional path-like values, treating empty strings as None."""
    if value is None:
        return None
    if isinstance(value, Path):
        return value
    stripped = value.strip()
    if not stripped:
        return None
    return expand_path(stripped)


def deep_merge_dicts(
    base: Mapping[str, Any], override: Mapping[str, Any]
) -> dict[str, Any]:
    """Deep-merge mapping values, preferring values from override."""
    merged: dict[str, Any] = dict(base)
    for key, value in override.items():
        if isinstance(value, Mapping) and isinstance(base.get(key), Mapping):
            merged[key] = deep_merge_dicts(base[key], value)
        else:
            merged[key] = value
    return merged


def validate_writable_dir(path: Path, create: bool = False) -> None:
    """Validate that a directory (or its closest existing parent) is writable.

    Args:
        path: The directory path to validate.
        create: If True, creates the directory if it doesn't exist.

    Raises:
        ConfigurationError: If the path is not a directory or is not writable.
    """

    def test_write(target: Path) -> None:
        try:
            with tempfile.NamedTemporaryFile(
                dir=target, prefix=".convoviz_test_", delete=True
            ):
                pass
        except OSError as exc:
            msg = f"Directory not writable: {target}"
            raise ConfigurationError(msg) from exc

    if create:
        try:
            path.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            msg = f"Cannot create directory: {path}"
            raise ConfigurationError(msg) from exc

    if path.exists():
        if not path.is_dir():
            msg = f"Not a directory: {path}"
            raise ConfigurationError(msg)
        test_write(path)
        return

    # If not existing and not creating, check closest existing parent
    for parent in path.parents:
        if parent.exists():
            if not parent.is_dir():
                msg = f"Parent is not a directory: {parent}"
                raise ConfigurationError(msg)
            test_write(parent)
            return
