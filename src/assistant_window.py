import tkinter as tk
from tkinter import scrolledtext
from tkinter import messagebox  # 追加
from typing import List, Dict, Any
from chat import load_history, save_history, chat_with_lmstudio
from speaker import speak_with_aivis_speech
from recorder import record_audio
from transcriber import transcribe_audio
import threading
import os
import random

WINDOW_SIZE = "500x700"
AUTO_INTERVAL_MS = 1000


def show_main_window(
    config,
    get_scenario_list=None,
    load_scenario_content=None,
    get_character_list=None,
    load_character_content=None,
    root=None,
    load_history_func=load_history,
    save_history_func=save_history,
    chat_with_lmstudio_func=chat_with_lmstudio,
    speak_with_aivis_speech_func=speak_with_aivis_speech,
):
    if root is None:
        root = tk.Tk()
    root.title("音声AIアシスタント")
    root.geometry(WINDOW_SIZE)

    messages: List[Dict[str, Any]] = []
    is_listening = False
    state = "init"

    scenario_filename = config["scenario"] if config["scenario"] else None
    character_filename = config["character"] if config["character"] else None
    system_msg = config["system"]
    messages = load_history_func(system_msg, scenario_filename, character_filename)

    # チャットログ
    tk.Label(root, text="チャットログ").pack()
    log_box = scrolledtext.ScrolledText(root, height=20)
    log_box.pack()

    def update_log_box():
        log_box.delete("1.0", "end")
        nonlocal messages
        if not messages:
            messages = load_history_func(
                system_msg, scenario_filename, character_filename
            )
        for msg in messages:
            if msg["role"] == "user":
                log_box.insert("end", f"👤 You: {msg['content']}\n")
            elif msg["role"] == "assistant":
                log_box.insert("end", f"🤖 AI: {msg['content']}\n\n")
            elif msg["role"] == "system":
                log_box.insert("end", f"[system] {msg['content']}\n\n")
        log_box.see("end")

    # テキスト入力欄と送信ボタン
    text_frame = tk.Frame(root)
    text_frame.pack(pady=5)
    text_entry = tk.Entry(text_frame, width=40)
    text_entry.pack(side="left", padx=(0, 5))

    def on_send_text(event=None):
        nonlocal messages
        if state != "running":
            return
        text = text_entry.get().strip()
        if not text:
            return
        text_entry.delete(0, "end")
        log_box.insert("end", f"👤 You: {text}\n")
        log_box.see("end")
        set_processing_state()

        def worker():
            nonlocal messages
            reply, messages_ = chat_with_lmstudio_func(text, messages, config["model"])
            messages = messages_
            speaker_id = int(config["speaker"].split(":")[0])

            def update_before_speech():
                log_box.insert("end", f"🤖 AI: {reply}\n\n")
                log_box.see("end")
                set_state("speaking")

                # 音声再生・履歴保存・状態遷移は別スレッドで
                def after_speech():
                    speak_with_aivis_speech_func(reply, speaker_id)
                    save_history_func(messages, scenario_filename, character_filename)
                    set_idle_state()
                    update_log_box()

                threading.Thread(target=after_speech, daemon=True).start()

            root.after(0, update_before_speech)

        threading.Thread(target=worker, daemon=True).start()

    send_button = tk.Button(text_frame, text="送信", command=on_send_text)
    send_button.pack(side="left")
    text_entry.bind("<Return>", on_send_text)

    # ボタンフレーム（上段: 録音・ランダム発言）より前にplay_random_speechを定義
    def play_random_speech():
        filename = selected_random_file.get()
        if filename == "（ファイルなし）" or not filename:
            log_box.insert("end", "⚠️ ランダム発言ファイルがありません\n")
            log_box.see("end")
            return
        random_file = os.path.join(random_speech_dir, filename)
        if not os.path.exists(random_file):
            log_box.insert("end", "⚠️ ランダム発言ファイルが見つかりません\n")
            log_box.see("end")
            refresh_random_files()
            return
        with open(random_file, encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
        if not lines:
            log_box.insert("end", "⚠️ ランダム発言が空です\n")
            log_box.see("end")
            return
        text = random.choice(lines)

        # on_send_textと同じ処理を呼び出す
        def send_random():
            nonlocal messages
            if state != "running":
                return
            log_box.insert("end", f"👤 You: {text}\n")
            log_box.see("end")
            set_processing_state()

            def worker():
                nonlocal messages
                reply, messages_ = chat_with_lmstudio_func(
                    text, messages, config["model"]
                )
                messages = messages_
                speaker_id = int(config["speaker"].split(":")[0])

                def update_before_speech():
                    log_box.insert("end", f"🤖 AI: {reply}\n\n")
                    log_box.see("end")
                    set_state("speaking")

                    def after_speech():
                        speak_with_aivis_speech_func(reply, speaker_id)
                        save_history_func(
                            messages, scenario_filename, character_filename
                        )
                        set_idle_state()
                        update_log_box()

                    threading.Thread(target=after_speech, daemon=True).start()

                root.after(0, update_before_speech)

            threading.Thread(target=worker, daemon=True).start()

        send_random()

    def reset_history():
        if not messagebox.askyesno("確認", "本当に履歴をリセットしますか？"):
            return
        nonlocal messages
        log_dir = os.environ.get("TMP_DIR") or os.path.join(
            os.path.dirname(__file__), "../tmp"
        )
        try:
            from chat import make_log_path

            log_path = make_log_path(log_dir, scenario_filename, character_filename)
            if os.path.exists(log_path):
                os.remove(log_path)
        except Exception:
            pass
        messages = load_history_func(system_msg, scenario_filename, character_filename)
        update_log_box()

    # ボタンフレーム（録音・履歴リセット・終了を1行で並べる）
    button_frame = tk.Frame(root)
    button_frame.pack(pady=10)

    start_button = tk.Button(
        button_frame, text="▶️ 録音開始", command=lambda: start_thread()
    )
    start_button.pack(side="left", padx=3)
    reset_button = tk.Button(button_frame, text="🗑️ 履歴リセット", command=reset_history)
    reset_button.pack(side="left", padx=3)
    exit_button = tk.Button(button_frame, text="終了", command=lambda: on_exit())
    exit_button.pack(side="left", padx=3)

    # ボタン名（ラベル）を定数としてまとめる
    LABEL_START = "▶️ 録音開始"
    LABEL_STOP = "⏹️ 録音停止"
    LABEL_PROCESSING = "AI処理中…"
    LABEL_SPEAKING = "音声再生中…"

    def set_state(new_state):
        nonlocal state
        state = new_state
        if state == "idle" or state == "running":
            start_button.config(
                text=LABEL_START, state="normal", command=lambda: start_thread()
            )
            send_button.config(state="normal")
            text_entry.config(state="normal")
            reset_button.config(state="normal")
            if get_random_files() == ["（ファイルなし）"]:
                random_button.config(state="disabled")
            else:
                random_button.config(state="normal")
        elif state == "recording":
            start_button.config(
                text=LABEL_STOP, state="normal", command=lambda: stop_listening()
            )
            send_button.config(state="normal")
            text_entry.config(state="normal")
            reset_button.config(state="normal")
            random_button.config(state="disabled")
        elif state == "processing":
            start_button.config(text=LABEL_PROCESSING, state="disabled")
            send_button.config(state="disabled")
            text_entry.config(state="disabled")
            reset_button.config(state="disabled")
            random_button.config(state="disabled")
        elif state == "speaking":
            start_button.config(text=LABEL_SPEAKING, state="disabled")
            send_button.config(state="disabled")
            text_entry.config(state="disabled")
            reset_button.config(state="disabled")
            random_button.config(state="disabled")

    def set_recording_state():
        set_state("recording")

    def set_processing_state():
        set_state("processing")

    def set_idle_state():
        set_state("idle")
        nonlocal state
        state = "running"  # idle表示だが、次のユーザー操作を受け付けるため内部状態はrunningに

    def start_thread():
        if state != "running":
            return
        threading.Thread(target=conversation_loop, daemon=True).start()

    def stop_listening():
        nonlocal is_listening
        is_listening = False

    def conversation_loop():
        nonlocal messages, is_listening
        if state != "running":
            return
        is_listening = True
        set_recording_state()
        speaker_id = int(config["speaker"].split(":")[0])
        if not messages:
            messages = load_history_func(
                system_msg, scenario_filename, character_filename
            )
        while is_listening and state == "recording":
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
            reply, messages = chat_with_lmstudio_func(text, messages, config["model"])
            root.after(0, lambda: log_box.insert("end", f"🤖 AI: {reply}\n\n"))
            root.after(0, log_box.see, "end")
            set_state("speaking")
            speak_with_aivis_speech_func(reply, speaker_id)
            save_history_func(messages, scenario_filename, character_filename)
            root.after(0, set_idle_state)
        set_idle_state()

    def on_exit():
        # GUIの破棄は必ずメインスレッドで行う
        if root:
            root.after(0, root.destroy)
        if (
            get_scenario_list
            and load_scenario_content
            and get_character_list
            and load_character_content
        ):
            from gui import run_gui

            def rerun():
                run_gui(
                    get_scenario_list,
                    load_scenario_content,
                    get_character_list,
                    load_character_content,
                )

            root.after(0, rerun)

    # --- ランダム発言ファイル選択UIの追加 ---
    random_speech_dir = os.path.join(os.path.dirname(__file__), "../random_speech")
    if not os.path.exists(random_speech_dir):
        os.makedirs(random_speech_dir)

    def get_random_files():
        files = [f for f in os.listdir(random_speech_dir) if f.endswith(".txt")]
        return files if files else ["（ファイルなし）"]

    random_files = get_random_files()
    selected_random_file = tk.StringVar(value=random_files[0])

    random_frame = tk.Frame(root)
    random_frame.pack(pady=8)
    random_menu = tk.OptionMenu(random_frame, selected_random_file, *random_files)
    random_menu.pack(side="left", padx=2)
    random_button = tk.Button(
        random_frame, text="🎲 ランダム発言", command=lambda: play_random_speech()
    )
    random_button.pack(side="left", padx=2)

    def refresh_random_files():
        files = get_random_files()
        menu = random_menu["menu"]
        menu.delete(0, "end")
        for f in files:
            menu.add_command(
                label=f, command=lambda value=f: selected_random_file.set(value)
            )
        selected_random_file.set(files[0])
        if files == ["（ファイルなし）"]:
            random_button.config(state="disabled")
        else:
            random_button.config(state="normal")

    # 初期化時にランダム発言ファイルがなければボタン無効化
    if random_files == ["（ファイルなし）"]:
        random_button.config(state="disabled")

    state = "running"
    update_log_box()
    root.mainloop()
    return root
