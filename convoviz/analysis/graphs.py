"""Graph generation for conversation analytics."""

from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path

from matplotlib.figure import Figure
from tqdm import tqdm

from convoviz.config import GraphConfig
from convoviz.models import ConversationCollection

WEEKDAYS = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]


def generate_week_barplot(
    timestamps: list[float],
    title: str,
    _config: GraphConfig | None = None,
) -> Figure:
    """Create a bar graph showing message distribution across weekdays.

    Args:
        timestamps: List of Unix timestamps
        title: Title for the graph
        config: Optional graph configuration (for future extensions)

    Returns:
        Matplotlib Figure object
    """
    dates = [datetime.fromtimestamp(ts, UTC) for ts in timestamps]

    weekday_counts: defaultdict[str, int] = defaultdict(int)
    for date in dates:
        weekday_counts[WEEKDAYS[date.weekday()]] += 1

    x = WEEKDAYS
    y = [weekday_counts[day] for day in WEEKDAYS]

    fig = Figure(dpi=300)
    ax = fig.add_subplot()

    ax.bar(x, y)
    ax.set_xlabel("Weekday")
    ax.set_ylabel("Prompt Count")
    ax.set_title(title)
    ax.set_xticks(range(len(x)))
    ax.set_xticklabels(x, rotation=45)
    fig.tight_layout()

    return fig


def generate_week_barplots(
    collection: ConversationCollection,
    output_dir: Path,
    config: GraphConfig | None = None,
    *,
    progress_bar: bool = False,
) -> None:
    """Generate weekly bar plots for monthly and yearly groupings.

    Args:
        collection: Collection of conversations
        output_dir: Directory to save the graphs
        config: Optional graph configuration
        progress_bar: Whether to show progress bars
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    month_groups = collection.group_by_month()
    year_groups = collection.group_by_year()

    for month, group in tqdm(
        month_groups.items(),
        desc="Creating monthly weekwise graphs 📈",
        disable=not progress_bar,
    ):
        title = month.strftime("%B '%y")
        fig = generate_week_barplot(group.timestamps("user"), title, config)
        fig.savefig(output_dir / f"{month.strftime('%Y %B')}.png")

    for year, group in tqdm(
        year_groups.items(),
        desc="Creating yearly weekwise graphs 📈",
        disable=not progress_bar,
    ):
        title = year.strftime("%Y")
        fig = generate_week_barplot(group.timestamps("user"), title, config)
        fig.savefig(output_dir / f"{year.strftime('%Y')}.png")
