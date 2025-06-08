import os
import json
from chat import get_model_list
from speaker import get_speaker_choices


def get_character_list():
    characters_dir = os.path.join(os.path.dirname(__file__), "../characters")
    if not os.path.exists(characters_dir):
        return []
    return [f for f in os.listdir(characters_dir) if f.endswith(".txt")]


def get_scenario_list():
    scenarios_dir = os.path.join(os.path.dirname(__file__), "../scenarios")
    if not os.path.exists(scenarios_dir):
        return []
    return [f for f in os.listdir(scenarios_dir) if f.endswith(".txt")]


def load_config(path="tmp/config.json"):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_config(config, path="tmp/config.json"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def get_initial_selections():
    config = load_config()
    return {
        "model": config.get("model"),
        "speaker": config.get("speaker"),
        "character": config.get("character"),
        "scenario": config.get("scenario"),
    }
