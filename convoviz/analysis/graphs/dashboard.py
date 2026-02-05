"""Dashboard and summary graph generation."""

from __future__ import annotations

import logging
from collections import defaultdict
from collections.abc import Callable
from datetime import datetime
from pathlib import Path

import matplotlib.dates as mdates
from matplotlib.figure import Figure
from tqdm import tqdm

from convoviz.config import GraphConfig, get_default_config
from convoviz.models import ConversationCollection

from .common import (
    WEEKDAYS,
    aggregate_counts_by_month,
    apply_tick_font,
    fill_missing_months,
    load_font,
    month_start,
    moving_average,
    style_axes,
    ts_to_dt,
    tz_label,
    year_start,
)
from .distributions import (
    generate_conversation_lifetime_histogram,
    generate_length_histogram,
    generate_model_piechart,
)
from .heatmaps import generate_activity_heatmap
from .timeseries import (
    generate_daily_activity_lineplot,
    generate_hour_barplot,
    generate_monthly_activity_barplot,
    generate_week_barplot,
)

logger = logging.getLogger(__name__)


def generate_summary_dashboard(
    collection: ConversationCollection,
    config: GraphConfig | None = None,
) -> Figure:
    """Create a compact, high-signal overview dashboard."""
    cfg = config or get_default_config().graph
    font_prop = load_font(cfg)

    fig = Figure(figsize=(14, 9), dpi=cfg.dpi, facecolor="white")
    gs = fig.add_gridspec(3, 2, height_ratios=[1.2, 1.0, 1.0], width_ratios=[1.25, 1.0])

    ax_ts = fig.add_subplot(gs[0, :])
    ax_heat = fig.add_subplot(gs[1:, 0])
    ax_model = fig.add_subplot(gs[1, 1])
    ax_len = fig.add_subplot(gs[2, 1])

    for ax in (ax_ts, ax_model, ax_len):
        style_axes(ax, cfg)
        apply_tick_font(ax, font_prop)

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
        dts = [ts_to_dt(ts, cfg) for ts in user_ts]
        date_range = f"{min(dts).date().isoformat()} → {max(dts).date().isoformat()}"
    else:
        date_range = "No activity"

    fig.text(
        0.01,
        0.955,
        f"{conv_count} conversations · {prompt_count} user prompts · {date_range} · {tz_label(cfg)}",
        fontproperties=font_prop,
        fontsize=10,
        va="top",
        ha="left",
        color="#57606a",
    )

    # Monthly activity (timeseries)
    if user_ts:
        month_counts = aggregate_counts_by_month(user_ts, cfg)
        months, values = fill_missing_months(month_counts)
        x = mdates.date2num(months)
        ax_ts.bar(x, values, width=25, color=cfg.color, alpha=0.20, edgecolor="none")
        smooth = moving_average(values, window=3)
        if smooth:
            ax_ts.plot(x[2:], smooth, color=cfg.color, linewidth=2.6, alpha=0.95)

        locator = mdates.AutoDateLocator(minticks=4, maxticks=10)
        ax_ts.xaxis.set_major_locator(locator)
        ax_ts.xaxis.set_major_formatter(mdates.ConciseDateFormatter(locator))
        ax_ts.set_title(
            "Monthly activity (user prompts)", fontproperties=font_prop, fontsize=13, pad=10
        )
        ax_ts.set_ylabel("User prompts", fontproperties=font_prop)
        ax_ts.set_xlabel(f"Month ({tz_label(cfg)})", fontproperties=font_prop)
        apply_tick_font(ax_ts, font_prop)
    else:
        ax_ts.text(0.5, 0.5, "No data", ha="center", va="center", fontproperties=font_prop)
        ax_ts.set_axis_off()

    # Heatmap
    if user_ts:
        grid: list[list[int]] = [[0 for _ in range(24)] for _ in range(7)]
        for ts in user_ts:
            dt = ts_to_dt(ts, cfg)
            grid[dt.weekday()][dt.hour] += 1

        ax_heat.grid(False)
        for side in ["top", "right", "left", "bottom"]:
            ax_heat.spines[side].set_visible(False)
        img = ax_heat.imshow(grid, aspect="auto", cmap="Blues", interpolation="nearest")
        ax_heat.set_title(
            f"Weekday × hour heatmap ({tz_label(cfg)})",
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

    # Model usage
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
        apply_tick_font(ax_model, font_prop)
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
        apply_tick_font(ax_len, font_prop)
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
            dt = ts_to_dt(ts, cfg)
            month_groups[month_start(dt)].append(ts)

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
            dt = ts_to_dt(ts, cfg)
            year_groups[year_start(dt)].append(ts)

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
