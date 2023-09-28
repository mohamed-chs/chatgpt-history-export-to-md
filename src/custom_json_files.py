import json
import os

from .metadata_extraction import extract_metadata
from .utils import timestamp_to_str as tts


def create_custom_instructions_json(
    json_filepath: str, out_folder: str, deduplication_mode: str = "all"
):
    with open(json_filepath, "r", encoding="utf-8") as file:
        conversations = json.load(file)

    custom_instructions = []
    seen_messages = {}

    for conversation in conversations:
        metadata = extract_metadata(conversation)
        custom_instruction = {
            "chat_title": metadata["title"],
            "chat_link": f"https://chat.openai.com/c/{metadata['id']}",
            "time": tts(metadata["create_time"]),
            "about_me": metadata["about_user_message"],
            "about_chatgpt": metadata["about_model_message"],
        }

        if (
            custom_instruction["about_me"] == "-"
            and custom_instruction["about_chatgpt"] == "-"
        ):
            continue

        # Use the tuple of (about_me, about_chatgpt) as key for deduplication
        key = (custom_instruction["about_me"], custom_instruction["about_chatgpt"])

        if deduplication_mode == "latest":
            if (
                key not in seen_messages
                or seen_messages[key]["time"] < custom_instruction["time"]
            ):
                seen_messages[key] = custom_instruction

        elif deduplication_mode == "earliest":
            if (
                key not in seen_messages
                or seen_messages[key]["time"] > custom_instruction["time"]
            ):
                seen_messages[key] = custom_instruction

        elif deduplication_mode == "all":
            custom_instructions.append(custom_instruction)  # type: ignore

    if deduplication_mode in ["latest", "earliest"]:
        custom_instructions.extend(seen_messages.values())  # type: ignore

    ci_json_filepath = os.path.join(out_folder, "custom_instructions.json")
    
    print("Writing 'custom_instructions.json' file...\n")

    with open(ci_json_filepath, "w", encoding="utf-8") as file:
        json.dump(custom_instructions, file, indent=2, ensure_ascii=False)
        
    print("Done!\n")
