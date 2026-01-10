"""Tests for interactive prompts."""

from __future__ import annotations

from pathlib import Path

import pytest

from convoviz.config import get_default_config
from convoviz.interactive import run_interactive_config


class FakePrompt[T]:
    """Minimal stand-in for a questionary prompt object."""

    def __init__(self, result: T | None) -> None:
        self._result = result

    def ask(self) -> T | None:
        return self._result


def test_ctrl_c_on_first_prompt_aborts_interactive(monkeypatch: pytest.MonkeyPatch) -> None:
    import convoviz.interactive as interactive

    monkeypatch.setattr(interactive, "find_latest_zip", lambda: None)
    monkeypatch.setattr(interactive, "qst_path", lambda *_a, **_k: FakePrompt(None))

    with pytest.raises(KeyboardInterrupt):
        run_interactive_config(get_default_config())


def test_ctrl_c_mid_flow_aborts_interactive(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    import convoviz.interactive as interactive

    monkeypatch.setattr(interactive, "find_latest_zip", lambda: None)

    path_answers = iter(["dummy.zip", str(tmp_path / "out")])

    def fake_qst_path(*_a, **_k):
        return FakePrompt(next(path_answers))

    monkeypatch.setattr(interactive, "qst_path", fake_qst_path)
    monkeypatch.setattr(interactive, "qst_text", lambda *_a, **_k: FakePrompt(None))

    with pytest.raises(KeyboardInterrupt):
        run_interactive_config(get_default_config())
