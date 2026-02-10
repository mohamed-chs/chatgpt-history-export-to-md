"""Distribution charts: histograms for conversation metrics."""

from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING

from convoviz.config import get_default_config

if TYPE_CHECKING:
    from matplotlib.figure import Figure

    from convoviz.config import GraphConfig
    from convoviz.models import ConversationCollection

from .common import apply_tick_font, setup_single_axes


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
    fig, ax, font_prop = setup_single_axes(cfg)

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

    apply_tick_font(ax, font_prop)
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
    fig, ax, font_prop = setup_single_axes(cfg)

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
        "Conversation length (user prompts)",
        fontproperties=font_prop,
        fontsize=14,
        pad=14,
    )
    ax.set_xlabel("User prompts per conversation", fontproperties=font_prop)
    ax.set_ylabel("Conversations", fontproperties=font_prop)
    ax.set_xlim(left=0, right=cap)
    apply_tick_font(ax, font_prop)

    fig.tight_layout()
    return fig


def generate_conversation_lifetime_histogram(
    collection: ConversationCollection,
    config: GraphConfig | None = None,
) -> Figure:
    """Create a histogram of conversation lifetimes (update_time - create_time)."""
    cfg = config or get_default_config().graph
    fig, ax, font_prop = setup_single_axes(cfg)

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

    ax.set_title(
        "Conversation lifetimes (days)", fontproperties=font_prop, fontsize=14, pad=14
    )
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
    apply_tick_font(ax, font_prop)

    fig.tight_layout()
    return fig
