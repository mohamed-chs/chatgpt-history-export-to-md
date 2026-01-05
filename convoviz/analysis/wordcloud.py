"""Word cloud generation for conversation text."""

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


def parse_custom_stopwords(stopwords_str: str) -> set[str]:
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


def generate_wordclouds(
    collection: ConversationCollection,
    output_dir: Path,
    config: WordCloudConfig,
    *,
    progress_bar: bool = False,
) -> None:
    """Generate word clouds for weekly, monthly, and yearly groupings.

    Args:
        collection: Collection of conversations
        output_dir: Directory to save the word clouds
        config: Word cloud configuration
        progress_bar: Whether to show progress bars
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    week_groups = collection.group_by_week()
    month_groups = collection.group_by_month()
    year_groups = collection.group_by_year()

    for week, group in tqdm(
        week_groups.items(),
        desc="Creating weekly wordclouds 🔡☁️",
        disable=not progress_bar,
    ):
        text = group.plaintext("user", "assistant")
        if text.strip():
            img = generate_wordcloud(text, config)
            img.save(output_dir / f"{week.strftime('%Y week %W')}.png", optimize=True)

    for month, group in tqdm(
        month_groups.items(),
        desc="Creating monthly wordclouds 🔡☁️",
        disable=not progress_bar,
    ):
        text = group.plaintext("user", "assistant")
        if text.strip():
            img = generate_wordcloud(text, config)
            img.save(output_dir / f"{month.strftime('%Y %B')}.png", optimize=True)

    for year, group in tqdm(
        year_groups.items(),
        desc="Creating yearly wordclouds 🔡☁️",
        disable=not progress_bar,
    ):
        text = group.plaintext("user", "assistant")
        if text.strip():
            img = generate_wordcloud(text, config)
            img.save(output_dir / f"{year.strftime('%Y')}.png", optimize=True)
