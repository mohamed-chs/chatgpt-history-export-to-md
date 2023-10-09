"""Module for handling user configuration and updating the models."""

import json
from pathlib import Path
from typing import Any, Dict

from models.conversation import Conversation
from models.conversation_list import ConversationList
from models.message import Message
from models.node import Node
from views.prompt_user import prompt_user


def get_user_configs() -> Dict[str, Any]:
    """Prompt the user for configuration options, with defaults from the config file.

    Returns the user configuration as a dictionary."""

    downloads_folder: Path = Path.home() / "Downloads"

    # most recent zip file in downloads folder
    default_zip_filepath: Path = max(
        downloads_folder.glob("*.zip"), key=lambda x: x.stat().st_ctime
    )

    default_output_folder: Path = Path.home() / "Documents" / "ChatGPT Data"

    with open("config.json", "r", encoding="utf-8") as file:
        default_configs = json.load(file)

    if not default_configs["zip_file"]:
        default_configs["zip_file"] = str(default_zip_filepath)

    if not default_configs["output_folder"]:
        default_configs["output_folder"] = str(default_output_folder)

    return prompt_user(default_configs)


def update_config_file(user_configs: Dict[str, Any]) -> None:
    """Update the config file with the user's configuration options."""
    with open("config.json", "w", encoding="utf-8") as file:
        json.dump(user_configs, file, indent=2)


def set_model_configs(configs: Dict[str, Any]) -> None:
    """Set the configuration for all models."""
    Conversation.configuration = configs.get("conversation", {})
    ConversationList.configuration = configs.get("conversation_list", {})
    Message.configuration = configs.get("message", {})
    Node.configuration = configs.get("node", {})
