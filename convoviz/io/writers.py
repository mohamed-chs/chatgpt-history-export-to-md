"""Writing functions for conversations and collections."""

from os import utime as os_utime
from pathlib import Path

from orjson import OPT_INDENT_2, dumps
from tqdm import tqdm

from convoviz.config import AuthorHeaders, ConversationConfig
from convoviz.io.assets import copy_asset, resolve_asset_path
from convoviz.models import Conversation, ConversationCollection
from convoviz.renderers import render_conversation
from convoviz.utils import sanitize


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
    progress_bar: bool = False,
) -> None:
    """Save all conversations in a collection to markdown files.

    Args:
        collection: The collection to save
        directory: Target directory
        config: Conversation rendering configuration
        headers: Author header configuration
        progress_bar: Whether to show a progress bar
    """
    directory.mkdir(parents=True, exist_ok=True)

    for conv in tqdm(
        collection.conversations,
        desc="Writing Markdown 📄 files",
        disable=not progress_bar,
    ):
        filepath = directory / f"{sanitize(conv.title)}.md"
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
