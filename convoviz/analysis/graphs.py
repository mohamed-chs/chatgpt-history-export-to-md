"""Graph generation for conversation analytics.

Goals:
- Professional, consistent styling across plots.
- High-signal summaries by default (avoid output spam).
- Correct time bucketing (based on *message timestamps*, not conversation creation time).
"""

from __future__ import annotations

import logging
from collections import defaultdict
from collections.abc import Callable, Iterable
from datetime import UTC, datetime
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.font_manager as fm
import matplotlib.ticker as mticker
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.image import AxesImage
from tqdm import tqdm

from convoviz.config import GraphConfig, get_default_config
from convoviz.models import ConversationCollection
from convoviz.utils import get_asset_path

logger = logging.getLogger(__name__)

WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def _load_font(config: GraphConfig) -> fm.FontProperties:
    font_path = get_asset_path(f"fonts/{config.font_name}")
    return fm.FontProperties(fname=str(font_path)) if font_path.exists() else fm.FontProperties()


def _style_axes(ax: Axes, config: GraphConfig) -> None:
    # Clean look
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


def _apply_tick_font(ax: Axes, font_prop: fm.FontProperties) -> None:
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontproperties(font_prop)


def _setup_single_axes(config: GraphConfig) -> tuple[Figure, Axes, fm.FontProperties]:
    fig = Figure(figsize=config.figsize, dpi=config.dpi, facecolor="white")
    ax: Axes = fig.add_subplot()
    font_prop = _load_font(config)
    _style_axes(ax, config)
    return fig, ax, font_prop


def _ts_to_dt(ts: float, config: GraphConfig) -> datetime:
    """Convert epoch timestamps into aware datetimes based on config."""
    dt_utc = datetime.fromtimestamp(ts, UTC)
    return dt_utc if config.timezone == "utc" else dt_utc.astimezone()


def _tz_label(config: GraphConfig) -> str:
    return "UTC" if config.timezone == "utc" else "Local"


def _month_start(dt: datetime) -> datetime:
    return dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def _year_start(dt: datetime) -> datetime:
    return dt.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)


def _day_start(dt: datetime) -> datetime:
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)


def _iter_month_starts(start: datetime, end: datetime) -> list[datetime]:
    start = _month_start(start)
    end = _month_start(end)
    months: list[datetime] = []
    cur = start
    while cur <= end:
        months.append(cur)
        year, month = cur.year, cur.month
        cur = cur.replace(year=year + 1, month=1) if month == 12 else cur.replace(month=month + 1)
    return months


def _fill_missing_months(counts: dict[datetime, int]) -> tuple[list[datetime], list[int]]:
    if not counts:
        return [], []
    keys = sorted(counts.keys())
    months = _iter_month_starts(keys[0], keys[-1])
    return months, [counts.get(m, 0) for m in months]


def _aggregate_counts_by_month(
    timestamps: Iterable[float],
    config: GraphConfig,
) -> dict[datetime, int]:
    counts: defaultdict[datetime, int] = defaultdict(int)
    for ts in timestamps:
        dt = _ts_to_dt(ts, config)
        counts[_month_start(dt)] += 1
    return dict(counts)


