"""Convoviz - ChatGPT data visualization and export tool."""

from typing import Any

from convoviz import config, io, models, renderers, utils
from convoviz.config import ConvovizConfig, get_default_config
from convoviz.models import Conversation, ConversationCollection, Message, Node
from convoviz.pipeline import run_pipeline

__all__ = [
    "Conversation",
    "ConversationCollection",
    "ConvovizConfig",
    "Message",
    "Node",
    "analysis",
    "config",
    "get_default_config",
    "io",
    "models",
    "renderers",
    "run_pipeline",
    "utils",
]


def __getattr__(name: str) -> Any:
    """Lazy import for optional submodules like analysis."""
    if name == "analysis":
        from convoviz import analysis  # noqa: PLC0415

        return analysis
    msg = f"module {__name__!r} has no attribute {name!r}"
    raise AttributeError(msg)
