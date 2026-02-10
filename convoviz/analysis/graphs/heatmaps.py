"""Heatmap visualizations for activity patterns."""

from __future__ import annotations

from typing import TYPE_CHECKING

from convoviz.config import get_default_config
from convoviz.utils import WEEKDAYS

if TYPE_CHECKING:
    from matplotlib.figure import Figure
    from matplotlib.image import AxesImage

    from convoviz.config import GraphConfig
    from convoviz.models import ConversationCollection

from .common import setup_single_axes, ts_to_dt, tz_label


def generate_activity_heatmap(
    collection: ConversationCollection,
    config: GraphConfig | None = None,
) -> Figure:
    """Create a heatmap of activity by weekday × hour (user prompts)."""  # noqa: RUF002
    cfg = config or get_default_config().graph
    timestamps = collection.timestamps("user")

    fig, ax, font_prop = setup_single_axes(cfg)
    if not timestamps:
        ax.text(0.5, 0.5, "No data", ha="center", va="center", fontproperties=font_prop)
        ax.set_axis_off()
        return fig

    grid: list[list[int]] = [[0 for _ in range(24)] for _ in range(7)]
    for ts in timestamps:
        dt = ts_to_dt(ts, cfg)
        grid[dt.weekday()][dt.hour] += 1

    # Keep the axes frame for the heatmap.
    ax.grid(False)
    for side in ["top", "right", "left", "bottom"]:
        ax.spines[side].set_visible(False)

    img: AxesImage = ax.imshow(
        grid, aspect="auto", cmap="Blues", interpolation="nearest"
    )

    ax.set_title(
        f"Activity heatmap (weekday × hour, {tz_label(cfg)})",  # noqa: RUF001
        fontproperties=font_prop,
        fontsize=14,
        pad=14,
    )
    ax.set_xlabel(f"Hour of day ({tz_label(cfg)})", fontproperties=font_prop)
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
