"""Loading functions for conversations and collections."""

import logging
from pathlib import Path, PurePosixPath
from zipfile import ZipFile

from orjson import loads

from convoviz.exceptions import InvalidZipError
from convoviz.models import ConversationCollection

logger = logging.getLogger(__name__)


def _is_safe_zip_member_name(name: str) -> bool:
    r"""Return True if a ZIP entry name is safe to extract.

    This is intentionally OS-agnostic: it treats both ``/`` and ``\\`` as path
    separators and rejects absolute paths, drive-letter paths, and ``..`` parts.
    """
    normalized = name.replace("\\", "/")
    member_path = PurePosixPath(normalized)

    # Absolute paths (e.g. "/etc/passwd") or empty names
    if not normalized or member_path.is_absolute():
        return False

    # Windows drive letters / UNC-style prefixes stored in the archive
    first = member_path.parts[0] if member_path.parts else ""
    if first.endswith(":") or first.startswith(("//", "\\\\")):
        return False

    return ".." not in member_path.parts


def extract_archive(filepath: Path, target_dir: Path) -> Path:
    """Extract a ZIP file to the target folder.

    Includes safety checks to prevent Path Traversal (Zip-Slip).

    Args:
        filepath: Path to the ZIP file
        target_dir: Path where to extract

    Returns:
        Path to the extracted folder (target_dir)

    Raises:
        InvalidZipError: If extraction fails or a security risk is detected

    """
    logger.info(f"Extracting archive: {filepath} to {target_dir}")

    with ZipFile(filepath) as zf:
        for member in zf.infolist():
            if not _is_safe_zip_member_name(member.filename):
                raise InvalidZipError(
                    str(filepath), reason=f"Malicious path in ZIP: {member.filename}"
                )

            # Additional check using resolved paths
            normalized = member.filename.replace("\\", "/")
            target_path = (target_dir / normalized).resolve()
            if not target_path.is_relative_to(target_dir.resolve()):
                raise InvalidZipError(
                    str(filepath), reason=f"Malicious path in ZIP: {member.filename}"
                )

        zf.extractall(target_dir)
    return target_dir


def validate_zip(filepath: Path) -> bool:
    """Check if a ZIP file contains conversations.json.

    Args:
        filepath: Path to the ZIP file

    Returns:
        True if valid, False otherwise

    """
    if not filepath.is_file() or filepath.suffix.lower() != ".zip":
        return False
    try:
        with ZipFile(filepath) as zf:
            return "conversations.json" in zf.namelist()
    except Exception:
        return False


def load_collection_from_json(filepath: Path | str) -> ConversationCollection:
    """Load a conversation collection from a JSON file.

    The JSON file should contain an array of conversation objects,
    or an object with a "conversations" key.

    Args:
        filepath: Path to the JSON file

    Returns:
        Loaded ConversationCollection object

    """
    filepath = Path(filepath)
    logger.debug(f"Loading collection from JSON: {filepath}")
    with filepath.open(encoding="utf-8") as f:
        data = loads(f.read())

    # Handle case where export is wrapped in a top-level object
    if isinstance(data, dict) and "conversations" in data:
        data = data["conversations"]

    return ConversationCollection(conversations=data, source_paths=[filepath.parent])


def load_collection_from_zip(
    filepath: Path | str, target_dir: Path
) -> ConversationCollection:
    """Load a conversation collection from a ChatGPT export ZIP file.

    Args:
        filepath: Path to the ZIP file
        target_dir: Directory to extract the ZIP into

    Returns:
        Loaded ConversationCollection object

    Raises:
        InvalidZipError: If the ZIP file is invalid or missing conversations.json

    """
    filepath = Path(filepath)

    if not validate_zip(filepath):
        raise InvalidZipError(str(filepath))

    extract_archive(filepath, target_dir)
    conversations_path = target_dir / "conversations.json"

    return load_collection_from_json(conversations_path)


def load_collection(input_path: Path, tmp_path: Path) -> ConversationCollection:
    """Load a conversation collection from a directory, JSON, or ZIP.

    Args:
        input_path: Path to the input (directory, JSON, or ZIP)
        tmp_path: Temporary directory for ZIP extraction

    Returns:
        Loaded ConversationCollection object

    """
    if input_path.is_dir():
        json_path = input_path / "conversations.json"
        if not json_path.exists():
            raise InvalidZipError(
                str(input_path), reason="Directory must contain conversations.json"
            )
        return load_collection_from_json(json_path)

    if input_path.suffix.lower() == ".json":
        return load_collection_from_json(input_path)

    return load_collection_from_zip(input_path, tmp_path)


def find_latest_valid_zip(directory: Path | None = None) -> Path | None:
    """Find the most recent valid ChatGPT export ZIP in a directory.

    A valid ZIP is one that contains conversations.json.

    Args:
        directory: Directory to search (defaults to ~/Downloads)

    Returns:
        Path to the most recent valid ZIP, or None if none found

    """
    if directory is None:
        directory = Path.home() / "Downloads"

    zip_files = [
        p for p in directory.iterdir() if p.is_file() and p.suffix.lower() == ".zip"
    ]
    if not zip_files:
        return None

    valid = [p for p in zip_files if validate_zip(p)]
    if not valid:
        return None

    return max(valid, key=lambda p: p.stat().st_mtime)


def find_script_export(directory: Path | None = None) -> Path | None:
    """Find the most recent script-generated export in a directory.

    Looks for files starting with "convoviz_export" and using .json/.zip.

    Args:
        directory: Directory to search (defaults to ~/Downloads)

    Returns:
        Path to the most recent export, or None if none found

    """
    if directory is None:
        directory = Path.home() / "Downloads"

    export_files = [
        f
        for f in directory.iterdir()
        if f.is_file()
        and f.name.lower().startswith("convoviz_export")
        and f.suffix.lower() in (".json", ".zip")
    ]

    if not export_files:
        return None

    return max(export_files, key=lambda p: p.stat().st_mtime)
