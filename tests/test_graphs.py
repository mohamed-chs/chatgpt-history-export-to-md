from matplotlib.figure import Figure

from convoviz.analysis.graphs import (
    generate_graphs,
    generate_hour_barplot,
    generate_length_histogram,
    generate_model_piechart,
    generate_monthly_activity_barplot,
    generate_week_barplot,
)
from convoviz.models import ConversationCollection


def test_generate_week_barplot():
    timestamps = [1736317200.0]  # Jan 8, 2025
    fig = generate_week_barplot(timestamps, "Test Week")
    assert isinstance(fig, Figure)


def test_generate_hour_barplot():
    timestamps = [1736317200.0]  # Jan 8, 2025
    fig = generate_hour_barplot(timestamps, "Test Hour")
    assert isinstance(fig, Figure)


def test_generate_graphs(tmp_path):
    # Minimal collection
    collection = ConversationCollection(conversations=[])
    generate_graphs(collection, tmp_path)
    # Even with no conversations, it shouldn't crash
    assert tmp_path.exists()
    assert (tmp_path / "Summary").exists()


def test_generate_model_piechart():
    collection = ConversationCollection(conversations=[])
    fig = generate_model_piechart(collection)
    assert isinstance(fig, Figure)


def test_generate_length_histogram():
    collection = ConversationCollection(conversations=[])
    fig = generate_length_histogram(collection)
    assert isinstance(fig, Figure)


def test_generate_monthly_activity_barplot():
    collection = ConversationCollection(conversations=[])
    fig = generate_monthly_activity_barplot(collection)
    assert isinstance(fig, Figure)
