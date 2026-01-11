"""Writing functions for conversations and collections."""

from os import utime as os_utime
from pathlib import Path

from orjson import OPT_INDENT_2, dumps
from tqdm import tqdm

from convoviz.config import AuthorHeaders, ConversationConfig, FolderOrganization
from convoviz.io.assets import copy_asset, resolve_asset_path
from convoviz.models import Conversation, ConversationCollection
from convoviz.renderers import render_conversation
from convoviz.utils import sanitize

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

    Creates a nested structure: year/month/week
    Example: 2024/03-March/Week-02/

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

    # Week folder: "Week-01" through "Week-05" (week of the month)
    # Calculate which week of the month this date falls into
    day = create_time.day
    week_of_month = (day - 1) // 7 + 1
    week = f"Week-{week_of_month:02d}"

    return Path(year) / month / week


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

    # Set modification time
    timestamp = conversation.update_time.timestamp()
    os_utime(final_path, (timestamp, timestamp))

    return final_path


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
