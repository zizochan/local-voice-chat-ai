import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import List, Dict, Any
from chat import (
    load_history,
    save_history,
    query_lmstudio,
    get_model_list,
    chat_with_lmstudio,
)
from speaker import speak_with_aivis_speech, get_speaker_choices
from recorder import record_audio
from transcriber import transcribe_audio
import threading
import os
from config_dialog import ConfigDialog, show_config_dialog
from ui_parts import create_model_dropdown, create_speaker_dropdown

CONFIG_WINDOW_SIZE = "400x500"
WINDOW_SIZE = "500x700"
DROPDOWN_WIDTH = 30


# --- 音声AIアシスタント本体ウィンドウ ---
def show_main_window(
    config,
    get_scenario_list=None,
    load_scenario_content=None,
    get_character_list=None,
    load_character_content=None,
    root=None,
):
    from assistant_window import show_main_window as real_show_main_window

    return real_show_main_window(
        config,
        get_scenario_list=get_scenario_list,
        load_scenario_content=load_scenario_content,
        get_character_list=get_character_list,
        load_character_content=load_character_content,
        root=root,
    )


def run_gui(
    get_scenario_list, load_scenario_content, get_character_list, load_character_content
):
    from chat import get_model_list
    from speaker import get_speaker_choices

    # --- 設定ダイアログのみを最初に表示 ---
    model_list = get_model_list()
    speaker_choices = get_speaker_choices()
    character_files = get_character_list()
    scenario_files = get_scenario_list()

    config = show_config_dialog(
        model_list,
        speaker_choices,
        character_files,
        scenario_files,
        load_scenario_content,
        load_character_content,
    )
    if not config:
        return
    show_main_window(
        config,
        get_scenario_list,
        load_scenario_content,
        get_character_list,
        load_character_content,
    )
