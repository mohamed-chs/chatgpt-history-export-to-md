"""Tests for word cloud generation and stop words."""

from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import patch

import pytest

from convoviz.analysis.wordcloud import (
    _generate_and_save_wordcloud,
    generate_wordcloud,
    generate_wordclouds,
    load_nltk_stopwords,
    parse_custom_stopwords,
)
from convoviz.config import WordCloudConfig
from convoviz.models import Conversation, ConversationCollection


def test_load_nltk_stopwords():
    """Test that NLTK stopwords are loaded and cached."""
    stopwords = load_nltk_stopwords()
    assert isinstance(stopwords, frozenset)
    assert len(stopwords) > 0
    assert "the" in stopwords  # English
    assert "le" in stopwords  # French


def test_parse_custom_stopwords():
    """Test parsing of custom stopwords string."""
    assert parse_custom_stopwords("one, TWO ,three") == {"one", "two", "three"}
    assert parse_custom_stopwords("") == set()
    assert parse_custom_stopwords(None) == set()


@patch("convoviz.analysis.wordcloud.WordCloud")
def test_generate_wordcloud_no_programming_stopwords(mock_wc):
    """Test that generate_wordcloud respects exclude_programming_keywords=False."""
    config = WordCloudConfig(
        custom_stopwords="python",
        exclude_programming_keywords=False,
    )
    text = "This is a test with def class and int"

    generate_wordcloud(text, config)

    _args, kwargs = mock_wc.call_args
    passed_stopwords = kwargs.get("stopwords")

    assert "the" in passed_stopwords  # From NLTK
    assert "python" in passed_stopwords  # From custom
    assert "def" not in passed_stopwords  # Should NOT be there
    assert "class" not in passed_stopwords  # Should NOT be there
    assert kwargs.get("random_state") == config.random_state


def test_generate_and_save_wordcloud_skips_empty_text(tmp_path: Path):
    """Test that _generate_and_save_wordcloud skips empty text."""
    config = WordCloudConfig()
    result = _generate_and_save_wordcloud(("", "test.png", tmp_path, config))
    assert result is False
    assert not (tmp_path / "test.png").exists()

    result = _generate_and_save_wordcloud(("   ", "test2.png", tmp_path, config))
    assert result is False
    assert not (tmp_path / "test2.png").exists()


def test_generate_and_save_wordcloud_creates_file(tmp_path: Path):
    """Test that _generate_and_save_wordcloud creates a wordcloud file."""
    config = WordCloudConfig()
    text = "hello world python programming code test example"
    result = _generate_and_save_wordcloud((text, "test.png", tmp_path, config))
    assert result is True
    assert (tmp_path / "test.png").exists()


def test_generate_wordclouds_empty_collection(tmp_path: Path):
    """Test generate_wordclouds with an empty collection."""
    collection = ConversationCollection()
    config = WordCloudConfig()
    # Should not raise, just do nothing
    generate_wordclouds(collection, tmp_path, config)
    # No files should be created (only directory)
    assert list(tmp_path.glob("*.png")) == []


def test_generate_wordclouds_parallel(tmp_path: Path, mock_conversation):
    """Test that generate_wordclouds works with parallel execution."""
    collection = ConversationCollection(conversations=[mock_conversation])
    config = WordCloudConfig(max_workers=2)

    generate_wordclouds(collection, tmp_path, config)

    # Should create at least one wordcloud (weekly, monthly, or yearly)
    png_files = list(tmp_path.glob("*.png"))
    assert len(png_files) >= 1


def test_generate_wordclouds_single_worker(tmp_path: Path, mock_conversation):
    """Test that generate_wordclouds works with a single worker."""
    collection = ConversationCollection(conversations=[mock_conversation])
    config = WordCloudConfig(max_workers=1)

    generate_wordclouds(collection, tmp_path, config)

    png_files = list(tmp_path.glob("*.png"))
    assert len(png_files) >= 1


def test_wordcloud_week_naming_uses_iso_week(tmp_path: Path) -> None:
    """Ensure weekly filenames use ISO week year/number."""
    ts = datetime(2021, 1, 1, 12, 0, tzinfo=UTC)
    conv = Conversation(
        title="ISO Week",
        create_time=ts,
        update_time=ts,
        mapping={
            "root": {
                "id": "root",
                "message": None,
                "parent": None,
                "children": ["user_node"],
            },
            "user_node": {
                "id": "user_node",
                "message": {
                    "id": "user_node",
                    "author": {"role": "user", "metadata": {}},
                    "create_time": ts.timestamp(),
                    "update_time": ts.timestamp(),
                    "content": {"content_type": "text", "parts": ["hello world"]},
                    "status": "finished_successfully",
                    "end_turn": True,
                    "weight": 1.0,
                    "metadata": {},
                    "recipient": "all",
                },
                "parent": "root",
                "children": [],
            },
        },
        current_node="user_node",
        conversation_id="iso_week_conv",
    )
    collection = ConversationCollection(conversations=[conv])
    config = WordCloudConfig(max_workers=1)

    generate_wordclouds(collection, tmp_path, config)

    assert (tmp_path / "2020-W53.png").exists()


@pytest.mark.parametrize("max_workers", [None, 1, 2, 4])
def test_wordcloud_config_max_workers(max_workers):
    """Test that max_workers config option is accepted."""
    config = WordCloudConfig(max_workers=max_workers)
    assert config.max_workers == max_workers


@pytest.mark.parametrize("random_state", [None, 0, 42, 1337])
def test_wordcloud_config_random_state(random_state):
    """Test that random_state config option is accepted."""
    config = WordCloudConfig(random_state=random_state)
    assert config.random_state == random_state
