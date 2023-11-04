"""Utility functions for the project."""

from __future__ import annotations

from pathlib import Path
from re import compile as re_compile
from re import sub as re_sub
from typing import Any, Literal, TypedDict
from zipfile import ZipFile

DOWNLOADS = Path.home() / "Downloads"


def latest_zip() -> Path:
    """Path to the most recently created zip file in the Downloads folder."""
    zip_files = list(DOWNLOADS.glob("*.zip"))

    if not zip_files:
        err_msg = f"No zip files found in {DOWNLOADS}"
        raise FileNotFoundError(err_msg)

    return max(zip_files, key=lambda x: x.stat().st_ctime)


def latest_bookmarklet_json() -> Path | None:
    """Path to the most recent JSON file in Downloads with 'bookmarklet' in the name."""
    bkmrklet_files = [x for x in DOWNLOADS.glob("*.json") if "bookmarklet" in x.name]

    if not bkmrklet_files:
        return None

    return max(bkmrklet_files, key=lambda x: x.stat().st_ctime)


def sanitize(filename: str) -> str:
    """Sanitized title of the conversation, compatible with file names."""
    anti_pattern = re_compile(r'[<>:"/\\|?*\n\r\t\f\v]+')

    return anti_pattern.sub("_", filename.strip()) or "untitled"


def close_code_blocks(text: str) -> str:
    """Ensure that all code blocks are closed."""
    # A code block can be opened with triple backticks, possibly followed by a lang name
    # It can only be closed however with triple backticks, with nothing else on the line

    open_code_block = False

    lines = text.split("\n")

    for line in lines:
        if line.startswith("```") and not open_code_block:
            open_code_block = True
            continue

        if line == "```" and open_code_block:
            open_code_block = False

    if open_code_block:
        text += "\n```"

    return text


def replace_latex_delimiters(text: str) -> str:
    """Replace all the LaTeX bracket delimiters in the string with dollar sign ones."""
    text = re_sub(r"\\\[", "$$", text)
    text = re_sub(r"\\\]", "$$", text)
    text = re_sub(r"\\\(", "$", text)

    return re_sub(r"\\\)", "$", text)


def stem(path: Path | str) -> str:
    """Return the `stem` of the given path."""
    return Path(path).stem


def root_dir() -> Path:
    """Path to the root directory of the project.

    might change when refactoring, currently it's `convoviz/`
    """
    return Path(__file__).parent


def font_names() -> list[str]:
    """List of font names in the `assets/fonts` folder."""
    fonts_path = root_dir() / "assets" / "fonts"
    return [font.stem for font in fonts_path.iterdir()]


def font_path(font_name: str) -> Path:
    """Path to the given font in the `assets/fonts` folder.

    `font_name` should be the stem of the font file, without the extension
    """
    return root_dir() / "assets" / "fonts" / f"{font_name}.ttf"


def default_font_path() -> Path:
    """Path to the default font in the `assets/fonts` folder."""
    return font_path("RobotoSlab-Thin")


def colormaps() -> list[str]:
    """List of colormaps in the `assets/colormaps.txt` file."""
    colormaps_path = root_dir() / "assets" / "colormaps.txt"
    with colormaps_path.open(encoding="utf-8") as file:
        return file.read().splitlines()


def validate_header(text: str) -> bool:
    """Return True if the given text is a valid markdown header."""
    max_header_level = 6
    return (
        1 <= text.count("#") <= max_header_level
        and text.startswith("#")
        and text[len(text.split()[0])] == " "
    )


def validate_zip(filepath: str | Path) -> bool:
    """Return True if the given path is a zip file with a `conversations.json` file."""
    filepath = Path(filepath)
    if not filepath.is_file() or filepath.suffix != ".zip":
        return False
    with ZipFile(filepath) as zip_ref:
        if "conversations.json" in zip_ref.namelist():
            return True
    return False


def get_archive(filepath: Path | str) -> Path:
    """Extract the zip and return the path to the extracted folder."""
    filepath = Path(filepath)
    folder = filepath.with_suffix("")

    with ZipFile(filepath) as file:
        file.extractall(folder)

    return folder


def code_block(text: str, lang: str = "python") -> str:
    """Wrap the given string in a code block."""
    return f"```{lang}\n{text}\n```"


# default configs


class AuthorHeaders(TypedDict):
    """Type hint for the author headers configs."""

    system: str
    user: str
    assistant: str
    tool: str


class MessageConfigs(TypedDict):
    """Type hint for the message configs."""

    author_headers: AuthorHeaders


DEFAULT_MESSAGE_CONFIGS: MessageConfigs = {
    "author_headers": {
        "system": "### System",
        "user": "# Me",
        "assistant": "# ChatGPT",
        "tool": "### Tool output",
    },
}


class MarkdownConfigs(TypedDict):
    """Type hint for the markdown configs."""

    latex_delimiters: Literal["default", "dollars"]


class YAMLConfigs(TypedDict):
    """Type hint for the yaml configs."""

    title: bool
    tags: bool
    chat_link: bool
    create_time: bool
    update_time: bool
    model: bool
    used_plugins: bool
    message_count: bool
    content_types: bool
    custom_instructions: bool


class ConversationConfigs(TypedDict):
    """Type hint for the conversation configs."""

    markdown: MarkdownConfigs
    yaml: YAMLConfigs


DEFAULT_CONVERSATION_CONFIGS: ConversationConfigs = {
    "markdown": {"latex_delimiters": "default"},
    "yaml": {
        "title": True,
        "tags": False,
        "chat_link": True,
        "create_time": True,
        "update_time": True,
        "model": True,
        "used_plugins": True,
        "message_count": True,
        "content_types": True,
        "custom_instructions": True,
    },
}


class GraphKwargs(TypedDict, total=False):
    """Type hint for the graph configs."""


class WordCloudKwargs(TypedDict, total=False):
    """Type hint for the wordcloud configs."""

    font_path: str
    colormap: str
    custom_stopwords: str
    background_color: str | None
    mode: Literal["RGB", "RGBA"]
    include_numbers: bool
    width: int
    height: int


DEFAULT_WORDCLOUD_CONFIGS: WordCloudKwargs = {
    "font_path": str(default_font_path()),
    "colormap": "prism",
    "custom_stopwords": "use, file, ",
    "background_color": None,
    "mode": "RGBA",
    "include_numbers": False,
    "width": 1000,
    "height": 1000,
}


class AllConfigs(TypedDict):
    """Type hint for the user config JSON file."""

    zip_filepath: str
    output_folder: str
    message: MessageConfigs
    conversation: ConversationConfigs
    wordcloud: WordCloudKwargs
    graph: GraphKwargs
    node: dict[str, Any]
    conversation_set: dict[str, Any]


DEFAULT_USER_CONFIGS: AllConfigs = {
    "zip_filepath": str(latest_zip()),
    "output_folder": str(Path.home() / "Documents" / "ChatGPT Data"),
    "message": DEFAULT_MESSAGE_CONFIGS,
    "conversation": DEFAULT_CONVERSATION_CONFIGS,
    "wordcloud": DEFAULT_WORDCLOUD_CONFIGS,
    "graph": {},
    "node": {},
    "conversation_set": {},
}
