import tkinter as tk
from tkinter import scrolledtext
from typing import List, Dict, Any
from chat import load_history, save_history, chat_with_lmstudio
from speaker import speak_with_aivis_speech
from recorder import record_audio
from transcriber import transcribe_audio
import threading
import os

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
    auto_mode = False
    auto_timer = None
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

    # ボタンフレーム（上段: 録音・停止・オート）
    button_frame = tk.Frame(root)
    button_frame.pack(pady=10)

    start_button = tk.Button(
        button_frame, text="▶️ 録音開始", command=lambda: start_thread()
    )
    start_button.pack(side="left", padx=3)
    auto_button = tk.Button(
        button_frame, text="▶️ オート開始", command=lambda: start_auto_mode()
    )
    auto_button.pack(side="left", padx=3)

    def reset_history():
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

    # 下段ボタンフレーム（履歴リセット・終了）
    bottom_button_frame = tk.Frame(root)
    bottom_button_frame.pack(pady=(0, 10))
    reset_button = tk.Button(
        bottom_button_frame, text="🗑️ 履歴リセット", command=reset_history
    )
    reset_button.pack(side="left", padx=3)
    exit_button = tk.Button(bottom_button_frame, text="終了", command=lambda: on_exit())
    exit_button.pack(side="left", padx=3)

    # ボタン名（ラベル）を定数としてまとめる
    LABEL_START = "▶️ 録音開始"
    LABEL_STOP = "⏹️ 録音停止"
    LABEL_AUTO_START = "▶️ オート開始"
    LABEL_AUTO_STOP = "■ オート停止"
    LABEL_PROCESSING = "AI処理中…"
    LABEL_SPEAKING = "音声再生中…"

    def set_state(new_state):
        nonlocal state
        state = new_state
        if state == "idle" or state == "running":
            start_button.config(
                text=LABEL_START, state="normal", command=lambda: start_thread()
            )
            auto_button.config(
                text=LABEL_AUTO_START, state="normal", command=start_auto_mode
            )
            send_button.config(state="normal")
            text_entry.config(state="normal")
            reset_button.config(state="normal")
        elif state == "recording":
            start_button.config(
                text=LABEL_STOP, state="normal", command=lambda: stop_listening()
            )
            auto_button.config(state="disabled")
            send_button.config(state="normal")
            text_entry.config(state="normal")
            reset_button.config(state="normal")
        elif state == "processing":
            start_button.config(text=LABEL_PROCESSING, state="disabled")
            if auto_mode:
                auto_button.config(state="normal")
            else:
                auto_button.config(state="disabled")
            send_button.config(state="disabled")
            text_entry.config(state="disabled")
            reset_button.config(state="disabled")
        elif state == "speaking":
            start_button.config(text=LABEL_SPEAKING, state="disabled")
            if auto_mode:
                auto_button.config(state="normal")
            else:
                auto_button.config(state="disabled")
            send_button.config(state="disabled")
            text_entry.config(state="disabled")
            reset_button.config(state="disabled")
        elif state == "auto":
            start_button.config(state="disabled")
            auto_button.config(
                text=LABEL_AUTO_STOP, state="normal", command=stop_auto_mode
            )
            send_button.config(state="disabled")
            text_entry.config(state="disabled")
            reset_button.config(state="disabled")

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

    def start_auto_mode():
        nonlocal auto_mode, auto_timer
        if state != "running":
            return
        if not auto_mode:
            auto_mode = True
            set_state("auto")  # ここで即座にUIをオート状態に
            auto_speak()
            auto_button.config(text="■ オート停止", command=stop_auto_mode)

    def stop_auto_mode():
        nonlocal auto_mode, auto_timer
        auto_mode = False
        auto_button.config(state="disabled")

    def auto_speak():
        nonlocal messages, auto_timer, auto_mode
        if not auto_mode:
            return
        set_state("auto")

        def worker():
            nonlocal messages
            text = "そのまま続けて"
            root.after(0, lambda: log_box.insert("end", f"🟢 Auto: {text}\n"))
            reply, messages_ = chat_with_lmstudio_func(text, messages, config["model"])
            messages = messages_
            root.after(0, lambda: log_box.insert("end", f"🤖 AI: {reply}\n\n"))
            root.after(0, log_box.see, "end")
            speaker_id = int(config["speaker"].split(":")[0])
            set_state("speaking")
            speak_with_aivis_speech_func(reply, speaker_id)
            save_history_func(messages, scenario_filename, character_filename)
            # idleに戻さず、オート状態を維持
            if auto_mode:
                root.after(0, lambda: set_state("auto"))
                root.after(AUTO_INTERVAL_MS, auto_speak)
            else:
                root.after(0, set_idle_state)

        threading.Thread(target=worker, daemon=True).start()

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

    state = "running"
    update_log_box()
    root.mainloop()
    return root
