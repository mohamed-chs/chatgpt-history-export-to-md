"""Loading functions for conversations and collections."""

from pathlib import Path
from zipfile import ZipFile

from orjson import loads

from convoviz.exceptions import InvalidZipError
from convoviz.models import Conversation, ConversationCollection


def extract_archive(filepath: Path) -> Path:
    """Extract a ZIP file and return the extraction folder path.

    Args:
        filepath: Path to the ZIP file

    Returns:
        Path to the extracted folder
    """
    folder = filepath.with_suffix("")
    with ZipFile(filepath) as zf:
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

    The JSON file should contain an array of conversation objects.

    Args:
        filepath: Path to the JSON file

    Returns:
        Loaded ConversationCollection object
    """
    filepath = Path(filepath)
    with filepath.open(encoding="utf-8") as f:
        data = loads(f.read())
    return ConversationCollection(conversations=data)


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
