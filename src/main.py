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


def create_speaker_dropdown(root, speaker_choices: List[str]):
    tk.Label(root, text="話者 (speaker_id)").pack()
    speaker_var = tk.StringVar()
    speaker_dropdown = ttk.Combobox(root, textvariable=speaker_var)
    speaker_dropdown["values"] = speaker_choices
    speaker_dropdown.current(0)
    speaker_dropdown.pack()
    return speaker_dropdown, speaker_var


def create_model_dropdown(root, models: List[str]):
    tk.Label(root, text="モデル選択 (model_id)").pack()
    model_var = tk.StringVar()
    model_combobox = ttk.Combobox(root, textvariable=model_var, state="readonly")
    model_combobox.pack()
    if models:
        model_combobox["values"] = models
        model_combobox.current(0)
    else:
        model_combobox["values"] = ["(取得失敗)"]
        model_combobox.current(0)
    return model_combobox, model_var


def run_gui():
    root = tk.Tk()
    root.title("音声AIアシスタント")
    root.geometry("500x700")

    messages: List[Dict[str, Any]] = []
    is_listening = False

    speaker_choices = get_speaker_choices()
    speaker_dropdown, speaker_var = create_speaker_dropdown(root, speaker_choices)
    model_combobox, model_var = create_model_dropdown(root, get_model_list())

    tk.Label(root, text="会話の前提（systemメッセージ）").pack()
    system_entry = tk.Text(root, height=3)
    system_entry.insert("1.0", "あなたは親しみやすいAIアシスタントです。")
    system_entry.pack()

    tk.Label(root, text="チャットログ").pack()
    log_box = scrolledtext.ScrolledText(root, height=15)
    log_box.pack()

    def set_recording_state():
        start_button.config(text="● 録音中…", state="disabled")

    def set_processing_state():
        start_button.config(text="AI処理中…", state="disabled")

    def set_idle_state():
        start_button.config(text="▶️ 録音開始", state="normal")

    def conversation_loop():
        nonlocal messages, is_listening
        is_listening = True
        set_recording_state()
        speaker_id = int(speaker_var.get().split(":")[0])
        system_msg = system_entry.get("1.0", "end").strip()
        if not messages:
            messages = load_history(system_msg)
        while is_listening:
            record_audio(should_stop=lambda: not is_listening)
            if not is_listening:
                break  # 停止時はAI処理に進まず即座に抜ける
            set_processing_state()
            try:
                text = transcribe_audio()
                log_box.insert("end", f"👤 You: {text}\n")
            except RuntimeError as e:
                log_box.insert("end", f"⚠️ {str(e)}\n")
                log_box.see("end")
                set_recording_state()
                continue
            reply, messages = chat_with_lmstudio(text, messages, model_var.get())
            log_box.insert("end", f"🤖 AI: {reply}\n\n")
            log_box.see("end")
            speak_with_aivis_speech(reply, speaker_id)
            save_history(messages)
            set_recording_state()
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
    root.mainloop()


if __name__ == "__main__":
    run_gui()
