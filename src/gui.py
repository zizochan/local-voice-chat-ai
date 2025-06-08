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

CONFIG_WINDOW_SIZE = "400x500"
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


# --- 設定ダイアログ ---
class ConfigDialog(tk.Tk):
    def __init__(
        self,
        model_list,
        speaker_choices,
        character_files,
        scenario_files,
        load_scenario_content,
        load_character_content,
    ):
        super().__init__()
        self.title("設定")
        self.geometry(CONFIG_WINDOW_SIZE)
        self.resizable(False, False)
        self.result = None
        self.protocol("WM_DELETE_WINDOW", self.on_cancel)
        self.load_scenario_content = load_scenario_content
        self.load_character_content = load_character_content
        self.character_files = character_files
        self.scenario_files = scenario_files

        # キャラクター
        tk.Label(self, text="キャラクター選択").pack(pady=(10, 0))
        self.character_var = tk.StringVar()
        self.character_combobox = ttk.Combobox(
            self, textvariable=self.character_var, state="readonly", width=30
        )
        self.character_combobox["values"] = character_files
        if character_files:
            self.character_combobox.current(0)
        self.character_combobox.pack()
        self.character_combobox.bind("<<ComboboxSelected>>", self.update_system_prompt)

        # シナリオ
        tk.Label(self, text="シナリオ選択").pack(pady=(10, 0))
        self.scenario_var = tk.StringVar()
        self.scenario_combobox = ttk.Combobox(
            self, textvariable=self.scenario_var, state="readonly", width=30
        )
        self.scenario_combobox["values"] = scenario_files
        if scenario_files:
            self.scenario_combobox.current(0)
        self.scenario_combobox.pack()
        self.scenario_combobox.bind("<<ComboboxSelected>>", self.update_system_prompt)

        # モデル
        tk.Label(self, text="モデル選択").pack(pady=(10, 0))
        self.model_var = tk.StringVar()
        model_values = model_list if model_list else ["(取得失敗)"]
        self.model_combobox = ttk.Combobox(
            self, textvariable=self.model_var, state="readonly", width=30
        )
        self.model_combobox["values"] = model_values
        self.model_combobox.current(0)
        self.model_combobox.pack()

        # ボイス
        tk.Label(self, text="ボイス選択").pack(pady=(10, 0))
        self.speaker_var = tk.StringVar()
        speaker_values = speaker_choices if speaker_choices else ["(取得失敗)"]
        self.speaker_combobox = ttk.Combobox(
            self, textvariable=self.speaker_var, state="readonly", width=30
        )
        self.speaker_combobox["values"] = speaker_values
        self.speaker_combobox.current(0)
        self.speaker_combobox.pack()

        # システムプロンプト
        tk.Label(self, text="システムプロンプト").pack(pady=(10, 0))
        self.system_entry = tk.Text(self, height=7, width=50)
        self.system_entry.pack()

        # エラー時のメッセージ表示
        error_msgs = []
        if model_values == ["(取得失敗)"]:
            error_msgs.append("⚠️ LM Studioに接続できません（モデル一覧取得失敗）")
        if speaker_values == ["(取得失敗)"]:
            error_msgs.append("⚠️ Aivis Speechに接続できません（ボイス一覧取得失敗）")
        if error_msgs:
            self.set_system_prompt("\n".join(error_msgs))
        else:
            self.update_system_prompt()

        # 開始ボタン（self.start_button）をここで生成
        self.start_button = tk.Button(self, text="開始", command=self.on_ok)
        self.start_button.pack(pady=(10, 10))
        self.check_services()

    def check_services(self):
        # サービス未接続時は開始ボタンを無効化
        model_ng = self.model_combobox.get() == "(取得失敗)" or self.model_combobox[
            "values"
        ] == ("(取得失敗)",)
        speaker_ng = (
            self.speaker_combobox.get() == "(取得失敗)"
            or self.speaker_combobox["values"] == ("(取得失敗)",)
        )
        if model_ng or speaker_ng:
            self.start_button.config(state="disabled")
            if model_ng:
                self.model_combobox.config(foreground="red")
            if speaker_ng:
                self.speaker_combobox.config(foreground="red")
        else:
            self.start_button.config(state="normal")
            self.model_combobox.config(foreground="black")
            self.speaker_combobox.config(foreground="black")

    def set_system_prompt(self, prompt):
        self.system_entry.delete("1.0", "end")
        self.system_entry.insert("1.0", prompt)

    def update_system_prompt(self, event=None):
        scenario_content = ""
        character_content = ""
        scenario = (
            self.scenario_var.get()
            if self.scenario_var.get()
            else (self.scenario_files[0] if self.scenario_files else "")
        )
        character = (
            self.character_var.get()
            if self.character_var.get()
            else (self.character_files[0] if self.character_files else "")
        )
        if scenario:
            try:
                scenario_content = self.load_scenario_content(scenario)
            except Exception:
                pass
        if character:
            try:
                character_content = self.load_character_content(character)
            except Exception:
                pass
        prompt = (
            scenario_content
            + ("\n" if scenario_content and character_content else "")
            + character_content
        )
        self.set_system_prompt(prompt)

    def on_ok(self):
        self.result = {
            "model": self.model_var.get(),
            "speaker": self.speaker_var.get(),
            "character": self.character_var.get(),
            "scenario": self.scenario_var.get(),
            "system": self.system_entry.get("1.0", "end").strip(),
        }
        self.destroy()

    def on_cancel(self):
        self.result = None
        self.destroy()


