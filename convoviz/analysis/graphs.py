"""Graph generation for conversation analytics."""

from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.font_manager as fm
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from tqdm import tqdm

from convoviz.config import GraphConfig, get_default_config
from convoviz.models import ConversationCollection
from convoviz.utils import get_asset_path

WEEKDAYS = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]


def _setup_figure(config: GraphConfig) -> tuple[Figure, Axes, fm.FontProperties]:
    """Internal helper to setup a figure with common styling."""
    fig = Figure(figsize=config.figsize, dpi=config.dpi)
    ax: Axes = fig.add_subplot()

    # Load custom font if possible
    font_path = get_asset_path(f"fonts/{config.font_name}")
    font_prop = (
        fm.FontProperties(fname=str(font_path)) if font_path.exists() else fm.FontProperties()
    )

    # Styling
    fig.set_facecolor("white")
    ax.set_facecolor("white")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    if config.grid:
        ax.grid(axis="y", linestyle="--", alpha=0.7)
    ax.set_axisbelow(True)

    return fig, ax, font_prop


def _ts_to_dt(ts: float, config: GraphConfig) -> datetime:
    """Convert epoch timestamps into aware datetimes based on config."""
    dt_utc = datetime.fromtimestamp(ts, UTC)
    if config.timezone == "utc":
        return dt_utc
    return dt_utc.astimezone()


