import tkinter as tk
from tkinter import ttk, scrolledtext
from recorder import record_audio
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


def create_speaker_dropdown(root, speaker_choices: List[str], width=DROPDOWN_WIDTH):
    tk.Label(root, text="ボイス選択").pack()
    speaker_var = tk.StringVar()
    speaker_dropdown = ttk.Combobox(root, textvariable=speaker_var, width=width)
    speaker_dropdown["values"] = speaker_choices
    speaker_dropdown.current(0)
    speaker_dropdown.pack()
    return speaker_dropdown, speaker_var


def create_model_dropdown(root, models: List[str], width=DROPDOWN_WIDTH):
    tk.Label(root, text="モデル選択").pack()
    model_var = tk.StringVar()
    model_combobox = ttk.Combobox(
        root, textvariable=model_var, state="readonly", width=width
    )
    model_combobox.pack()
    if models:
        model_combobox["values"] = models
        model_combobox.current(0)
    else:
        model_combobox["values"] = ["(取得失敗)"]
        model_combobox.current(0)
    return model_combobox, model_var


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


def run_gui():
    root = tk.Tk()
    root.title("音声AIアシスタント")
    root.geometry(WINDOW_SIZE)

    messages: List[Dict[str, Any]] = []
    is_listening = False
    auto_mode = False
    auto_timer = None
    state = "idle"  # idle, recording, processing, speaking, auto

    # キャラクター選択
    character_files = get_character_list()
    tk.Label(root, text="キャラクター選択").pack()
    character_var = tk.StringVar()
    character_combobox = ttk.Combobox(
        root, textvariable=character_var, state="readonly", width=DROPDOWN_WIDTH
    )
    character_combobox["values"] = character_files
    if character_files:
        character_combobox.current(0)
    character_combobox.pack()

    # シナリオ選択
    scenario_files = get_scenario_list()
    tk.Label(root, text="シナリオ選択").pack()
    scenario_var = tk.StringVar()
    scenario_combobox = ttk.Combobox(
        root, textvariable=scenario_var, state="readonly", width=DROPDOWN_WIDTH
    )
    scenario_combobox["values"] = scenario_files
    if scenario_files:
        scenario_combobox.current(0)
    scenario_combobox.pack()

    # モデル選択
    model_list = get_model_list()
    model_combobox, model_var = create_model_dropdown(
        root, model_list, width=DROPDOWN_WIDTH
    )

    # ボイス選択
    speaker_choices = get_speaker_choices()
    speaker_dropdown, speaker_var = create_speaker_dropdown(
        root, speaker_choices, width=DROPDOWN_WIDTH
    )

    def update_system_entry():
        scenario_content = ""
        character_content = ""
        if scenario_var.get():
            scenario_content = load_scenario_content(scenario_var.get())
        if character_var.get():
            character_content = load_character_content(character_var.get())
        system_entry.delete("1.0", "end")
        system_entry.insert(
            "1.0",
            scenario_content
            + ("\n" if scenario_content and character_content else "")
            + character_content,
        )
        # シナリオ・キャラクター変更時に履歴とチャットログも更新
        update_log_box()

    def update_log_box():
        log_box.delete("1.0", "end")
        scenario_filename = scenario_var.get() if scenario_var.get() else None
        character_filename = character_var.get() if character_var.get() else None
        system_msg = system_entry.get("1.0", "end").strip()
        # 最新のmessagesがあればそれを優先して表示
        nonlocal messages
        display_messages = messages if messages else None
        if not display_messages:
            try:
                display_messages = load_history(
                    system_msg, scenario_filename, character_filename
                )
            except Exception:
                display_messages = None
        if display_messages:
            for msg in display_messages:
                if msg["role"] == "user":
                    log_box.insert("end", f"👤 You: {msg['content']}\n")
                elif msg["role"] == "assistant":
                    log_box.insert("end", f"🤖 AI: {msg['content']}\n\n")
                elif msg["role"] == "system":
                    log_box.insert("end", f"[system] {msg['content']}\n")
            log_box.see("end")

    def on_scenario_select(event=None):
        update_system_entry()

    def on_character_select(event=None):
        update_system_entry()

    scenario_combobox.bind("<<ComboboxSelected>>", on_scenario_select)
    character_combobox.bind("<<ComboboxSelected>>", on_character_select)

    # システムプロンプト
    tk.Label(root, text="システムプロンプト").pack()
    system_entry = tk.Text(root, height=5)
    system_entry.pack()

    # チャットログ
    tk.Label(root, text="チャットログ").pack()
    log_box = scrolledtext.ScrolledText(root, height=15)
    log_box.pack()

    # 初期表示（ウィジェット生成後に呼ぶ）
    update_system_entry()
    update_log_box()

    # エラー検出とUI制御
    error_found = False
    if speaker_choices == ["(取得失敗)"]:
        log_box.insert("end", "⚠️ Aivis Speechに接続できません（ボイス一覧取得失敗）\n")
        error_found = True
    if model_list == [] or model_list == ["(取得失敗)"]:
        log_box.insert("end", "⚠️ LM Studioに接続できません（モデル一覧取得失敗）\n")
        error_found = True

    def set_state(new_state):
        nonlocal state
        state = new_state
        # UI制御
        if state == "idle":
            start_button.config(state="normal")
            auto_button.config(state="normal")
        elif state == "recording":
            start_button.config(text="● 録音中…", state="disabled")
            auto_button.config(state="disabled")
        elif state == "processing":
            start_button.config(text="AI処理中…", state="disabled")
            auto_button.config(state="disabled")
        elif state == "speaking":
            start_button.config(text="音声再生中…", state="disabled")
            auto_button.config(state="disabled")
        elif state == "auto":
            start_button.config(state="disabled")
            auto_button.config(text="■ オート停止", state="normal")

    def set_recording_state():
        set_state("recording")

    def set_processing_state():
        set_state("processing")

    def set_idle_state():
        set_state("idle")

    def auto_speak():
        nonlocal messages, auto_timer, auto_mode
        if not auto_mode or state != "idle":
            return
        set_state("auto")

        def worker():
            nonlocal messages
            text = "そのまま続けて"
            root.after(0, lambda: log_box.insert("end", f"🟢 Auto: {text}\n"))
            reply, messages_ = chat_with_lmstudio(text, messages, model_var.get())
            messages = messages_
            root.after(0, lambda: log_box.insert("end", f"🤖 AI: {reply}\n\n"))
            root.after(0, log_box.see, "end")
            speaker_id = int(speaker_var.get().split(":")[0])
            set_state("speaking")
            speak_with_aivis_speech(reply, speaker_id)
            save_history(messages, scenario_var.get(), character_var.get())
            root.after(0, set_idle_state)
            # 10秒後に再度実行
            if auto_mode:
                root.after(10000, auto_speak)

        threading.Thread(target=worker, daemon=True).start()

    def start_auto_mode():
        nonlocal auto_mode, auto_timer
        if not auto_mode:
            auto_mode = True
            auto_speak()
            auto_button.config(text="■ オート停止", command=stop_auto_mode)

    def stop_auto_mode():
        nonlocal auto_mode, auto_timer
        auto_mode = False
        if auto_timer:
            root.after_cancel(auto_timer)
            auto_timer = None
        auto_button.config(text="▶️ オート開始", command=start_auto_mode)
        set_idle_state()

    # チャットログの保存ファイル名をシナリオごとに分ける
    def conversation_loop():
        nonlocal messages, is_listening
        is_listening = True
        set_recording_state()
        speaker_id = int(speaker_var.get().split(":")[0])
        system_msg = system_entry.get("1.0", "end").strip()
        scenario_filename = scenario_var.get() if scenario_var.get() else None
        character_filename = character_var.get() if character_var.get() else None
        if not messages:
            messages = load_history(system_msg, scenario_filename, character_filename)
        while is_listening:
            set_state("recording")
            record_audio(should_stop=lambda: not is_listening)
            if not is_listening:
                break
            set_state("processing")
            try:
                text = transcribe_audio()
                root.after(0, lambda: log_box.insert("end", f"👤 You: {text}\n"))
            except RuntimeError as e:
                root.after(0, lambda: log_box.insert("end", f"⚠️ {str(e)}\n"))
                root.after(0, log_box.see, "end")
                set_recording_state()
                continue
            reply, messages = chat_with_lmstudio(text, messages, model_var.get())
            root.after(0, lambda: log_box.insert("end", f"🤖 AI: {reply}\n\n"))
            root.after(0, log_box.see, "end")
            set_state("speaking")
            speak_with_aivis_speech(reply, speaker_id)
            save_history(messages, scenario_filename, character_filename)
            set_idle_state()
        set_idle_state()

    def start_thread():
        threading.Thread(target=conversation_loop, daemon=True).start()

    def stop_listening():
        print("⏹️ 停止")
        nonlocal is_listening
        is_listening = False

    start_button = tk.Button(root, text="▶️ 録音開始", command=start_thread)
    start_button.pack(pady=10)
    stop_button = tk.Button(root, text="⏹️ 停止", command=stop_listening)
    stop_button.pack(pady=10)
    auto_button = tk.Button(root, text="▶️ オート開始", command=start_auto_mode)
    auto_button.pack(pady=10)

    if error_found:
        start_button.config(state="disabled")

    root.mainloop()


if __name__ == "__main__":
    run_gui()
