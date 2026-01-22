"""Data analysis and visualization for convoviz.

Requires the [viz] extra: uv tool install "convoviz[viz]"
"""

__all__ = [
    "generate_week_barplot",
    "generate_wordcloud",
]


def __getattr__(name: str):
    """Lazy import for visualization functions requiring optional dependencies."""
    if name == "generate_week_barplot":
        from convoviz.analysis.graphs import generate_week_barplot

        return generate_week_barplot
    if name == "generate_wordcloud":
        from convoviz.analysis.wordcloud import generate_wordcloud

        return generate_wordcloud
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
