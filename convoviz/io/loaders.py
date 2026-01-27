"""Loading functions for conversations and collections."""

import logging
from pathlib import Path, PurePosixPath
from zipfile import ZipFile

from orjson import loads

from convoviz.exceptions import InvalidZipError
from convoviz.models import Conversation, ConversationCollection

logger = logging.getLogger(__name__)


def _is_safe_zip_member_name(name: str) -> bool:
    """Return True if a ZIP entry name is safe to extract.

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
    if first.endswith(":") or first.startswith("//") or first.startswith("\\\\"):
        return False

    return ".." not in member_path.parts


def extract_archive(filepath: Path) -> Path:
    """Extract a ZIP file and return the extraction folder path.

    Includes safety checks to prevent Path Traversal (Zip-Slip).

    Args:
        filepath: Path to the ZIP file

    Returns:
        Path to the extracted folder

    Raises:
        InvalidZipError: If extraction fails or a security risk is detected
    """
    folder = filepath.with_suffix("")
    folder.mkdir(parents=True, exist_ok=True)
    logger.info(f"Extracting archive: {filepath} to {folder}")

    with ZipFile(filepath) as zf:
        for member in zf.infolist():
            # Check for path traversal (Zip-Slip) in an OS-agnostic way.
            # ZIP files are typically POSIX-path-like, but malicious archives can
            # embed backslashes or drive-letter tricks.
            if not _is_safe_zip_member_name(member.filename):
                raise InvalidZipError(
                    str(filepath), reason=f"Malicious path in ZIP: {member.filename}"
                )

            # Additional check using resolved paths
            normalized = member.filename.replace("\\", "/")
            target_path = (folder / normalized).resolve()
            if not target_path.is_relative_to(folder.resolve()):
                raise InvalidZipError(
                    str(filepath), reason=f"Malicious path in ZIP: {member.filename}"
                )

        zf.extractall(folder)
    return folder


def validate_zip(filepath: Path) -> bool:
    """Check if a ZIP file contains conversations.json.

    Args:
        filepath: Path to the ZIP file

    Returns:
        True if valid, False otherwise
    """
    if not filepath.is_file() or filepath.suffix != ".zip":
        return False
    try:
        with ZipFile(filepath) as zf:
            return "conversations.json" in zf.namelist()
    except Exception:
        return False


def load_conversation_from_json(filepath: Path | str) -> Conversation:
    """Load a single conversation from a JSON file.

    Args:
        filepath: Path to the JSON file

    Returns:
        Loaded Conversation object
    """
    filepath = Path(filepath)
    with filepath.open(encoding="utf-8") as f:
        data = loads(f.read())
    return Conversation(**data)


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

    return ConversationCollection(conversations=data, source_path=filepath.parent)


def load_collection_from_zip(filepath: Path | str) -> ConversationCollection:
    """Load a conversation collection from a ChatGPT export ZIP file.

    Args:
        filepath: Path to the ZIP file

    Returns:
        Loaded ConversationCollection object

    Raises:
        InvalidZipError: If the ZIP file is invalid or missing conversations.json
    """
    filepath = Path(filepath)

    if not validate_zip(filepath):
        raise InvalidZipError(str(filepath))

    extracted_folder = extract_archive(filepath)
    conversations_path = extracted_folder / "conversations.json"

    return load_collection_from_json(conversations_path)


def find_latest_zip(directory: Path | None = None) -> Path | None:
    """Find the most recently created ZIP file in a directory.

    Args:
        directory: Directory to search (defaults to ~/Downloads)

    Returns:
        Path to the most recent ZIP, or None if none found
    """
    if directory is None:
        directory = Path.home() / "Downloads"

    zip_files = list(directory.glob("*.zip"))
    if not zip_files:
        return None

    return max(zip_files, key=lambda p: p.stat().st_ctime)


def find_latest_bookmarklet_json(directory: Path | None = None) -> Path | None:
    """Find the most recent bookmarklet JSON file in a directory.

    Args:
        directory: Directory to search (defaults to ~/Downloads)

    Returns:
        Path to the most recent bookmarklet JSON, or None if none found
    """
    if directory is None:
        directory = Path.home() / "Downloads"

    bookmarklet_files = [f for f in directory.glob("*.json") if "bookmarklet" in f.name.lower()]
    if not bookmarklet_files:
        return None

    return max(bookmarklet_files, key=lambda p: p.stat().st_ctime)
