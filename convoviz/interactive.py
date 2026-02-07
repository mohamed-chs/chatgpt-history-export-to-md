"""Interactive configuration prompts using questionary."""

import logging
from typing import Literal, Protocol, cast

from questionary import Choice, Style, checkbox, confirm, select
from questionary import path as qst_path
from questionary import text as qst_text

from convoviz.config import ConvovizConfig, OutputKind, YAMLConfig, get_default_config
from convoviz.io.loaders import find_latest_valid_zip, find_script_export, validate_zip
from convoviz.utils import (
    colormaps,
    default_font_path,
    expand_path,
    font_names,
    font_path,
    validate_header,
)

OUTPUT_TITLES = {
    OutputKind.MARKDOWN: "Markdown conversations",
    OutputKind.GRAPHS: "Graphs (usage analytics)",
    OutputKind.WORDCLOUDS: "Word clouds",
}

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
    ]
)

logger = logging.getLogger(__name__)


class _QuestionaryPrompt[T](Protocol):
    def ask(self) -> T | None: ...


def _ask_or_cancel[T](prompt: _QuestionaryPrompt[T]) -> T:
    """Ask a questionary prompt; treat Ctrl+C/Ctrl+D as cancelling the run.

    questionary's `.ask()` returns `None` on cancellation (Ctrl+C / Ctrl+D). We
    convert that to `KeyboardInterrupt` so callers can abort the whole
    interactive session with a single Ctrl+C.
    """

    result = prompt.ask()
    if result is None:
        raise KeyboardInterrupt
    return result


def _validate_input_path(raw: str) -> bool | str:
    path = expand_path(raw)
    if not path.exists():
        return "Path must exist"

    if path.is_dir():
        if (path / "conversations.json").exists():
            return True
        return "Directory must contain conversations.json"

    if path.suffix.lower() == ".json":
        return True

    if path.suffix.lower() == ".zip":
        return True if validate_zip(path) else "ZIP must contain conversations.json"

    return "Input must be a .zip, a .json, or a directory containing conversations.json"


