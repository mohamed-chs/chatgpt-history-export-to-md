"""Graph generation for conversation analytics.

This package provides functions to generate various graphs and visualizations
from conversation data. The functionality is split into focused submodules:

- common: Shared utilities (font loading, styling, time conversions)
- timeseries: Time-based activity charts (weekday, hourly, monthly patterns)
- distributions: Histograms and distribution charts (lengths, models)
- heatmaps: Activity heatmaps
- dashboard: Summary dashboards and orchestration

Usage:
    from convoviz.analysis.graphs import generate_graphs
    generate_graphs(collection, output_dir)
"""

from convoviz.utils import WEEKDAYS

from .dashboard import (
    generate_graphs,
    generate_summary_dashboard,
    generate_summary_graphs,
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

__all__ = [
    "WEEKDAYS",
    "generate_activity_heatmap",
    "generate_conversation_lifetime_histogram",
    "generate_daily_activity_lineplot",
    "generate_graphs",
    "generate_hour_barplot",
    "generate_length_histogram",
    "generate_model_piechart",
    "generate_monthly_activity_barplot",
    "generate_summary_dashboard",
    "generate_summary_graphs",
    "generate_week_barplot",
]