# --- 音声AIアシスタント本体ウィンドウ ---
def show_main_window(
    config,
    get_scenario_list=None,
    load_scenario_content=None,
    get_character_list=None,
    load_character_content=None,
    root=None,
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
    messages = load_history(system_msg, scenario_filename, character_filename)

    # チャットログ
    tk.Label(root, text="チャットログ").pack()
    log_box = scrolledtext.ScrolledText(root, height=20)
    log_box.pack()

    def update_log_box():
        log_box.delete("1.0", "end")
        nonlocal messages
        if not messages:
            messages = load_history(system_msg, scenario_filename, character_filename)
        for msg in messages:
            if msg["role"] == "user":
                log_box.insert("end", f"👤 You: {msg['content']}\n")
            elif msg["role"] == "assistant":
                log_box.insert("end", f"🤖 AI: {msg['content']}\n\n")
            elif msg["role"] == "system":
                log_box.insert("end", f"[system] {msg['content']}\n")
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
        reply, messages = chat_with_lmstudio(text, messages, config["model"])
        log_box.insert("end", f"🤖 AI: {reply}\n\n")
        log_box.see("end")
        speaker_id = int(config["speaker"].split(":")[0])
        set_state("speaking")
        speak_with_aivis_speech(reply, speaker_id)
        save_history(messages, scenario_filename, character_filename)
        set_idle_state()
        update_log_box()

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
    stop_button = tk.Button(
        button_frame, text="⏹️ 停止", command=lambda: stop_listening()
    )
    stop_button.pack(side="left", padx=3)
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
        # 履歴をsystemメッセージで初期化
        messages = load_history(system_msg, scenario_filename, character_filename)
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
        # 履歴をsystemメッセージで初期化
        messages = load_history(system_msg, scenario_filename, character_filename)
        update_log_box()

    # ボタンフレーム
    button_frame = tk.Frame(root)
    button_frame.pack(pady=10)

    # 状態管理のバグ修正: set_stateでstart_buttonのtextを常に"▶️ 録音開始"に戻すようにし、
    # set_state("speaking")やset_state("processing")の後もstate="running"に戻すようにする
    def set_state(new_state):
        nonlocal state
        state = new_state
        if state == "idle":
            start_button.config(text="▶️ 録音開始", state="normal")
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
        # 状態を"running"に戻す（2回目以降の入力ができるように）
        nonlocal state
        state = "running"

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
            auto_speak()
            auto_button.config(text="■ オート停止", command=stop_auto_mode)

    def stop_auto_mode():
        nonlocal auto_mode, auto_timer
        if state != "running":
            return
        auto_mode = False
        if auto_timer:
            root.after_cancel(auto_timer)
            auto_timer = None
        auto_button.config(text="▶️ オート開始", command=start_auto_mode)
        set_idle_state()

    def auto_speak():
        nonlocal messages, auto_timer, auto_mode
        if not auto_mode or state != "idle":
            return
        set_state("auto")

        def worker():
            nonlocal messages
            text = "そのまま続けて"
            root.after(0, lambda: log_box.insert("end", f"🟢 Auto: {text}\n"))
            reply, messages_ = chat_with_lmstudio(text, messages, config["model"])
            messages = messages_
            root.after(0, lambda: log_box.insert("end", f"🤖 AI: {reply}\n\n"))
            root.after(0, log_box.see, "end")
            speaker_id = int(config["speaker"].split(":")[0])
            set_state("speaking")
            speak_with_aivis_speech(reply, speaker_id)
            save_history(messages, scenario_filename, character_filename)
            root.after(0, set_idle_state)
            if auto_mode:
                root.after(10000, auto_speak)

        threading.Thread(target=worker, daemon=True).start()

    def conversation_loop():
        nonlocal messages, is_listening
        if state != "running":
            return
        is_listening = True
        set_recording_state()
        speaker_id = int(config["speaker"].split(":")[0])
        if not messages:
            messages = load_history(system_msg, scenario_filename, character_filename)
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
            reply, messages = chat_with_lmstudio(text, messages, config["model"])
            root.after(0, lambda: log_box.insert("end", f"🤖 AI: {reply}\n\n"))
            root.after(0, log_box.see, "end")
            set_state("speaking")
            speak_with_aivis_speech(reply, speaker_id)
            save_history(messages, scenario_filename, character_filename)
            root.after(0, set_idle_state)
        set_idle_state()

    def on_exit():
        root.destroy()
        # 設定ダイアログに戻る
        if (
            get_scenario_list
            and load_scenario_content
            and get_character_list
            and load_character_content
        ):
            run_gui(
                get_scenario_list,
                load_scenario_content,
                get_character_list,
                load_character_content,
            )

    # 初期化
    state = "running"
    update_log_box()
    root.mainloop()
    return root


def run_gui(
    get_scenario_list, load_scenario_content, get_character_list, load_character_content
):
    # --- 設定ダイアログのみを最初に表示 ---
    model_list = get_model_list()
    speaker_choices = get_speaker_choices()
    character_files = get_character_list()
    scenario_files = get_scenario_list()

    config_dialog = ConfigDialog(
        model_list,
        speaker_choices,
        character_files,
        scenario_files,
        load_scenario_content,
        load_character_content,
    )
    config_dialog.mainloop()
    config = config_dialog.result
    if not config:
        return
    show_main_window(
        config,
        get_scenario_list,
        load_scenario_content,
        get_character_list,
        load_character_content,
    )
