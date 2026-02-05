"""I/O operations for Canvas (canmore) documents."""

from __future__ import annotations

import logging
from pathlib import Path

from convoviz.models import ConversationCollection
from convoviz.utils import sanitize

logger = logging.getLogger(__name__)

# Map common Canvas MIME types to file extensions
EXTENSION_MAP = {
    "code/html": ".html",
    "code/python": ".py",
    "code/javascript": ".js",
    "code/typescript": ".ts",
    "code/css": ".css",
    "code/json": ".json",
    "code/bash": ".sh",
    "code/shell": ".sh",
    "document/markdown": ".md",
    "text/plain": ".txt",
}


def get_extension(mime_type: str | None) -> str:
    """Get file extension from MIME type."""
    if not mime_type:
        return ".txt"
    return EXTENSION_MAP.get(mime_type, ".txt")


def save_canvas_documents(
    collection: ConversationCollection,
    output_dir: Path,
) -> int:
    """Extract and save all Canvas documents from a collection.

    Args:
        collection: The collection to extract from
        output_dir: Base output directory (docs will go in 'canvas/' subdir)

    Returns:
        Number of documents saved
    """
    canvas_dir = output_dir / "canvas"
    docs = collection.all_canvas_documents
    if not docs:
        return 0

    canvas_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Extracting {len(docs)} Canvas documents to {canvas_dir}")

    saved_count = 0
    for doc in docs:
        name = doc["name"]
        content = doc["content"]
        mime_type = doc["type"]
        conv_id = doc["conversation_id"][:8]  # Short ID for prefix

        ext = get_extension(mime_type)
        # Prefix with short conversation ID to avoid collisions between identically named docs
        filename = sanitize(f"[{conv_id}] {name}{ext}")
        filepath = canvas_dir / filename

        try:
            with filepath.open("w", encoding="utf-8") as f:
                f.write(content)
            saved_count += 1
            logger.debug(f"Saved Canvas doc: {filename}")
        except Exception as e:
            logger.error(f"Failed to save Canvas doc {filename}: {e}")

    return saved_count
