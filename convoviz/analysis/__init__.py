"""Data analysis and visualization for convoviz.

Requires the [viz] extra: uv tool install "convoviz[viz]"
"""

from typing import Any

__all__ = [
    "generate_week_barplot",
    "generate_wordcloud",
]


def __getattr__(name: str) -> Any:
    """Lazy import for visualization functions requiring optional dependencies."""
    if name == "generate_week_barplot":
        from convoviz.analysis.graphs import generate_week_barplot  # noqa: PLC0415

        return generate_week_barplot
    if name == "generate_wordcloud":
        from convoviz.analysis.wordcloud import generate_wordcloud  # noqa: PLC0415

        return generate_wordcloud
    msg = f"module {__name__!r} has no attribute {name!r}"
    raise AttributeError(msg)
