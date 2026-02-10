"""Time-based activity charts: weekday, hourly, monthly, daily patterns."""

from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING

import matplotlib.dates as mdates

from convoviz.config import get_default_config
from convoviz.utils import WEEKDAYS

if TYPE_CHECKING:
    from datetime import datetime

    from matplotlib.figure import Figure

    from convoviz.config import GraphConfig
    from convoviz.models import ConversationCollection

from .common import (
    aggregate_counts_by_month,
    apply_tick_font,
    fill_missing_months,
    moving_average,
    setup_single_axes,
    ts_to_dt,
    tz_label,
)


def generate_week_barplot(
    timestamps: list[float],
    title: str,
    config: GraphConfig | None = None,
) -> Figure:
    """Create a bar graph showing message distribution across weekdays.

    Args:
        timestamps: List of Unix timestamps
        title: Title for the graph
        config: Optional graph configuration

    Returns:
        Matplotlib Figure object

    """
    cfg = config or get_default_config().graph
    fig, ax, font_prop = setup_single_axes(cfg)

    weekday_counts: dict[str, int] = dict.fromkeys(WEEKDAYS, 0)
    for ts in timestamps:
        dt = ts_to_dt(ts, cfg)
        weekday_counts[WEEKDAYS[dt.weekday()]] += 1

    x = list(range(len(WEEKDAYS)))
    y = [weekday_counts[d] for d in WEEKDAYS]

    bars = ax.bar(x, y, color=cfg.color, alpha=0.9, width=0.72)
    if cfg.show_counts:
        ax.bar_label(
            bars, padding=3, fontsize=9, fontproperties=font_prop, color="#24292f"
        )

    ax.set_title(
        f"{title} · Weekday pattern", fontproperties=font_prop, fontsize=14, pad=14
    )
    ax.set_xlabel("Weekday", fontproperties=font_prop)
    ax.set_ylabel("User prompts", fontproperties=font_prop)
    ax.set_xticks(x)
    ax.set_xticklabels(WEEKDAYS, rotation=35, ha="right", fontproperties=font_prop)
    apply_tick_font(ax, font_prop)

    fig.tight_layout()
    return fig


def generate_hour_barplot(
    timestamps: list[float],
    title: str,
    config: GraphConfig | None = None,
) -> Figure:
    """Create a bar graph showing message distribution across hours of the day (0-23).

    Args:
        timestamps: List of Unix timestamps
        title: Title for the graph
        config: Optional graph configuration

    Returns:
        Matplotlib Figure object

    """
    cfg = config or get_default_config().graph
    fig, ax, font_prop = setup_single_axes(cfg)

    hour_counts: dict[int, int] = dict.fromkeys(range(24), 0)
    for ts in timestamps:
        dt = ts_to_dt(ts, cfg)
        hour_counts[dt.hour] += 1

    y = [hour_counts[i] for i in range(24)]

    bars = ax.bar(range(24), y, color=cfg.color, alpha=0.9, width=0.72)
    if cfg.show_counts:
        ax.bar_label(
            bars, padding=2, fontsize=7, fontproperties=font_prop, color="#24292f"
        )

    ax.set_title(
        f"{title} · Hourly pattern ({tz_label(cfg)})",
        fontproperties=font_prop,
        fontsize=14,
        pad=14,
    )
    ax.set_xlabel(f"Hour of day ({tz_label(cfg)})", fontproperties=font_prop)
    ax.set_ylabel("User prompts", fontproperties=font_prop)

    ax.set_xticks(range(0, 24, 2))
    ax.set_xticklabels(
        [f"{i:02d}:00" for i in range(0, 24, 2)], fontproperties=font_prop
    )
    apply_tick_font(ax, font_prop)

    fig.tight_layout()
    return fig


def generate_monthly_activity_barplot(
    collection: ConversationCollection,
    config: GraphConfig | None = None,
) -> Figure:
    """Create a bar chart showing total prompt count per month.

    Important: this is computed from *message timestamps* (actual activity), not from
    the conversation creation month.
    """
    cfg = config or get_default_config().graph
    timestamps = collection.timestamps("user")
    fig, ax, font_prop = setup_single_axes(cfg)

    if not timestamps:
        ax.text(0.5, 0.5, "No data", ha="center", va="center", fontproperties=font_prop)
        ax.set_axis_off()
        return fig

    month_counts = aggregate_counts_by_month(timestamps, cfg)
    months, values = fill_missing_months(month_counts)
    if not months:
        ax.text(0.5, 0.5, "No data", ha="center", va="center", fontproperties=font_prop)
        ax.set_axis_off()
        return fig

    x = mdates.date2num(months)
    ax.bar(x, values, width=25, color=cfg.color, alpha=0.25, edgecolor="none")

    smooth = moving_average(values, window=3)
    if smooth:
        ax.plot(x[2:], smooth, color=cfg.color, linewidth=2.2, alpha=0.9)

    locator = mdates.AutoDateLocator(minticks=4, maxticks=10)
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(locator))

    ax.set_title(
        "Monthly activity (user prompts)", fontproperties=font_prop, fontsize=14, pad=14
    )
    ax.set_xlabel(f"Month ({tz_label(cfg)})", fontproperties=font_prop)
    ax.set_ylabel("User prompts", fontproperties=font_prop)
    apply_tick_font(ax, font_prop)

    fig.tight_layout()
    return fig


def generate_daily_activity_lineplot(
    collection: ConversationCollection,
    config: GraphConfig | None = None,
) -> Figure:
    """Create a line chart showing user prompt count per day (with a rolling mean)."""
    cfg = config or get_default_config().graph
    timestamps = collection.timestamps("user")

    fig, ax, font_prop = setup_single_axes(cfg)
    if not timestamps:
        ax.text(0.5, 0.5, "No data", ha="center", va="center", fontproperties=font_prop)
        ax.set_axis_off()
        return fig

    counts: defaultdict[datetime, int] = defaultdict(int)
    for ts in timestamps:
        dt = ts_to_dt(ts, cfg)
        day = dt.replace(hour=0, minute=0, second=0, microsecond=0)
        counts[day] += 1

    days = sorted(counts.keys())
    values = [counts[d] for d in days]

    x = mdates.date2num(days)
    ax.bar(x, values, width=0.9, color=cfg.color, alpha=0.18, edgecolor="none")
    ax.plot(x, values, color=cfg.color, linewidth=1.2, alpha=0.25)
    smooth = moving_average(values, window=7)
    if smooth:
        ax.plot(x[6:], smooth, color=cfg.color, linewidth=2.4, alpha=0.95)

    locator = mdates.AutoDateLocator()
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(locator))
    ax.set_title(
        "Daily activity (user prompts)", fontproperties=font_prop, fontsize=14, pad=14
    )
    ax.set_xlabel(f"Day ({tz_label(cfg)})", fontproperties=font_prop)
    ax.set_ylabel("User prompts", fontproperties=font_prop)

    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontproperties(font_prop)

    fig.tight_layout()
    return fig
