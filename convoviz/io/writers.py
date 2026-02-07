"""Writing functions for conversations and collections."""

import logging
import re
from datetime import datetime
from os import utime as os_utime
from pathlib import Path
from urllib.parse import quote

from orjson import OPT_INDENT_2, dumps
from tqdm import tqdm

from convoviz.config import AuthorHeaders, ConversationConfig, FolderOrganization
from convoviz.io.assets import AssetIndex, build_asset_index, copy_asset, resolve_asset_path
from convoviz.models import Conversation, ConversationCollection
from convoviz.renderers import render_conversation
from convoviz.utils import sanitize

logger = logging.getLogger(__name__)

# Month names for folder naming
_MONTH_NAMES = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]


def get_date_folder_path(conversation: Conversation) -> Path:
    """Get the date-based folder path for a conversation.

    Creates a nested structure: year/month
    Example: 2024/03-March/

    Args:
        conversation: The conversation to get the path for

    Returns:
        Relative path for the date-based folder structure
    """
    create_time = conversation.create_time

    # Year folder: "2024"
    year = str(create_time.year)

    # Month folder: "03-March"
    month_num = create_time.month
    month_name = _MONTH_NAMES[month_num - 1]
    month = f"{month_num:02d}-{month_name}"

    return Path(year) / month


_ID_SCAN_LIMIT = 128 * 1024


def _get_conversation_id_from_file(filepath: Path) -> str | None:
    """Extract conversation_id from an existing markdown file's YAML frontmatter.

    Scans a bounded prefix of the file to avoid loading huge files.
    """
    try:
        with filepath.open("r", encoding="utf-8") as f:
            content = f.read(_ID_SCAN_LIMIT)

        # Check hidden marker first
        marker = re.search(
            r"<!--\s*conversation_id=([^>\s]+)\s*-->",
            content,
            re.IGNORECASE,
        )
        if marker:
            return marker.group(1)
        # Look for conversation_id: "id"
        match = re.search(r'^conversation_id:\s*"([^"]+)"', content, re.MULTILINE)
        if match:
            return match.group(1)
        # Fallback: check chat_link
        match = re.search(
            r'^chat_link:\s*"https://(?:chatgpt\.com|chat\.openai\.com)/c/([^"]+)"',
            content,
            re.MULTILINE,
        )
        if match:
            return match.group(1)
    except Exception:
        pass
    return None


def _build_markdown_filename(
    title: str,
    *,
    prepend_timestamp: bool,
    create_time: datetime,
    suffix: str = ".md",
    max_length: int = 255,
) -> str:
    sanitized_title = sanitize(title)
    prefix = f"{create_time.strftime('%Y-%m-%d_%H-%M-%S')} - " if prepend_timestamp else ""
    available = max_length - len(prefix) - len(suffix)
    if available < 1:
        truncated = "untitled"
    else:
        truncated = (
            sanitized_title[:available] if len(sanitized_title) > available else sanitized_title
        )
    return f"{prefix}{truncated}{suffix}"


def save_conversation(
    conversation: Conversation,
    filepath: Path,
    config: ConversationConfig,
    headers: AuthorHeaders,
    source_paths: list[Path] | None = None,
    asset_indexes: dict[Path, AssetIndex] | None = None,
) -> Path:
    """Save a conversation to a markdown file.

    Handles filename conflicts by appending a counter. If a file with the same
    title exists, it overwrites it ONLY if it belongs to the same conversation ID.
    Otherwise, it increments the filename.
    """
    base_name = sanitize(filepath.stem)
    final_path = filepath
    counter = 0

    while final_path.exists():
        # Check if this existing file is the SAME conversation
        existing_id = _get_conversation_id_from_file(final_path)
        if existing_id == conversation.conversation_id:
            logger.debug(f"Identity match for {final_path.name}, overwriting.")
            break

        # Different conversation with same title, increment
        counter += 1
        final_path = filepath.with_name(f"{base_name} ({counter}){filepath.suffix}")

    if asset_indexes is None:
        asset_indexes = {}
        if source_paths:
            asset_indexes = {path: build_asset_index(path) for path in source_paths}

    # Define asset resolver
    def asset_resolver(asset_id: str, target_name: str | None = None) -> str | None:
        if not source_paths:
            return None

        for source_path in source_paths:
            src_file = resolve_asset_path(
                source_path, asset_id, index=asset_indexes.get(source_path)
            )
            if src_file:
                # Copy to output directory (relative to the markdown file's directory)
                return copy_asset(
                    src_file,
                    final_path.parent,
                    target_name,
                    convert_webp_to_png=config.markdown.flavor == "pandoc",
                )

        return None

    # Render and write
    markdown = render_conversation(conversation, config, headers, asset_resolver=asset_resolver)
    with final_path.open("w", encoding="utf-8") as f:
        f.write(markdown)
    logger.debug(f"Saved conversation: {final_path}")

    # Set modification time
    timestamp = conversation.update_time.timestamp()
    os_utime(final_path, (timestamp, timestamp))

    return final_path


