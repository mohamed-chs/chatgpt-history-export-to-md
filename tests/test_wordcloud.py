"""Tests for word cloud generation and stop words."""

from unittest.mock import patch

from convoviz.analysis.wordcloud import (
    generate_wordcloud,
    load_nltk_stopwords,
    parse_custom_stopwords,
)
from convoviz.config import WordCloudConfig


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
def test_generate_wordcloud_stopwords(mock_wc):
    """Test that generate_wordcloud correctly combines stopwords."""
    config = WordCloudConfig(custom_stopwords="python,java", exclude_programming_keywords=True)
    text = "This is a test with def class and int"

    generate_wordcloud(text, config)

    # Check the stopwords passed to WordCloud constructor
    args, kwargs = mock_wc.call_args
    passed_stopwords = kwargs.get("stopwords")

    assert "the" in passed_stopwords  # From NLTK
    assert "python" in passed_stopwords  # From custom
    assert "java" in passed_stopwords  # From custom
    assert "def" in passed_stopwords  # From programming
    assert "class" in passed_stopwords  # From programming


@patch("convoviz.analysis.wordcloud.WordCloud")
def test_generate_wordcloud_no_programming_stopwords(mock_wc):
    """Test that generate_wordcloud respects exclude_programming_keywords=False."""
    config = WordCloudConfig(custom_stopwords="python", exclude_programming_keywords=False)
    text = "This is a test with def class and int"

    generate_wordcloud(text, config)

    args, kwargs = mock_wc.call_args
    passed_stopwords = kwargs.get("stopwords")

    assert "the" in passed_stopwords  # From NLTK
    assert "python" in passed_stopwords  # From custom
    assert "def" not in passed_stopwords  # Should NOT be there
    assert "class" not in passed_stopwords  # Should NOT be there
