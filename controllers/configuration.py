"""Module for handling user configuration and updating the models."""

import json
from typing import Any

from models.conversation import Conversation
from models.conversation_set import ConversationSet
from models.message import Message
from models.node import Node
from views.prompt_user import prompt_user

from .file_system import default_output_folder, get_openai_zip_filepath


def get_user_configs() -> dict[str, Any]:
    """Loads the default configs and calls the prompt_user function with those defaults.
    Returns the new configuration."""

    with open("config.json", "r", encoding="utf-8") as file:
        default_configs = json.load(file)

    if not default_configs["zip_file"]:
        default_configs["zip_file"] = get_openai_zip_filepath()

    if not default_configs["output_folder"]:
        default_configs["output_folder"] = default_output_folder()

    return prompt_user(default_configs)


def update_config_file(user_configs: dict[str, Any]) -> None:
    """Update the config file with the new configuration options."""
    with open("config.json", "w", encoding="utf-8") as file:
        json.dump(user_configs, file, indent=2)


def set_model_configs(configs: dict[str, Any]) -> None:
    """Set the configuration for all models."""
    Conversation.configuration = configs.get("conversation", {})
    ConversationSet.configuration = configs.get("conversation_set", {})
    Message.configuration = configs.get("message", {})
    Node.configuration = configs.get("node", {})