def _generate_year_index(year_dir: Path, year: str) -> None:
    """Generate a _index.md file for a year folder.

    Args:
        year_dir: Path to the year directory
        year: The year string (e.g., "2024")
    """
    months = sorted(
        [d.name for d in year_dir.iterdir() if d.is_dir()],
        key=lambda m: int(m.split("-")[0]),
    )

    lines = [
        f"# {year}",
        "",
        "## Months",
        "",
    ]

    for month in months:
        month_name = month.split("-", 1)[1] if "-" in month else month
        lines.append(f"- [{month_name}]({month}/_index.md)")

    index_path = year_dir / "_index.md"
    index_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    logger.debug(f"Generated year index: {index_path}")


def _generate_root_index(root_dir: Path) -> None:
    """Generate a top-level _index.md that links to year indexes."""
    years = sorted([d.name for d in root_dir.iterdir() if d.is_dir() and d.name.isdigit()])
    if not years:
        return

    lines = [
        "# ChatGPT Conversations",
        "",
        "## Years",
        "",
    ]

    for year in years:
        encoded = quote(f"{year}/_index.md")
        lines.append(f"- [{year}]({encoded})")

    index_path = root_dir / "_index.md"
    index_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    logger.debug(f"Generated root index: {index_path}")


def _generate_month_index(month_dir: Path, year: str, month: str) -> None:
    """Generate a _index.md file for a month folder.

    Args:
        month_dir: Path to the month directory
        year: The year string (e.g., "2024")
        month: The month folder name (e.g., "03-March")
    """
    month_name = month.split("-", 1)[1] if "-" in month else month
    files = sorted([f.name for f in month_dir.glob("*.md") if f.name != "_index.md"])

    lines = [
        f"# {month_name} {year}",
        "",
        "## Conversations",
        "",
    ]

    for file in files:
        title = file[:-3]  # Remove .md extension
        encoded_file = quote(file)
        lines.append(f"- [{title}]({encoded_file})")

    index_path = month_dir / "_index.md"
    index_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    logger.debug(f"Generated month index: {index_path}")


def save_collection(
    collection: ConversationCollection,
    directory: Path,
    config: ConversationConfig,
    headers: AuthorHeaders,
    *,
    folder_organization: FolderOrganization = FolderOrganization.FLAT,
    prepend_timestamp: bool = False,
    progress_bar: bool = False,
) -> None:
    """Save all conversations in a collection to markdown files.

    Args:
        collection: The collection to save
        directory: Target directory
        config: Conversation rendering configuration
        headers: Author header configuration
        folder_organization: How to organize files in folders (flat or by date)
        prepend_timestamp: Whether to prepend the conversation timestamp to the filename
        progress_bar: Whether to show a progress bar
    """
    directory.mkdir(parents=True, exist_ok=True)

    asset_indexes: dict[Path, AssetIndex] | None = None
    if collection.source_paths:
        asset_indexes = {path: build_asset_index(path) for path in collection.source_paths}

    for conv in tqdm(
        collection.conversations,
        desc="Writing Markdown 📄 files",
        disable=not progress_bar,
    ):
        # Determine target directory based on organization setting
        if folder_organization == FolderOrganization.DATE:
            target_dir = directory / get_date_folder_path(conv)
            target_dir.mkdir(parents=True, exist_ok=True)
        else:
            target_dir = directory

        # Determine filename
        filename = _build_markdown_filename(
            conv.title,
            prepend_timestamp=prepend_timestamp,
            create_time=conv.create_time,
        )

        filepath = target_dir / filename
        save_conversation(
            conv,
            filepath,
            config,
            headers,
            source_paths=collection.source_paths,
            asset_indexes=asset_indexes,
        )

    # Generate index files for date organization
    if folder_organization == FolderOrganization.DATE:
        for year_dir in directory.iterdir():
            if year_dir.is_dir() and year_dir.name.isdigit():
                for month_dir in year_dir.iterdir():
                    if month_dir.is_dir():
                        _generate_month_index(month_dir, year_dir.name, month_dir.name)
                _generate_year_index(year_dir, year_dir.name)
        _generate_root_index(directory)


def save_custom_instructions(
    collection: ConversationCollection,
    filepath: Path,
) -> None:
    """Save all custom instructions from a collection to a JSON file.

    Args:
        collection: The collection to extract instructions from
        filepath: Target JSON file path
    """
    instructions = collection.custom_instructions
    with filepath.open("w", encoding="utf-8") as f:
        f.write(dumps(instructions, option=OPT_INDENT_2).decode())