def _moving_average(values: list[int], window: int) -> list[float]:
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
    fig, ax, font_prop = _setup_single_axes(cfg)

    weekday_counts: dict[str, int] = dict.fromkeys(WEEKDAYS, 0)
    for ts in timestamps:
        dt = _ts_to_dt(ts, cfg)
        weekday_counts[WEEKDAYS[dt.weekday()]] += 1

    x = list(range(len(WEEKDAYS)))
    y = [weekday_counts[d] for d in WEEKDAYS]

    bars = ax.bar(x, y, color=cfg.color, alpha=0.9, width=0.72)
    if cfg.show_counts:
        ax.bar_label(bars, padding=3, fontsize=9, fontproperties=font_prop, color="#24292f")

    ax.set_title(f"{title} · Weekday pattern", fontproperties=font_prop, fontsize=14, pad=14)
    ax.set_xlabel("Weekday", fontproperties=font_prop)
    ax.set_ylabel("User prompts", fontproperties=font_prop)
    ax.set_xticks(x)
    ax.set_xticklabels(WEEKDAYS, rotation=35, ha="right", fontproperties=font_prop)
    _apply_tick_font(ax, font_prop)

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
    fig, ax, font_prop = _setup_single_axes(cfg)

    hour_counts: dict[int, int] = dict.fromkeys(range(24), 0)
    for ts in timestamps:
        dt = _ts_to_dt(ts, cfg)
        hour_counts[dt.hour] += 1

    y = [hour_counts[i] for i in range(24)]

    bars = ax.bar(range(24), y, color=cfg.color, alpha=0.9, width=0.72)
    if cfg.show_counts:
        ax.bar_label(bars, padding=2, fontsize=7, fontproperties=font_prop, color="#24292f")

    ax.set_title(
        f"{title} · Hourly pattern ({_tz_label(cfg)})",
        fontproperties=font_prop,
        fontsize=14,
        pad=14,
    )
    ax.set_xlabel(f"Hour of day ({_tz_label(cfg)})", fontproperties=font_prop)
    ax.set_ylabel("User prompts", fontproperties=font_prop)

    ax.set_xticks(range(0, 24, 2))
    ax.set_xticklabels([f"{i:02d}:00" for i in range(0, 24, 2)], fontproperties=font_prop)
    _apply_tick_font(ax, font_prop)

    fig.tight_layout()
    return fig


def generate_model_piechart(
    collection: ConversationCollection,
    config: GraphConfig | None = None,
) -> Figure:
    """Create a model usage chart.

    Note: kept for backwards compatibility (historically a pie chart). We now render a
    more readable horizontal bar chart with percentages.
    """
    cfg = config or get_default_config().graph
    model_counts: defaultdict[str, int] = defaultdict(int)

    for conv in collection.conversations:
        model = conv.model or "Unknown"
        model_counts[model] += 1

    total = sum(model_counts.values())
    fig, ax, font_prop = _setup_single_axes(cfg)

    if total == 0:
        ax.text(0.5, 0.5, "No data", ha="center", va="center", fontproperties=font_prop)
        ax.set_axis_off()
        return fig

    # Group minor models to keep the plot readable.
    threshold = 0.05
    refined_counts: dict[str, int] = {}
    other_count = 0
    for model, count in model_counts.items():
        if count / total < threshold:
            other_count += count
        else:
            refined_counts[model] = count
    if other_count:
        refined_counts["Other"] = other_count

    items = sorted(refined_counts.items(), key=lambda x: x[1], reverse=True)
    labels = [k for k, _ in items][:10]
    counts = [v for _, v in items][:10]
    y = list(range(len(labels)))[::-1]

    bars = ax.barh(y, counts[::-1], color=cfg.color, alpha=0.9, height=0.6)
    ax.set_yticks(y)
    ax.set_yticklabels(labels[::-1], fontproperties=font_prop)
    ax.set_xlabel("Conversations", fontproperties=font_prop)
    ax.set_title("Model usage", fontproperties=font_prop, fontsize=14, pad=14)

    for bar, count in zip(bars, counts[::-1], strict=True):
        pct = 100 * (count / total)
        ax.text(
            bar.get_width(),
            bar.get_y() + bar.get_height() / 2,
            f"  {count}  ({pct:.1f}%)",
            va="center",
            ha="left",
            fontproperties=font_prop,
            fontsize=9,
            color="#24292f",
        )

    _apply_tick_font(ax, font_prop)
    fig.tight_layout()
    return fig


