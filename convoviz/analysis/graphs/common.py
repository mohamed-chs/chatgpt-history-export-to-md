"""Common utilities and helpers for graph generation.

This module contains shared functions for styling, font loading, time conversions,
and data aggregation used across all graph types.
"""

from __future__ import annotations

import logging
from collections import defaultdict
from datetime import UTC, datetime
from typing import TYPE_CHECKING

import matplotlib.font_manager as fm
import matplotlib.ticker as mticker
from matplotlib.figure import Figure

from convoviz.utils import (
    get_resource_path,
    month_start,
)

if TYPE_CHECKING:
    from collections.abc import Iterable

    from matplotlib.axes import Axes

    from convoviz.config import GraphConfig

logger = logging.getLogger(__name__)


def load_font(config: GraphConfig) -> fm.FontProperties:
    """Load font from config or fall back to system default."""
    font_path = get_resource_path(f"assets/fonts/{config.font_name}")
    return (
        fm.FontProperties(fname=str(font_path))
        if font_path.exists()
        else fm.FontProperties()
    )


def style_axes(ax: Axes, config: GraphConfig) -> None:
    """Apply consistent styling to axes."""
    ax.set_facecolor("white")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#d0d7de")
    ax.spines["bottom"].set_color("#d0d7de")
    ax.tick_params(colors="#24292f")
    ax.yaxis.set_major_locator(mticker.MaxNLocator(nbins=6, integer=True))

    if config.grid:
        ax.grid(axis="y", linestyle="-", linewidth=0.8, alpha=0.35, color="#8c959f")
    ax.set_axisbelow(True)


def apply_tick_font(ax: Axes, font_prop: fm.FontProperties) -> None:
    """Apply font properties to tick labels."""
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontproperties(font_prop)


def setup_single_axes(config: GraphConfig) -> tuple[Figure, Axes, fm.FontProperties]:
    """Create a figure with a single axes, styled and ready to use."""
    fig = Figure(figsize=config.figsize, dpi=config.dpi, facecolor="white")
    ax: Axes = fig.add_subplot()
    font_prop = load_font(config)
    style_axes(ax, config)
    return fig, ax, font_prop


def ts_to_dt(ts: float, config: GraphConfig) -> datetime:
    """Convert epoch timestamp to aware datetime based on config timezone."""
    dt_utc = datetime.fromtimestamp(ts, UTC)
    return dt_utc if config.timezone == "utc" else dt_utc.astimezone()


def tz_label(config: GraphConfig) -> str:
    """Get human-readable timezone label."""
    return "UTC" if config.timezone == "utc" else "Local"


def build_weekday_hour_grid(
    timestamps: Iterable[float], config: GraphConfig
) -> list[list[int]]:
    """Aggregate timestamps into a weekday(0-6) x hour(0-23) activity grid."""
    grid: list[list[int]] = [[0 for _ in range(24)] for _ in range(7)]
    for ts in timestamps:
        dt = ts_to_dt(ts, config)
        grid[dt.weekday()][dt.hour] += 1
    return grid


def fill_missing_months(
    counts: dict[datetime, int],
) -> tuple[list[datetime], list[int]]:
    """Fill in zero counts for missing months in a range."""
    if not counts:
        return [], []
    keys = sorted(counts.keys())
    start = month_start(keys[0])
    end = month_start(keys[-1])
    months: list[datetime] = []
    cur = start
    while cur <= end:
        months.append(cur)
        year, month = cur.year, cur.month
        cur = (
            cur.replace(year=year + 1, month=1)
            if month == 12
            else cur.replace(month=month + 1)
        )
    return months, [counts.get(m, 0) for m in months]


def aggregate_counts_by_month(
    timestamps: Iterable[float],
    config: GraphConfig,
) -> dict[datetime, int]:
    """Aggregate timestamps into monthly counts."""
    counts: defaultdict[datetime, int] = defaultdict(int)
    for ts in timestamps:
        dt = ts_to_dt(ts, config)
        counts[month_start(dt)] += 1
    return dict(counts)


def moving_average(values: list[int], window: int) -> list[float]:
    """Calculate moving average with given window size."""
    if window <= 1:
        return [float(v) for v in values]
    if len(values) < window:
        return []
    out: list[float] = []
    running = sum(values[:window])
    out.append(running / window)
    for i in range(window, len(values)):
        running += values[i] - values[i - window]
        out.append(running / window)
    return out
