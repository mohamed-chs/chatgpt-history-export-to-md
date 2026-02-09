"""Tests for interactive prompts."""

from __future__ import annotations

from pathlib import Path

import pytest

from convoviz.config import OutputKind, get_default_config
from convoviz.interactive import run_interactive_config


class FakePrompt[T]:
    """Minimal stand-in for a questionary prompt object."""

    def __init__(self, result: T | None) -> None:
        self._result = result

    def ask(self) -> T | None:
        return self._result


def test_ctrl_c_on_first_prompt_aborts_interactive(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import convoviz.interactive as interactive

    monkeypatch.setattr(interactive, "find_latest_valid_zip", lambda: None)
    monkeypatch.setattr(interactive, "find_script_export", lambda: None)
    monkeypatch.setattr(interactive, "qst_path", lambda *_a, **_k: FakePrompt(None))

    with pytest.raises(KeyboardInterrupt):
        run_interactive_config(get_default_config())


def test_ctrl_c_mid_flow_aborts_interactive(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    import convoviz.interactive as interactive

    monkeypatch.setattr(interactive, "find_latest_valid_zip", lambda: None)
    monkeypatch.setattr(interactive, "find_script_export", lambda: None)

    path_answers = iter(["dummy.zip", str(tmp_path / "out")])

    def fake_qst_path(*_a, **_k):
        return FakePrompt(next(path_answers))

    monkeypatch.setattr(interactive, "qst_path", fake_qst_path)
    # Ctrl+C on the output selection checkbox (which comes after the two path prompts)
    monkeypatch.setattr(interactive, "checkbox", lambda *_a, **_k: FakePrompt(None))

    with pytest.raises(KeyboardInterrupt):
        run_interactive_config(get_default_config())


def test_ctrl_c_on_outputs_checkbox_aborts_interactive(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Test Ctrl+C on the outputs checkbox prompt aborts."""
    import convoviz.interactive as interactive

    monkeypatch.setattr(interactive, "find_latest_valid_zip", lambda: None)
    monkeypatch.setattr(interactive, "find_script_export", lambda: None)

    path_answers = iter(["dummy.zip", str(tmp_path / "out")])

    def fake_qst_path(*_a, **_k):
        return FakePrompt(next(path_answers))

    monkeypatch.setattr(interactive, "qst_path", fake_qst_path)
    monkeypatch.setattr(interactive, "checkbox", lambda *_a, **_k: FakePrompt(None))

    with pytest.raises(KeyboardInterrupt):
        run_interactive_config(get_default_config())


def test_outputs_selection_sets_config(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Test that output selection correctly sets config.outputs."""
    import convoviz.interactive as interactive

    monkeypatch.setattr(interactive, "find_latest_valid_zip", lambda: None)
    monkeypatch.setattr(interactive, "find_script_export", lambda: None)

    path_answers = iter(["dummy.zip", str(tmp_path / "out")])

    def fake_qst_path(*_a, **_k):
        return FakePrompt(next(path_answers))

    checkbox_call_count = [0]

    def fake_checkbox(*_a, **_k):
        checkbox_call_count[0] += 1
        if checkbox_call_count[0] == 1:
            # First checkbox is the outputs selection - only select markdown
            return FakePrompt([OutputKind.MARKDOWN])
        if checkbox_call_count[0] == 2:
            # Second checkbox is extras
            return FakePrompt(["canvas", "custom_instructions"])
        # Third checkbox is YAML fields
        return FakePrompt(["title", "chat_link"])

    monkeypatch.setattr(interactive, "qst_path", fake_qst_path)
    monkeypatch.setattr(interactive, "checkbox", fake_checkbox)
    monkeypatch.setattr(interactive, "qst_text", lambda *_a, **_k: FakePrompt("# Me"))
    monkeypatch.setattr(interactive, "select", lambda *_a, **_k: FakePrompt("standard"))
    monkeypatch.setattr(interactive, "confirm", lambda *_a, **_k: FakePrompt(True))

    config = run_interactive_config(get_default_config())

    # Should have only markdown selected
    assert config.outputs == {OutputKind.MARKDOWN}


def test_wordcloud_prompts_skipped_when_not_selected(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Test that wordcloud prompts are skipped when wordclouds output is not selected."""
    import convoviz.interactive as interactive

    monkeypatch.setattr(interactive, "find_latest_valid_zip", lambda: None)
    monkeypatch.setattr(interactive, "find_script_export", lambda: None)
    monkeypatch.setattr(interactive, "font_names", lambda: ["Font1", "Font2"])
    monkeypatch.setattr(interactive, "colormaps", lambda: ["cmap1", "cmap2"])

    path_answers = iter(["dummy.zip", str(tmp_path / "out")])

    def fake_qst_path(*_a, **_k):
        return FakePrompt(next(path_answers))

    checkbox_call_count = [0]

    def fake_checkbox(*_a, **_k):
        checkbox_call_count[0] += 1
        if checkbox_call_count[0] == 1:
            # First checkbox: select only markdown (no wordclouds)
            return FakePrompt([OutputKind.MARKDOWN])
        if checkbox_call_count[0] == 2:
            # Second checkbox: extras
            return FakePrompt(["canvas", "custom_instructions"])
        # Third checkbox: YAML fields
        return FakePrompt(["title"])

    select_call_count = [0]

    def fake_select(*_a, **_k):
        select_call_count[0] += 1
        # Only one select call expected (markdown flavor), not font/colormap
        return FakePrompt("standard")

    text_call_count = [0]

    def fake_text(*_a, **_k):
        text_call_count[0] += 1
        return FakePrompt("# Me")

    monkeypatch.setattr(interactive, "qst_path", fake_qst_path)
    monkeypatch.setattr(interactive, "checkbox", fake_checkbox)
    monkeypatch.setattr(interactive, "select", fake_select)
    monkeypatch.setattr(interactive, "qst_text", fake_text)
    monkeypatch.setattr(interactive, "confirm", lambda *_a, **_k: FakePrompt(True))

    run_interactive_config(get_default_config())

    # Only 2 select calls (markdown flavor + render order), not 4 (add font/colormap)
    assert select_call_count[0] == 2
    # Only 2 text calls (user header + assistant header), not 3 (+ stopwords)
    assert text_call_count[0] == 2


def test_markdown_prompts_skipped_when_not_selected(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Test that markdown prompts are skipped when markdown output is not selected."""
    import convoviz.interactive as interactive

    monkeypatch.setattr(interactive, "find_latest_valid_zip", lambda: None)
    monkeypatch.setattr(interactive, "find_script_export", lambda: None)
    monkeypatch.setattr(interactive, "font_names", lambda: ["Font1", "Font2"])
    monkeypatch.setattr(interactive, "colormaps", lambda: ["cmap1", "cmap2"])

    path_answers = iter(["dummy.zip", str(tmp_path / "out")])

    def fake_qst_path(*_a, **_k):
        return FakePrompt(next(path_answers))

    checkbox_call_count = [0]

    def fake_checkbox(*_a, **_k):
        checkbox_call_count[0] += 1
        if checkbox_call_count[0] == 1:
            # Outputs: select only graphs (no markdown, no wordclouds)
            return FakePrompt([OutputKind.GRAPHS])
        # Extras
        return FakePrompt(["canvas", "custom_instructions"])

    select_call_count = [0]

    def fake_select(*_a, **_k):
        select_call_count[0] += 1
        return FakePrompt("standard")

    text_call_count = [0]

    def fake_text(*_a, **_k):
        text_call_count[0] += 1
        return FakePrompt("# Me")

    monkeypatch.setattr(interactive, "qst_path", fake_qst_path)
    monkeypatch.setattr(interactive, "checkbox", fake_checkbox)
    monkeypatch.setattr(interactive, "select", fake_select)
    monkeypatch.setattr(interactive, "qst_text", fake_text)

    config = run_interactive_config(get_default_config())

    # No select calls (no markdown flavor/render order, no font, no colormap)
    assert select_call_count[0] == 0
    # No text calls (no author headers, no stopwords)
    assert text_call_count[0] == 0
    # Only 2 checkbox calls (output selection + extras), no YAML fields checkbox
    assert checkbox_call_count[0] == 2
    # Verify only graphs selected
    assert config.outputs == {OutputKind.GRAPHS}


def test_outputs_prompt_respects_existing_config(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that the outputs prompt respects the pre-existing configuration."""
    import convoviz.interactive as interactive

    # Setup mocks
    monkeypatch.setattr(interactive, "find_latest_valid_zip", lambda: None)
    monkeypatch.setattr(interactive, "find_script_export", lambda: None)

    captured_choices = []

    def fake_checkbox(*_a, **_k):
        choices = _k.get("choices", _a[1] if len(_a) > 1 else [])
        captured_choices.append(choices)
        # Simulate user pressing enter immediately (returning the checked items)
        selected = [c.value for c in choices if c.checked]
        return FakePrompt(selected)

    monkeypatch.setattr(interactive, "checkbox", fake_checkbox)
    # Mock other prompts to just return defaults
    monkeypatch.setattr(interactive, "qst_path", lambda *_a, **_k: FakePrompt("dummy"))
    # Mock text/select just in case
    monkeypatch.setattr(interactive, "qst_text", lambda *_a, **_k: FakePrompt("val"))
    monkeypatch.setattr(interactive, "select", lambda *_a, **_k: FakePrompt("val"))
    monkeypatch.setattr(interactive, "confirm", lambda *_a, **_k: FakePrompt(True))

    # Create a config with ONLY Markdown selected
    initial_config = get_default_config()
    initial_config.outputs = {OutputKind.MARKDOWN}

    # Run
    run_interactive_config(initial_config)

    # Verify the first checkbox (Outputs) had only Markdown checked
    output_choices = captured_choices[0]

    markdown_choice = next(c for c in output_choices if c.value == OutputKind.MARKDOWN)
    graphs_choice = next(c for c in output_choices if c.value == OutputKind.GRAPHS)

    assert markdown_choice.checked is True
    assert graphs_choice.checked is False


def test_script_export_merge_prompt(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Test that the script export merge prompt appears and sets config."""
    import convoviz.interactive as interactive

    # Mock script export found
    export_path = tmp_path / "convoviz_export.json"
    export_path.write_text("[]")
    monkeypatch.setattr(interactive, "find_script_export", lambda: export_path)
    monkeypatch.setattr(interactive, "find_latest_valid_zip", lambda: None)

    # Mock other prompts
    path_answers = iter(["dummy.zip", str(tmp_path / "out")])
    monkeypatch.setattr(
        interactive, "qst_path", lambda *_a, **_k: FakePrompt(next(path_answers))
    )
    checkbox_call_count = [0]

    def fake_checkbox(*_a, **_k):
        checkbox_call_count[0] += 1
        if checkbox_call_count[0] == 1:
            return FakePrompt([OutputKind.GRAPHS])
        return FakePrompt(["canvas", "custom_instructions"])

    monkeypatch.setattr(interactive, "checkbox", fake_checkbox)

    # Mock confirm prompt - User says YES
    monkeypatch.setattr(interactive, "confirm", lambda *_a, **_k: FakePrompt(True))

    config = run_interactive_config(get_default_config())

    assert config.bookmarklet_path == export_path


def test_script_export_merge_prompt_declined(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Test that declining the script export merge prompt does not set config."""
    import convoviz.interactive as interactive

    # Mock script export found
    export_path = tmp_path / "convoviz_export.json"
    export_path.write_text("[]")
    monkeypatch.setattr(interactive, "find_script_export", lambda: export_path)
    monkeypatch.setattr(interactive, "find_latest_valid_zip", lambda: None)

    # Mock other prompts
    path_answers = iter(["dummy.zip", str(tmp_path / "out")])
    monkeypatch.setattr(
        interactive, "qst_path", lambda *_a, **_k: FakePrompt(next(path_answers))
    )
    checkbox_call_count = [0]

    def fake_checkbox(*_a, **_k):
        checkbox_call_count[0] += 1
        if checkbox_call_count[0] == 1:
            return FakePrompt([OutputKind.GRAPHS])
        return FakePrompt(["canvas", "custom_instructions"])

    monkeypatch.setattr(interactive, "checkbox", fake_checkbox)

    # Mock confirm prompt - User says NO
    monkeypatch.setattr(interactive, "confirm", lambda *_a, **_k: FakePrompt(False))

    config = run_interactive_config(get_default_config())

    assert config.bookmarklet_path is None


def test_script_export_merge_prompt_skipped_if_manually_selected(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Test that the script export merge prompt is skipped if it's already the input."""
    import convoviz.interactive as interactive

    # Mock script export found
    export_path = tmp_path / "convoviz_export.json"
    export_path.write_text("[]")
    monkeypatch.setattr(interactive, "find_script_export", lambda: export_path)
    monkeypatch.setattr(interactive, "find_latest_valid_zip", lambda: export_path)

    # Mock other prompts
    # User selects the export_path as their main input
    monkeypatch.setattr(
        interactive, "qst_path", lambda *_a, **_k: FakePrompt(str(export_path))
    )
    checkbox_call_count = [0]

    def fake_checkbox(*_a, **_k):
        checkbox_call_count[0] += 1
        if checkbox_call_count[0] == 1:
            return FakePrompt([OutputKind.GRAPHS])
        return FakePrompt(["canvas", "custom_instructions"])

    monkeypatch.setattr(interactive, "checkbox", fake_checkbox)

    # Mock confirm prompt - should NOT be called!
    # If it is called, it will crash because we haven't mocked it specifically here or we can monitor it
    confirm_called = [False]

    def fake_confirm(*_a, **_k):
        confirm_called[0] = True
        return FakePrompt(True)

    monkeypatch.setattr(interactive, "confirm", fake_confirm)

    config = run_interactive_config(get_default_config())

    # Verify input_path is correct but bookmarklet_path is NOT set (since no prompt happened)
    # resolve() because we resolve in interactive.py
    assert config.input_path.resolve() == export_path.resolve()
    assert config.bookmarklet_path is None
    assert confirm_called[0] is False


def test_output_validation_does_not_create_directories(tmp_path: Path) -> None:
    """Validation should not create output directories during typing."""
    import convoviz.interactive as interactive

    target = tmp_path / "new" / "output"
    assert not target.exists()
    assert not (tmp_path / "new").exists()

    result = interactive._validate_output_path(str(target))

    assert result is True
    assert not target.exists()
    assert not (tmp_path / "new").exists()