def generate_length_histogram(
    collection: ConversationCollection,
    config: GraphConfig | None = None,
) -> Figure:
    """Create a histogram showing distribution of conversation lengths.

    Caps the X-axis at the 95th percentile to focus on typical lengths.

    Args:
        collection: Collection of conversations
        config: Optional graph configuration

    Returns:
        Matplotlib Figure object
    """
    cfg = config or get_default_config().graph
    lengths = [conv.message_count("user") for conv in collection.conversations]
    fig, ax, font_prop = _setup_single_axes(cfg)

    if not lengths:
        ax.text(0.5, 0.5, "No data", ha="center", va="center", fontproperties=font_prop)
        ax.set_axis_off()
        return fig

    sorted_lengths = sorted(lengths)
    p50 = sorted_lengths[int(0.50 * (len(sorted_lengths) - 1))]
    p90 = sorted_lengths[int(0.90 * (len(sorted_lengths) - 1))]
    p95 = sorted_lengths[int(0.95 * (len(sorted_lengths) - 1))]
    cap = max(int(p95), 5)
    plot_lengths = [min(L, cap) for L in lengths]

    bin_count = min(24, max(10, cap // 2))
    ax.hist(
        plot_lengths,
        bins=bin_count,
        color=cfg.color,
        alpha=0.85,
        rwidth=0.9,
        edgecolor="white",
        linewidth=0.5,
    )

    ax.axvline(p50, color="#24292f", linewidth=1.2, alpha=0.8)
    ax.axvline(p90, color="#cf222e", linewidth=1.2, alpha=0.8)
    ax.text(
        p50,
        ax.get_ylim()[1] * 0.95,
        f"median={p50}",
        rotation=90,
        va="top",
        ha="right",
        fontproperties=font_prop,
        fontsize=9,
        color="#24292f",
    )
    ax.text(
        p90,
        ax.get_ylim()[1] * 0.95,
        f"p90={p90}",
        rotation=90,
        va="top",
        ha="right",
        fontproperties=font_prop,
        fontsize=9,
        color="#cf222e",
    )

    ax.set_title(
        "Conversation length (user prompts)", fontproperties=font_prop, fontsize=14, pad=14
    )
    ax.set_xlabel("User prompts per conversation", fontproperties=font_prop)
    ax.set_ylabel("Conversations", fontproperties=font_prop)
    ax.set_xlim(left=0, right=cap)
    _apply_tick_font(ax, font_prop)

    fig.tight_layout()
    return fig


def generate_conversation_lifetime_histogram(
    collection: ConversationCollection,
    config: GraphConfig | None = None,
) -> Figure:
    """Create a histogram of conversation lifetimes (update_time - create_time)."""
    cfg = config or get_default_config().graph
    fig, ax, font_prop = _setup_single_axes(cfg)

    lifetimes_days: list[float] = []
    for conv in collection.conversations:
        delta = conv.update_time - conv.create_time
        lifetimes_days.append(max(0.0, delta.total_seconds() / 86_400))

    if not lifetimes_days:
        ax.text(0.5, 0.5, "No data", ha="center", va="center", fontproperties=font_prop)
        ax.set_axis_off()
        return fig

    sorted_vals = sorted(lifetimes_days)
    p50 = sorted_vals[int(0.50 * (len(sorted_vals) - 1))]
    p90 = sorted_vals[int(0.90 * (len(sorted_vals) - 1))]
    p95 = sorted_vals[int(0.95 * (len(sorted_vals) - 1))]
    cap = max(float(p95), 1.0)
    plot_vals = [min(v, cap) for v in lifetimes_days]

    ax.hist(
        plot_vals,
        bins=24,
        color=cfg.color,
        alpha=0.85,
        rwidth=0.9,
        edgecolor="white",
        linewidth=0.5,
    )
    ax.axvline(p50, color="#24292f", linewidth=1.2, alpha=0.8)
    ax.axvline(p90, color="#cf222e", linewidth=1.2, alpha=0.8)

    ax.set_title("Conversation lifetimes (days)", fontproperties=font_prop, fontsize=14, pad=14)
    ax.set_xlabel("Days between first and last message", fontproperties=font_prop)
    ax.set_ylabel("Conversations", fontproperties=font_prop)
    ax.set_xlim(left=0, right=cap)
    ax.text(
        0.99,
        0.98,
        f"median={p50:.1f}d\np90={p90:.1f}d",
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontproperties=font_prop,
        fontsize=9,
        color="#57606a",
    )
    _apply_tick_font(ax, font_prop)

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
    fig, ax, font_prop = _setup_single_axes(cfg)

    if not timestamps:
        ax.text(0.5, 0.5, "No data", ha="center", va="center", fontproperties=font_prop)
        ax.set_axis_off()
        return fig

    month_counts = _aggregate_counts_by_month(timestamps, cfg)
    months, values = _fill_missing_months(month_counts)
    if not months:
        ax.text(0.5, 0.5, "No data", ha="center", va="center", fontproperties=font_prop)
        ax.set_axis_off()
        return fig

    x = mdates.date2num(months)
    ax.bar(x, values, width=25, color=cfg.color, alpha=0.25, edgecolor="none")

    smooth = _moving_average(values, window=3)
    if smooth:
        ax.plot(x[2:], smooth, color=cfg.color, linewidth=2.2, alpha=0.9)

    locator = mdates.AutoDateLocator(minticks=4, maxticks=10)
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(locator))

    ax.set_title("Monthly activity (user prompts)", fontproperties=font_prop, fontsize=14, pad=14)
    ax.set_xlabel(f"Month ({_tz_label(cfg)})", fontproperties=font_prop)
    ax.set_ylabel("User prompts", fontproperties=font_prop)
    _apply_tick_font(ax, font_prop)

    fig.tight_layout()
    return fig


def generate_daily_activity_lineplot(
    collection: ConversationCollection,
    config: GraphConfig | None = None,
) -> Figure:
    """Create a line chart showing user prompt count per day (with a rolling mean)."""
    cfg = config or get_default_config().graph
    timestamps = collection.timestamps("user")

    fig, ax, font_prop = _setup_single_axes(cfg)
    if not timestamps:
        ax.text(0.5, 0.5, "No data", ha="center", va="center", fontproperties=font_prop)
        ax.set_axis_off()
        return fig

    counts: defaultdict[datetime, int] = defaultdict(int)
    for ts in timestamps:
        dt = _ts_to_dt(ts, cfg)
        day = dt.replace(hour=0, minute=0, second=0, microsecond=0)
        counts[day] += 1

    days = sorted(counts.keys())
    values = [counts[d] for d in days]

    x = mdates.date2num(days)
    ax.bar(x, values, width=0.9, color=cfg.color, alpha=0.18, edgecolor="none")
    ax.plot(x, values, color=cfg.color, linewidth=1.2, alpha=0.25)
    smooth = _moving_average(values, window=7)
    if smooth:
        ax.plot(x[6:], smooth, color=cfg.color, linewidth=2.4, alpha=0.95)

    locator = mdates.AutoDateLocator()
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(locator))
    ax.set_title("Daily activity (user prompts)", fontproperties=font_prop, fontsize=14, pad=14)
    ax.set_xlabel(f"Day ({_tz_label(cfg)})", fontproperties=font_prop)
    ax.set_ylabel("User prompts", fontproperties=font_prop)

    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontproperties(font_prop)

    fig.tight_layout()
    return fig


