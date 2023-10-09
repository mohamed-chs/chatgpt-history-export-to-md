"""Module for handling user configuration and updating the models."""

import json
from pathlib import Path
from typing import Any, Dict

from models.conversation import Conversation
from models.conversation_list import ConversationList
from models.message import Message
from models.node import Node
from views.prompt_user import prompt_user

CONFIG_PATH = Path("config.json")

HOME: Path = Path.home()
DOWNLOADS: Path = HOME / "Downloads"

# most recent zip file in downloads folder
DEFAULT_ZIP_FILE: Path = max(DOWNLOADS.glob("*.zip"), key=lambda x: x.stat().st_ctime)

DEFAULT_OUTPUT_FOLDER: Path = HOME / "Documents" / "ChatGPT Data"


def get_user_configs() -> Dict[str, Any]:
    """Prompt the user for configuration options, with defaults from the config file.

    Returns the user configuration as a dictionary."""

    with open(CONFIG_PATH, "r", encoding="utf-8") as file:
        default_configs = json.load(file)

    if not default_configs["zip_file"]:
        default_configs["zip_file"] = str(DEFAULT_ZIP_FILE)

    if not default_configs["output_folder"]:
        default_configs["output_folder"] = str(DEFAULT_OUTPUT_FOLDER)

    return prompt_user(default_configs)


def update_config_file(user_configs: Dict[str, Any]) -> None:
    """Update the config file with the user's configuration options."""
    with open(CONFIG_PATH, "w", encoding="utf-8") as file:
        json.dump(user_configs, file, indent=2)


def set_model_configs(configs: Dict[str, Any]) -> None:
    """Set the configuration for all models."""
    Conversation.configuration = configs.get("conversation", {})
    ConversationList.configuration = configs.get("conversation_list", {})
    Message.configuration = configs.get("message", {})
    Node.configuration = configs.get("node", {})
