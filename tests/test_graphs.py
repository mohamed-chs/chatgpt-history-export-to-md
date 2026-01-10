from matplotlib.figure import Figure

from convoviz.analysis.graphs import (
    generate_activity_heatmap,
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
    output_dir = tmp_path / "graphs"
    generate_graphs(collection, output_dir)
    # Even with no conversations, it shouldn't crash
    assert output_dir.exists()


def test_generate_graphs_writes_summary_images(tmp_path, mock_conversation):
    collection = ConversationCollection(conversations=[mock_conversation])
    output_dir = tmp_path / "graphs"
    generate_graphs(collection, output_dir)

    assert output_dir.exists()
    assert (output_dir / "overview.png").exists()
    assert (output_dir / "activity_heatmap.png").exists()
    assert (output_dir / "monthly_activity.png").exists()
    assert (output_dir / "daily_activity.png").exists()
    assert (output_dir / "model_usage.png").exists()
    assert (output_dir / "conversation_lengths.png").exists()
    assert (output_dir / "conversation_lifetimes.png").exists()
    assert (output_dir / "weekday_pattern.png").exists()
    assert (output_dir / "hourly_pattern.png").exists()


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


def test_generate_activity_heatmap():
    collection = ConversationCollection(conversations=[])
    fig = generate_activity_heatmap(collection)
    assert isinstance(fig, Figure)