def generate_activity_heatmap(
    collection: ConversationCollection,
    config: GraphConfig | None = None,
) -> Figure:
    """Create a heatmap of activity by weekday × hour (user prompts)."""
    cfg = config or get_default_config().graph
    timestamps = collection.timestamps("user")

    fig, ax, font_prop = _setup_single_axes(cfg)
    if not timestamps:
        ax.text(0.5, 0.5, "No data", ha="center", va="center", fontproperties=font_prop)
        ax.set_axis_off()
        return fig

    grid: list[list[int]] = [[0 for _ in range(24)] for _ in range(7)]
    for ts in timestamps:
        dt = _ts_to_dt(ts, cfg)
        grid[dt.weekday()][dt.hour] += 1

    # Keep the axes frame for the heatmap.
    ax.grid(False)
    for side in ["top", "right", "left", "bottom"]:
        ax.spines[side].set_visible(False)

    img: AxesImage = ax.imshow(grid, aspect="auto", cmap="Blues", interpolation="nearest")

    ax.set_title(
        f"Activity heatmap (weekday × hour, {_tz_label(cfg)})",
        fontproperties=font_prop,
        fontsize=14,
        pad=14,
    )
    ax.set_xlabel(f"Hour of day ({_tz_label(cfg)})", fontproperties=font_prop)
    ax.set_ylabel("Weekday", fontproperties=font_prop)

    ax.set_xticks(list(range(0, 24, 2)))
    ax.set_xticklabels([f"{h:02d}" for h in range(0, 24, 2)], fontproperties=font_prop)
    ax.set_yticks(list(range(7)))
    ax.set_yticklabels(WEEKDAYS, fontproperties=font_prop)

    cbar = fig.colorbar(img, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("User prompts", fontproperties=font_prop)
    for t in cbar.ax.get_yticklabels():
        t.set_fontproperties(font_prop)

    fig.tight_layout()
    return fig


def generate_summary_dashboard(
    collection: ConversationCollection,
    config: GraphConfig | None = None,
) -> Figure:
    """Create a compact, high-signal overview dashboard."""
    cfg = config or get_default_config().graph
    font_prop = _load_font(cfg)

    fig = Figure(figsize=(14, 9), dpi=cfg.dpi, facecolor="white")
    gs = fig.add_gridspec(3, 2, height_ratios=[1.2, 1.0, 1.0], width_ratios=[1.25, 1.0])

    ax_ts: Axes = fig.add_subplot(gs[0, :])
    ax_heat: Axes = fig.add_subplot(gs[1:, 0])
    ax_model: Axes = fig.add_subplot(gs[1, 1])
    ax_len: Axes = fig.add_subplot(gs[2, 1])

    for ax in (ax_ts, ax_model, ax_len):
        _style_axes(ax, cfg)
        _apply_tick_font(ax, font_prop)

    # Header
    user_ts = collection.timestamps("user")
    conv_count = len(collection.conversations)
    prompt_count = len(user_ts)

    fig.text(
        0.01,
        0.985,
        "ChatGPT usage overview",
        fontproperties=font_prop,
        fontsize=18,
        va="top",
        ha="left",
        color="#24292f",
    )

    if user_ts:
        dts = [_ts_to_dt(ts, cfg) for ts in user_ts]
        date_range = f"{min(dts).date().isoformat()} → {max(dts).date().isoformat()}"
    else:
        date_range = "No activity"

    fig.text(
        0.01,
        0.955,
        f"{conv_count} conversations · {prompt_count} user prompts · {date_range} · {_tz_label(cfg)}",
        fontproperties=font_prop,
        fontsize=10,
        va="top",
        ha="left",
        color="#57606a",
    )

    # Monthly activity (timeseries)
    if user_ts:
        month_counts = _aggregate_counts_by_month(user_ts, cfg)
        months, values = _fill_missing_months(month_counts)
        x = mdates.date2num(months)
        ax_ts.bar(x, values, width=25, color=cfg.color, alpha=0.20, edgecolor="none")
        smooth = _moving_average(values, window=3)
        if smooth:
            ax_ts.plot(x[2:], smooth, color=cfg.color, linewidth=2.6, alpha=0.95)

        locator = mdates.AutoDateLocator(minticks=4, maxticks=10)
        ax_ts.xaxis.set_major_locator(locator)
        ax_ts.xaxis.set_major_formatter(mdates.ConciseDateFormatter(locator))
        ax_ts.set_title(
            "Monthly activity (user prompts)", fontproperties=font_prop, fontsize=13, pad=10
        )
        ax_ts.set_ylabel("User prompts", fontproperties=font_prop)
        ax_ts.set_xlabel(f"Month ({_tz_label(cfg)})", fontproperties=font_prop)
        _apply_tick_font(ax_ts, font_prop)
    else:
        ax_ts.text(0.5, 0.5, "No data", ha="center", va="center", fontproperties=font_prop)
        ax_ts.set_axis_off()

    # Heatmap
    if user_ts:
        grid: list[list[int]] = [[0 for _ in range(24)] for _ in range(7)]
        for ts in user_ts:
            dt = _ts_to_dt(ts, cfg)
            grid[dt.weekday()][dt.hour] += 1

        ax_heat.grid(False)
        for side in ["top", "right", "left", "bottom"]:
            ax_heat.spines[side].set_visible(False)
        img = ax_heat.imshow(grid, aspect="auto", cmap="Blues", interpolation="nearest")
        ax_heat.set_title(
            f"Weekday × hour heatmap ({_tz_label(cfg)})",
            fontproperties=font_prop,
            fontsize=13,
            pad=10,
        )
        ax_heat.set_xlabel("Hour", fontproperties=font_prop)
        ax_heat.set_ylabel("Weekday", fontproperties=font_prop)
        ax_heat.set_xticks(list(range(0, 24, 3)))
        ax_heat.set_xticklabels([f"{h:02d}" for h in range(0, 24, 3)], fontproperties=font_prop)
        ax_heat.set_yticks(list(range(7)))
        ax_heat.set_yticklabels(WEEKDAYS, fontproperties=font_prop)
        cbar = fig.colorbar(img, ax=ax_heat, fraction=0.046, pad=0.04)
        cbar.set_label("Prompts", fontproperties=font_prop)
        for t in cbar.ax.get_yticklabels():
            t.set_fontproperties(font_prop)
    else:
        ax_heat.text(0.5, 0.5, "No data", ha="center", va="center", fontproperties=font_prop)
        ax_heat.set_axis_off()

    # Model usage (reuse existing generator logic by drawing into its own axes)
    model_counts: defaultdict[str, int] = defaultdict(int)
    for conv in collection.conversations:
        model_counts[conv.model or "Unknown"] += 1
    total_models = sum(model_counts.values())
    if total_models:
        items = sorted(model_counts.items(), key=lambda x: x[1], reverse=True)
        labels = [k for k, _ in items][:8]
        counts = [v for _, v in items][:8]
        y = list(range(len(labels)))[::-1]
        bars = ax_model.barh(y, counts[::-1], color=cfg.color, alpha=0.9, height=0.6)
        ax_model.set_yticks(y)
        ax_model.set_yticklabels(labels[::-1], fontproperties=font_prop)
        ax_model.set_xlabel("Conversations", fontproperties=font_prop)
        ax_model.set_title("Models", fontproperties=font_prop, fontsize=13, pad=10)
        for bar, count in zip(bars, counts[::-1], strict=True):
            pct = 100 * (count / total_models)
            ax_model.text(
                bar.get_width(),
                bar.get_y() + bar.get_height() / 2,
                f"  {pct:.0f}%",
                va="center",
                ha="left",
                fontproperties=font_prop,
                fontsize=9,
                color="#57606a",
            )
        _apply_tick_font(ax_model, font_prop)
    else:
        ax_model.text(0.5, 0.5, "No data", ha="center", va="center", fontproperties=font_prop)
        ax_model.set_axis_off()

    # Conversation length mini-hist
    lengths = [conv.message_count("user") for conv in collection.conversations]
    if lengths:
        sorted_lengths = sorted(lengths)
        cap = max(int(sorted_lengths[int(0.95 * (len(sorted_lengths) - 1))]), 5)
        plot_lengths = [min(L, cap) for L in lengths]
        ax_len.hist(
            plot_lengths,
            bins=min(16, max(8, cap // 2)),
            color=cfg.color,
            alpha=0.85,
            rwidth=0.9,
            edgecolor="white",
            linewidth=0.5,
        )
        ax_len.set_title("Conversation length", fontproperties=font_prop, fontsize=13, pad=10)
        ax_len.set_xlabel("User prompts", fontproperties=font_prop)
        ax_len.set_ylabel("Conversations", fontproperties=font_prop)
        ax_len.set_xlim(left=0, right=cap)
        _apply_tick_font(ax_len, font_prop)
    else:
        ax_len.text(0.5, 0.5, "No data", ha="center", va="center", fontproperties=font_prop)
        ax_len.set_axis_off()

    fig.subplots_adjust(top=0.93, left=0.06, right=0.98, bottom=0.06, hspace=0.4, wspace=0.25)
    return fig


def generate_summary_graphs(
    collection: ConversationCollection,
    output_dir: Path,
    config: GraphConfig | None = None,
    *,
    progress_bar: bool = False,
) -> None:
    """Generate all summary-level graphs.

    Args:
        collection: Collection of conversations
        output_dir: Directory to save the graphs
        config: Optional graph configuration
    """
    if not collection.conversations:
        return

    cfg = config or get_default_config().graph

    user_ts = collection.timestamps("user")
    logger.info(f"Generating summary graphs to {output_dir}")

    tasks: list[tuple[str, str, Callable[[], Figure]]] = [
        ("Overview", "overview.png", lambda: generate_summary_dashboard(collection, cfg)),
        (
            "Activity heatmap",
            "activity_heatmap.png",
            lambda: generate_activity_heatmap(collection, cfg),
        ),
        (
            "Daily activity",
            "daily_activity.png",
            lambda: generate_daily_activity_lineplot(collection, cfg),
        ),
        (
            "Monthly activity",
            "monthly_activity.png",
            lambda: generate_monthly_activity_barplot(collection, cfg),
        ),
        ("Model usage", "model_usage.png", lambda: generate_model_piechart(collection, cfg)),
        (
            "Conversation lengths",
            "conversation_lengths.png",
            lambda: generate_length_histogram(collection, cfg),
        ),
        (
            "Conversation lifetimes",
            "conversation_lifetimes.png",
            lambda: generate_conversation_lifetime_histogram(collection, cfg),
        ),
    ]

    if user_ts:
        tasks.extend(
            [
                (
                    "Weekday pattern",
                    "weekday_pattern.png",
                    lambda: generate_week_barplot(user_ts, "All time", cfg),
                ),
                (
                    "Hourly pattern",
                    "hourly_pattern.png",
                    lambda: generate_hour_barplot(user_ts, "All time", cfg),
                ),
            ]
        )

    for _, filename, build in tqdm(
        tasks,
        desc="Creating summary graphs",
        disable=not progress_bar,
    ):
        fig = build()
        fig.savefig(output_dir / filename, facecolor="white")


def generate_graphs(
    collection: ConversationCollection,
    output_dir: Path,
    config: GraphConfig | None = None,
    *,
    progress_bar: bool = False,
) -> None:
    """Generate weekly, hourly, and summary graphs.

    Args:
        collection: Collection of conversations
        output_dir: Directory to save the graphs
        config: Optional graph configuration
        progress_bar: Whether to show progress bars
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    cfg = config or get_default_config().graph

    # Summary graphs (default: small, high-signal set)
    generate_summary_graphs(collection, output_dir, cfg, progress_bar=progress_bar)

    # Optional breakdowns (can generate lots of files; off by default)
    if not collection.conversations:
        return

    timestamps = collection.timestamps("user")
    if not timestamps:
        return

    breakdown_root = output_dir / "Breakdowns"
    if cfg.generate_monthly_breakdowns:
        monthly_dir = breakdown_root / "Monthly"
        monthly_dir.mkdir(parents=True, exist_ok=True)

        month_groups: defaultdict[datetime, list[float]] = defaultdict(list)
        for ts in timestamps:
            dt = _ts_to_dt(ts, cfg)
            month_groups[_month_start(dt)].append(ts)

        for month, ts_list in tqdm(
            sorted(month_groups.items(), key=lambda x: x[0]),
            desc="Creating monthly breakdown graphs",
            disable=not progress_bar,
        ):
            slug = month.strftime("%Y-%m")
            title = month.strftime("%b %Y")
            generate_week_barplot(ts_list, title, cfg).savefig(
                monthly_dir / f"{slug}_weekday.png", facecolor="white"
            )
            generate_hour_barplot(ts_list, title, cfg).savefig(
                monthly_dir / f"{slug}_hourly.png", facecolor="white"
            )

    if cfg.generate_yearly_breakdowns:
        yearly_dir = breakdown_root / "Yearly"
        yearly_dir.mkdir(parents=True, exist_ok=True)

        year_groups: defaultdict[datetime, list[float]] = defaultdict(list)
        for ts in timestamps:
            dt = _ts_to_dt(ts, cfg)
            year_groups[_year_start(dt)].append(ts)

        for year, ts_list in tqdm(
            sorted(year_groups.items(), key=lambda x: x[0]),
            desc="Creating yearly breakdown graphs",
            disable=not progress_bar,
        ):
            slug = year.strftime("%Y")
            title = year.strftime("%Y")
            generate_week_barplot(ts_list, title, cfg).savefig(
                yearly_dir / f"{slug}_weekday.png", facecolor="white"
            )
            generate_hour_barplot(ts_list, title, cfg).savefig(
                yearly_dir / f"{slug}_hourly.png", facecolor="white"
            )