def _tz_label(config: GraphConfig) -> str:
    return "UTC" if config.timezone == "utc" else "Local"


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
    dates = [_ts_to_dt(ts, cfg) for ts in timestamps]

    weekday_counts: defaultdict[str, int] = defaultdict(int)
    for date in dates:
        weekday_counts[WEEKDAYS[date.weekday()]] += 1

    x = list(range(len(WEEKDAYS)))
    y = [weekday_counts[day] for day in WEEKDAYS]

    fig, ax, font_prop = _setup_figure(cfg)

    bars = ax.bar(x, y, color=cfg.color, alpha=0.85)

    if cfg.show_counts:
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.text(
                    bar.get_x() + bar.get_width() / 2.0,
                    height,
                    f"{int(height)}",
                    ha="center",
                    va="bottom",
                    fontproperties=font_prop,
                )

    ax.set_xlabel("Weekday", fontproperties=font_prop)
    ax.set_ylabel("User Prompt Count", fontproperties=font_prop)
    ax.set_title(title, fontproperties=font_prop, fontsize=16, pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(WEEKDAYS, rotation=45, fontproperties=font_prop)

    for label in ax.get_yticklabels():
        label.set_fontproperties(font_prop)

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
    dates = [_ts_to_dt(ts, cfg) for ts in timestamps]

    hour_counts: dict[int, int] = dict.fromkeys(range(24), 0)
    for date in dates:
        hour_counts[date.hour] += 1

    x = [f"{i:02d}:00" for i in range(24)]
    y = [hour_counts[i] for i in range(24)]

    fig, ax, font_prop = _setup_figure(cfg)

    bars = ax.bar(range(24), y, color=cfg.color, alpha=0.8)

    if cfg.show_counts:
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.text(
                    bar.get_x() + bar.get_width() / 2.0,
                    height,
                    f"{int(height)}",
                    ha="center",
                    va="bottom",
                    fontproperties=font_prop,
                    fontsize=8,
                )

    ax.set_xlabel(f"Hour of Day ({_tz_label(cfg)})", fontproperties=font_prop)
    ax.set_ylabel("User Prompt Count", fontproperties=font_prop)
    ax.set_title(f"{title} - Hourly Distribution", fontproperties=font_prop, fontsize=16, pad=20)
    ax.set_xticks(range(24))
    ax.set_xticklabels(x, rotation=90, fontproperties=font_prop)

    for label in ax.get_yticklabels():
        label.set_fontproperties(font_prop)

    fig.tight_layout()
    return fig


def generate_model_piechart(
    collection: ConversationCollection,
    config: GraphConfig | None = None,
) -> Figure:
    """Create a pie chart showing distribution of models used.

    Groups models with < 5% usage into "Other".

    Args:
        collection: Collection of conversations
        config: Optional graph configuration

    Returns:
        Matplotlib Figure object
    """
    cfg = config or get_default_config().graph
    model_counts: defaultdict[str, int] = defaultdict(int)

    for conv in collection.conversations:
        model = conv.model or "Unknown"
        model_counts[model] += 1

    total = sum(model_counts.values())
    if total == 0:
        # Return empty figure or figure with "No Data"
        fig, ax, font_prop = _setup_figure(cfg)
        ax.text(0.5, 0.5, "No Data", ha="center", va="center", fontproperties=font_prop)
        return fig

    # Group minor models
    threshold = 0.05
    refined_counts: dict[str, int] = {}
    other_count = 0

    for model, count in model_counts.items():
        if count / total < threshold:
            other_count += count
        else:
            refined_counts[model] = count

    if other_count > 0:
        refined_counts["Other"] = other_count

    # Sort for consistent display
    sorted_items = sorted(refined_counts.items(), key=lambda x: x[1], reverse=True)
    labels = [item[0] for item in sorted_items]
    sizes = [item[1] for item in sorted_items]

    fig, ax, font_prop = _setup_figure(cfg)

    colors = [
        "#4A90E2",
        "#50E3C2",
        "#F5A623",
        "#D0021B",
        "#8B572A",
        "#417505",
        "#9013FE",
        "#BD10E0",
        "#7F7F7F",
    ]
    ax.pie(
        sizes,
        labels=labels,
        autopct="%1.1f%%",
        startangle=140,
        colors=colors[: len(labels)],
        textprops={"fontproperties": font_prop},
    )
    ax.set_title("Model Usage Distribution", fontproperties=font_prop, fontsize=16, pad=20)

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

    fig, ax, font_prop = _setup_figure(cfg)

    if not lengths:
        ax.text(0.5, 0.5, "No Data", ha="center", va="center", fontproperties=font_prop)
        return fig

    # Cap at 95th percentile to focus on most conversations
    sorted_lengths = sorted(lengths)
    idx = int(0.95 * (len(sorted_lengths) - 1))
    cap = int(sorted_lengths[idx])
    cap = max(cap, 5)  # Ensure at least some range

    # Filter lengths for the histogram plot, but keep the data correct
    plot_lengths = [min(L, cap) for L in lengths]

    bins = range(0, cap + 2, max(1, cap // 10))
    ax.hist(plot_lengths, bins=bins, color=cfg.color, alpha=0.8, rwidth=0.8)

    ax.set_xlabel("Number of User Prompts", fontproperties=font_prop)
    ax.set_ylabel("Number of Conversations", fontproperties=font_prop)
    ax.set_title(
        f"Conversation Length Distribution (Capped at {cap})",
        fontproperties=font_prop,
        fontsize=16,
        pad=20,
    )

    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontproperties(font_prop)

    fig.tight_layout()
    return fig


def generate_monthly_activity_barplot(
    collection: ConversationCollection,
    config: GraphConfig | None = None,
) -> Figure:
    """Create a bar chart showing total prompt count per month with readable labels.

    Args:
        collection: Collection of conversations
        config: Optional graph configuration

    Returns:
        Matplotlib Figure object
    """
    cfg = config or get_default_config().graph
    month_groups = collection.group_by_month()
    sorted_months = sorted(month_groups.keys())

    # Format labels as "Feb '23"
    x = [m.strftime("%b '%y") for m in sorted_months]
    y = [len(month_groups[m].timestamps("user")) for m in sorted_months]

    fig, ax, font_prop = _setup_figure(cfg)

    positions = list(range(len(x)))
    bars = ax.bar(positions, y, color=cfg.color, alpha=0.85)

    if cfg.show_counts:
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.text(
                    bar.get_x() + bar.get_width() / 2.0,
                    height,
                    f"{int(height)}",
                    ha="center",
                    va="bottom",
                    fontproperties=font_prop,
                    fontsize=8,
                )

    ax.set_xlabel("Month", fontproperties=font_prop)
    ax.set_ylabel("User Prompt Count", fontproperties=font_prop)
    ax.set_title("Monthly Activity History", fontproperties=font_prop, fontsize=16, pad=20)
    tick_step = max(1, len(positions) // 12)  # show ~12 labels max
    shown = positions[::tick_step] if positions else []
    ax.set_xticks(shown)
    ax.set_xticklabels([x[i] for i in shown], rotation=45, fontproperties=font_prop)

    for label in ax.get_yticklabels():
        label.set_fontproperties(font_prop)

    fig.tight_layout()
    return fig


def generate_daily_activity_lineplot(
    collection: ConversationCollection,
    config: GraphConfig | None = None,
) -> Figure:
    """Create a line chart showing user prompt count per day."""
    cfg = config or get_default_config().graph
    timestamps = collection.timestamps("user")

    fig, ax, font_prop = _setup_figure(cfg)
    if not timestamps:
        ax.text(0.5, 0.5, "No Data", ha="center", va="center", fontproperties=font_prop)
        return fig

    counts: defaultdict[datetime, int] = defaultdict(int)
    for ts in timestamps:
        dt = _ts_to_dt(ts, cfg)
        day = dt.replace(hour=0, minute=0, second=0, microsecond=0)
        counts[day] += 1

    days = sorted(counts.keys())
    values = [counts[d] for d in days]

    x = mdates.date2num(days)
    ax.plot(x, values, color=cfg.color, linewidth=2.0)
    ax.fill_between(x, values, color=cfg.color, alpha=0.15)
    locator = mdates.AutoDateLocator()
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(locator))
    ax.set_title("Daily Activity History", fontproperties=font_prop, fontsize=16, pad=20)
    ax.set_xlabel(f"Day ({_tz_label(cfg)})", fontproperties=font_prop)
    ax.set_ylabel("User Prompt Count", fontproperties=font_prop)

    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontproperties(font_prop)

    fig.tight_layout()
    return fig


def generate_summary_graphs(
    collection: ConversationCollection,
    output_dir: Path,
    config: GraphConfig | None = None,
) -> None:
    """Generate all summary-level graphs.

    Args:
        collection: Collection of conversations
        output_dir: Directory to save the graphs
        config: Optional graph configuration
    """
    summary_dir = output_dir / "Summary"
    summary_dir.mkdir(parents=True, exist_ok=True)

    if not collection.conversations:
        return

    # Model usage
    fig_models = generate_model_piechart(collection, config)
    fig_models.savefig(summary_dir / "model_usage.png")

    # Length distribution
    fig_length = generate_length_histogram(collection, config)
    fig_length.savefig(summary_dir / "conversation_lengths.png")

    # Monthly activity
    fig_activity = generate_monthly_activity_barplot(collection, config)
    fig_activity.savefig(summary_dir / "monthly_activity.png")

    # Daily activity
    fig_daily = generate_daily_activity_lineplot(collection, config)
    fig_daily.savefig(summary_dir / "daily_activity.png")


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

    # Summary graphs
    generate_summary_graphs(collection, output_dir, config)

    month_groups = collection.group_by_month()
    year_groups = collection.group_by_year()

    # Month-wise graphs
    for month, group in tqdm(
        month_groups.items(),
        desc="Creating monthly graphs 📈",
        disable=not progress_bar,
    ):
        base_name = month.strftime("%Y %B")
        title = month.strftime("%B '%y")
        timestamps = group.timestamps("user")

        # Weekday distribution
        fig_week = generate_week_barplot(timestamps, title, config)
        fig_week.savefig(output_dir / f"{base_name}_weekly.png")

        # Hourly distribution
        fig_hour = generate_hour_barplot(timestamps, title, config)
        fig_hour.savefig(output_dir / f"{base_name}_hourly.png")

    # Year-wise graphs
    for year, group in tqdm(
        year_groups.items(),
        desc="Creating yearly graphs 📈",
        disable=not progress_bar,
    ):
        base_name = year.strftime("%Y")
        title = year.strftime("%Y")
        timestamps = group.timestamps("user")

        # Weekday distribution
        fig_week = generate_week_barplot(timestamps, title, config)
        fig_week.savefig(output_dir / f"{base_name}_weekly.png")

        # Hourly distribution
        fig_hour = generate_hour_barplot(timestamps, title, config)
        fig_hour.savefig(output_dir / f"{base_name}_hourly.png")
