"""Word cloud generation for conversation text."""

import logging
import os
from concurrent.futures import ProcessPoolExecutor
from functools import lru_cache
from pathlib import Path

from nltk import download as nltk_download
from nltk.corpus import stopwords as nltk_stopwords
from nltk.data import find as nltk_find
from PIL.Image import Image
from tqdm import tqdm
from wordcloud import WordCloud

from convoviz.config import WordCloudConfig
from convoviz.models import ConversationCollection

logger = logging.getLogger(__name__)

# Languages for stopwords
STOPWORD_LANGUAGES = [
    "arabic",
    "english",
    "french",
    "german",
    "spanish",
    "portuguese",
]


@lru_cache(maxsize=1)
def load_programming_stopwords() -> frozenset[str]:
    """Load programming keywords and types from assets.

    Returns:
        Frozen set of programming stop words
    """
    stopwords_path = Path(__file__).parent.parent / "assets" / "stopwords.txt"
    if not stopwords_path.exists():
        return frozenset()

    with open(stopwords_path, encoding="utf-8") as f:
        return frozenset(
            line.strip().lower() for line in f if line.strip() and not line.strip().startswith("#")
        )


@lru_cache(maxsize=1)
def load_nltk_stopwords() -> frozenset[str]:
    """Load and cache NLTK stopwords.

    Downloads stopwords if not already present.

    Returns:
        Frozen set of stopwords from multiple languages
    """
    try:
        nltk_find("corpora/stopwords")
    except LookupError:
        nltk_download("stopwords", quiet=True)

    words: set[str] = set()
    for lang in STOPWORD_LANGUAGES:
        words.update(nltk_stopwords.words(fileids=lang))

    return frozenset(words)


def parse_custom_stopwords(stopwords_str: str | None) -> set[str]:
    """Parse a comma-separated string of custom stopwords.

    Args:
        stopwords_str: Comma-separated stopwords

    Returns:
        Set of lowercase, stripped stopwords
    """
    if not stopwords_str:
        return set()

    return {word.strip().lower() for word in stopwords_str.split(",") if word.strip()}


def generate_wordcloud(text: str, config: WordCloudConfig) -> Image:
    """Generate a word cloud from text.

    Args:
        text: The text to create a word cloud from
        config: Word cloud configuration

    Returns:
        PIL Image of the word cloud
    """
    # Combine NLTK and custom stopwords
    stopwords = set(load_nltk_stopwords())
    stopwords.update(parse_custom_stopwords(config.custom_stopwords))

    if config.exclude_programming_keywords:
        stopwords.update(load_programming_stopwords())

    wc = WordCloud(
        font_path=str(config.font_path) if config.font_path else None,
        width=config.width,
        height=config.height,
        stopwords=stopwords,
        background_color=config.background_color,
        mode=config.mode,
        colormap=config.colormap,
        include_numbers=config.include_numbers,
    )

    wc.generate(text)
    result: Image = wc.to_image()
    return result


def _generate_and_save_wordcloud(args: tuple[str, str, Path, WordCloudConfig]) -> bool:
    """Worker function for parallel wordcloud generation.

    Must be at module level for pickling by ProcessPoolExecutor.

    Args:
        args: Tuple of (text, filename, output_dir, config)

    Returns:
        True if wordcloud was generated, False if skipped (empty text)
    """
    text, filename, output_dir, config = args
    if not text.strip():
        return False
    img = generate_wordcloud(text, config)
    img.save(output_dir / filename, optimize=True)
    return True


def generate_wordclouds(
    collection: ConversationCollection,
    output_dir: Path,
    config: WordCloudConfig,
    *,
    progress_bar: bool = False,
) -> None:
    """Generate word clouds for weekly, monthly, and yearly groupings.

    Uses parallel processing to speed up generation on multi-core systems.

    Args:
        collection: Collection of conversations
        output_dir: Directory to save the word clouds
        config: Word cloud configuration
        progress_bar: Whether to show progress bars
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Generating wordclouds to {output_dir}")

    week_groups = collection.group_by_week()
    month_groups = collection.group_by_month()
    year_groups = collection.group_by_year()

    # Pre-load/download NLTK stopwords in the main process to avoid race conditions in workers
    load_nltk_stopwords()

    # Build list of all tasks: (text, filename, output_dir, config)
    tasks: list[tuple[str, str, Path, WordCloudConfig]] = []

    for week, group in week_groups.items():
        text = group.plaintext("user", "assistant")
        # Format: 2024-W15.png (ISO week format)
        filename = f"{week.strftime('%Y-W%W')}.png"
        tasks.append((text, filename, output_dir, config))

    for month, group in month_groups.items():
        text = group.plaintext("user", "assistant")
        # Format: 2024-03-March.png (consistent with folder naming)
        filename = f"{month.strftime('%Y-%m-%B')}.png"
        tasks.append((text, filename, output_dir, config))

    for year, group in year_groups.items():
        text = group.plaintext("user", "assistant")
        # Format: 2024.png
        filename = f"{year.strftime('%Y')}.png"
        tasks.append((text, filename, output_dir, config))

    if not tasks:
        return

    # Determine worker count: use config if set, otherwise half CPU count (min 1)
    max_workers = config.max_workers
    if max_workers is None:
        cpu_count = os.cpu_count() or 2
        max_workers = max(1, cpu_count // 2)

    # Use parallel processing for speedup on multi-core systems
    logger.debug(f"Starting wordcloud generation with {max_workers} workers for {len(tasks)} tasks")
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        list(
            tqdm(
                executor.map(_generate_and_save_wordcloud, tasks),
                total=len(tasks),
                desc="Creating wordclouds 🔡☁️",
                disable=not progress_bar,
            )
        )