def run_interactive_config(initial_config: ConvovizConfig | None = None) -> ConvovizConfig:
    """Run interactive prompts to configure convoviz.

    Args:
        initial_config: Optional starting configuration (uses defaults if None)

    Returns:
        Updated configuration based on user input
    """
    config = initial_config or get_default_config()
    logger.info("Starting interactive configuration")

    # Set sensible defaults if not already set
    if not config.input_path:
        latest = find_latest_valid_zip()
        if latest:
            config.input_path = latest

    if not config.wordcloud.font_path:
        config.wordcloud.font_path = default_font_path()

    # Prompt for input path
    input_default = str(config.input_path) if config.input_path else ""
    input_result: str = _ask_or_cancel(
        qst_path(
            "Enter the path to the export ZIP, JSON, or extracted directory:",
            default=input_default,
            validate=_validate_input_path,
            style=CUSTOM_STYLE,
        )
    )

    if input_result:
        config.input_path = expand_path(input_result)
    logger.debug(f"User selected input: {config.input_path}")
    # Prompt to merge script export if detected (and not already selected as primary input)
    script_export = find_script_export()
    if script_export and (
        not config.input_path or script_export.resolve() != config.input_path.resolve()
    ):
        merge_it: bool = _ask_or_cancel(
            confirm(
                f"Found recent convoviz script export: {script_export.name}\n  Merge it with your main input?",
                default=True,
                style=CUSTOM_STYLE,
            )
        )
        if merge_it:
            config.bookmarklet_path = script_export
            logger.debug(f"User confirmed script export merge: {script_export}")
        else:
            logger.debug("User declined script export merge")

    # Prompt for output folder
    output_result: str = _ask_or_cancel(
        qst_path(
            "Enter the path to the output folder:",
            default=str(config.output_folder),
            style=CUSTOM_STYLE,
        )
    )

    if output_result:
        config.output_folder = expand_path(output_result)
    logger.debug(f"User selected output: {config.output_folder}")

    # Prompt for outputs to generate
    while True:
        output_choices = [
            Choice(
                title=OUTPUT_TITLES.get(kind, kind.value.title()),
                value=kind,
                checked=kind in config.outputs,
            )
            for kind in OutputKind
        ]

        selected_outputs: list[OutputKind] = _ask_or_cancel(
            checkbox(
                "Select outputs to generate:",
                choices=output_choices,
                style=CUSTOM_STYLE,
            )
        )

        if selected_outputs:
            config.outputs = set(selected_outputs)
            break

        proceed_empty: bool = _ask_or_cancel(
            confirm(
                "No outputs selected. Continue anyway?",
                default=False,
                style=CUSTOM_STYLE,
            )
        )
        if proceed_empty:
            config.outputs = set()
            break
    logger.debug(f"User selected outputs: {config.outputs}")

    extra_choices = [
        Choice(title="Canvas documents", value="canvas", checked=config.export_canvas),
        Choice(
            title="Custom instructions (custom_instructions.json)",
            value="custom_instructions",
            checked=config.export_custom_instructions,
        ),
    ]
    selected_extras: list[str] = _ask_or_cancel(
        checkbox(
            "Select extra exports:",
            choices=extra_choices,
            style=CUSTOM_STYLE,
        )
    )
    selected_extras_set = set(selected_extras)
    config.export_canvas = "canvas" in selected_extras_set
    config.export_custom_instructions = "custom_instructions" in selected_extras_set
    logger.debug(
        "User selected extras: canvas=%s, custom_instructions=%s",
        config.export_canvas,
        config.export_custom_instructions,
    )

    # Prompt for markdown settings (only if markdown output is selected)
    if OutputKind.MARKDOWN in config.outputs:
        # Prompt for author headers
        headers = config.message.author_headers
        for role in ["user", "assistant"]:
            current = getattr(headers, role)
            result: str = _ask_or_cancel(
                qst_text(
                    f"Enter the message header for '{role}':",
                    default=current,
                    validate=lambda t: (
                        validate_header(t) or "Must be a valid markdown header (e.g., # Title)"
                    ),
                    style=CUSTOM_STYLE,
                )
            )
            if result:
                setattr(headers, role, result)
        logger.debug(f"User selected headers: {headers}")

        # Prompt for markdown flavor
        flavor_result = cast(
            Literal["standard", "obsidian", "pandoc"],
            _ask_or_cancel(
                select(
                    "Select the markdown flavor:",
                    choices=["standard", "obsidian", "pandoc"],
                    default=config.conversation.markdown.flavor,
                    style=CUSTOM_STYLE,
                )
            ),
        )

        if flavor_result:
            config.conversation.markdown.flavor = flavor_result
        logger.debug(f"User selected flavor: {config.conversation.markdown.flavor}")

        render_order_result = cast(
            Literal["active", "full"],
            _ask_or_cancel(
                select(
                    "Select conversation render order:",
                    choices=[
                        Choice(title="Active branch only (recommended)", value="active"),
                        Choice(title="Full DAG (all branches)", value="full"),
                    ],
                    default=config.conversation.markdown.render_order,
                    style=CUSTOM_STYLE,
                )
            ),
        )
        if render_order_result:
            config.conversation.markdown.render_order = render_order_result
        logger.debug(f"User selected render order: {config.conversation.markdown.render_order}")

        if config.conversation.markdown.flavor == "pandoc":
            enable_pdf: bool = _ask_or_cancel(
                confirm(
                    "Inject PDF frontmatter (Typst) for pandoc flavor?",
                    default=config.conversation.pandoc_pdf.enabled,
                    style=CUSTOM_STYLE,
                )
            )
            config.conversation.pandoc_pdf.enabled = enable_pdf
            logger.debug(f"User selected Pandoc PDF frontmatter: {enable_pdf}")

        # Prompt for YAML headers
        yaml_config = config.conversation.yaml
        yaml_fields = list(YAMLConfig.model_fields.keys())
        yaml_choices = [
            Choice(title=field, checked=getattr(yaml_config, field)) for field in yaml_fields
        ]

        selected: list[str] = _ask_or_cancel(
            checkbox(
                "Select YAML metadata headers to include:",
                choices=yaml_choices,
                style=CUSTOM_STYLE,
            )
        )

        selected_set = set(selected)
        for field_name in yaml_fields:
            setattr(yaml_config, field_name, field_name in selected_set)

    # Prompt for wordcloud settings (only if wordclouds output is selected)
    if OutputKind.WORDCLOUDS in config.outputs:
        # Prompt for font
        available_fonts = font_names()
        if available_fonts:
            current_font = (
                config.wordcloud.font_path.stem
                if config.wordcloud.font_path
                else available_fonts[0]
            )
            font_result: str = _ask_or_cancel(
                select(
                    "Select the font for word clouds:",
                    choices=available_fonts,
                    default=current_font if current_font in available_fonts else available_fonts[0],
                    style=CUSTOM_STYLE,
                )
            )

            if font_result:
                config.wordcloud.font_path = font_path(font_result)

        # Prompt for colormap
        available_colormaps = colormaps()
        if available_colormaps:
            colormap_result: str = _ask_or_cancel(
                select(
                    "Select the color theme for word clouds:",
                    choices=available_colormaps,
                    default=config.wordcloud.colormap
                    if config.wordcloud.colormap in available_colormaps
                    else available_colormaps[0],
                    style=CUSTOM_STYLE,
                )
            )

            if colormap_result:
                config.wordcloud.colormap = colormap_result

        # Prompt for custom stopwords
        stopwords_result: str = _ask_or_cancel(
            qst_text(
                "Enter custom stopwords (comma-separated):",
                default=config.wordcloud.custom_stopwords,
                style=CUSTOM_STYLE,
            )
        )

        config.wordcloud.custom_stopwords = stopwords_result

    return config
