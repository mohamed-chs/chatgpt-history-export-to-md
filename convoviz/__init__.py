"""Convoviz - ChatGPT data visualization and export tool."""

from convoviz import config, io, models, renderers, utils
from convoviz.config import ConvovizConfig, get_default_config
from convoviz.models import Conversation, ConversationCollection, Message, Node
from convoviz.pipeline import run_pipeline

__all__ = [
    # Submodules
    "analysis",
    "config",
    "io",
    "models",
    "renderers",
    "utils",
    # Main classes
    "Conversation",
    "ConversationCollection",
    "ConvovizConfig",
    "Message",
    "Node",
    # Functions
    "get_default_config",
    "run_pipeline",
]


def __getattr__(name: str):
    """Lazy import for optional submodules like analysis."""
    if name == "analysis":
        from convoviz import analysis

        return analysis
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
