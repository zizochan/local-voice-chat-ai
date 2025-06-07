from gui import run_gui, create_speaker_dropdown, create_model_dropdown
from transcriber import transcribe_audio
from chat import (
    load_history,
    save_history,
    query_lmstudio,
    get_model_list,
    chat_with_lmstudio,
)
from speaker import speak_with_aivis_speech, get_speaker_choices
import threading
from typing import List, Dict, Any
import os

WINDOW_SIZE = "500x700"
DROPDOWN_WIDTH = 30


def get_scenario_list():
    scenario_dir = os.path.join(os.path.dirname(__file__), "../scenarios")
    scenario_files = [f for f in os.listdir(scenario_dir) if f.endswith(".txt")]
    scenario_files.sort()
    return scenario_files


def load_scenario_content(filename):
    scenario_dir = os.path.join(os.path.dirname(__file__), "../scenarios")
    with open(os.path.join(scenario_dir, filename), encoding="utf-8") as f:
        return f.read().strip()


def get_character_list():
    character_dir = os.path.join(os.path.dirname(__file__), "../characters")
    if not os.path.exists(character_dir):
        return []
    character_files = [f for f in os.listdir(character_dir) if f.endswith(".txt")]
    character_files.sort()
    return character_files


def load_character_content(filename):
    character_dir = os.path.join(os.path.dirname(__file__), "../characters")
    with open(os.path.join(character_dir, filename), encoding="utf-8") as f:
        return f.read().strip()


if __name__ == "__main__":
    run_gui(
        get_scenario_list,
        load_scenario_content,
        get_character_list,
        load_character_content,
    )
