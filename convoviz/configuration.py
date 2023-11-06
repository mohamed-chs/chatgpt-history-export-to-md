"""Module for handling user configuration and updating the models."""

from __future__ import annotations

from questionary import (
    Choice,
    Style,
    checkbox,
    select,
)
from questionary import (
    path as qst_path,
)
from questionary import (
    text as qst_text,
)

from .models import Conversation, Message
from .utils import (
    DEFAULT_USER_CONFIGS,
    colormaps,
    font_names,
    font_path,
    stem,
    validate_header,
    validate_zip,
)

CUSTOM_STYLE = Style(
    [
        ("qmark", "fg:#34eb9b bold"),
        ("question", "bold fg:#e0e0e0"),
        ("answer", "fg:#34ebeb bold"),
        ("pointer", "fg:#e834eb bold"),
        ("highlighted", "fg:#349ceb bold"),
        ("selected", "fg:#34ebeb"),
        ("separator", "fg:#eb3434"),
        ("instruction", "fg:#eb9434"),
        ("text", "fg:#b2eb34"),
        ("disabled", "fg:#858585 italic"),
    ],
)


class UserConfigs:
    """Class for handling user configuration."""

    def __init__(self) -> None:
        """Initialize UserConfigs object."""
        self.configs = DEFAULT_USER_CONFIGS.copy()

        # will implement a way to read from a config file later ...

    def prompt(self) -> None:
        """Prompt the user for input and update the configs."""
        lookup = self.configs

        lookup["zip_filepath"] = qst_path(
            "Enter the path to the zip file :",
            lookup["zip_filepath"],
            validate=validate_zip,
            style=CUSTOM_STYLE,
        ).ask()

        lookup["output_folder"] = qst_path(
            "Enter the path to the output folder :",
            lookup["output_folder"],
            style=CUSTOM_STYLE,
        ).ask()

        for author_role in lookup["message"]["author_headers"]:
            lookup["message"]["author_headers"][author_role] = qst_text(
                f"Enter the message header (#) for messages from '{author_role}' :",
                lookup["message"]["author_headers"][author_role],
                validate=validate_header,
                style=CUSTOM_STYLE,
            ).ask()

        lookup["conversation"]["markdown"]["latex_delimiters"] = select(
            "Select the LaTeX math delimiters you want to use :",
            ["default", "dollars"],
            lookup["conversation"]["markdown"]["latex_delimiters"],
            style=CUSTOM_STYLE,
        ).ask()

        yaml_choices = [
            Choice(title=header, checked=value)
            for header, value in lookup["conversation"]["yaml"].items()
        ]

        selected_headers = checkbox(
            "Select the YAML metadata headers you want to include :",
            yaml_choices,
            style=CUSTOM_STYLE,
        ).ask()

        for header in lookup["conversation"]["yaml"]:
            lookup["conversation"]["yaml"][header] = header in selected_headers

        font_name: str = select(
            "Select the font you want to use for the word clouds :",
            font_names(),
            stem(lookup["wordcloud"].get("font_path") or ""),
            style=CUSTOM_STYLE,
        ).ask()

        lookup["wordcloud"]["font_path"] = str(font_path(font_name))

        lookup["wordcloud"]["colormap"] = select(
            "Select the color theme you want to use for the word clouds :",
            colormaps(),
            lookup["wordcloud"].get("colormap"),
            style=CUSTOM_STYLE,
        ).ask()

        lookup["wordcloud"]["custom_stopwords"] = qst_text(
            "Enter custom stopwords (separated by commas) :",
            lookup["wordcloud"].get("custom_stopwords", ""),
            style=CUSTOM_STYLE,
        ).ask()

    def set_model_configs(self) -> None:
        """Set the configuration for all models."""
        Message.update_configs(self.configs["message"])
        Conversation.update_configs(self.configs["conversation"])
