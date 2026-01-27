"""Writing functions for conversations and collections."""

import logging
from os import utime as os_utime
from pathlib import Path
from urllib.parse import quote

from orjson import OPT_INDENT_2, dumps
from tqdm import tqdm

from convoviz.config import AuthorHeaders, ConversationConfig, FolderOrganization
from convoviz.io.assets import copy_asset, resolve_asset_path
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


def save_conversation(
    conversation: Conversation,
    filepath: Path,
    config: ConversationConfig,
    headers: AuthorHeaders,
    source_path: Path | None = None,
) -> Path:
    """Save a conversation to a markdown file.

    Handles filename conflicts by appending a counter. Sets the file's
    modification time to match the conversation's update time.

    Args:
        conversation: The conversation to save
        filepath: Target file path
        config: Conversation rendering configuration
        headers: Author header configuration
        source_path: Path to the source directory containing assets

    Returns:
        The actual path the file was saved to (may differ if there was a conflict)
    """
    # Handle filename conflicts
    base_name = sanitize(filepath.stem)
    final_path = filepath
    counter = 0

    while final_path.exists():
        counter += 1
        final_path = filepath.with_name(f"{base_name} ({counter}){filepath.suffix}")

    # Define asset resolver
    def asset_resolver(asset_id: str) -> str | None:
        if not source_path:
            return None

        src_file = resolve_asset_path(source_path, asset_id)
        if not src_file:
            return None

        # Copy to output directory (relative to the markdown file's directory)
        return copy_asset(src_file, final_path.parent)

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
    progress_bar: bool = False,
) -> None:
    """Save all conversations in a collection to markdown files.

    Args:
        collection: The collection to save
        directory: Target directory
        config: Conversation rendering configuration
        headers: Author header configuration
        folder_organization: How to organize files in folders (flat or by date)
        progress_bar: Whether to show a progress bar
    """
    directory.mkdir(parents=True, exist_ok=True)

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

        filepath = target_dir / f"{sanitize(conv.title)}.md"
        save_conversation(conv, filepath, config, headers, source_path=collection.source_path)

    # Generate index files for date organization
    if folder_organization == FolderOrganization.DATE:
        for year_dir in directory.iterdir():
            if year_dir.is_dir() and year_dir.name.isdigit():
                for month_dir in year_dir.iterdir():
                    if month_dir.is_dir():
                        _generate_month_index(month_dir, year_dir.name, month_dir.name)
                _generate_year_index(year_dir, year_dir.name)


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
