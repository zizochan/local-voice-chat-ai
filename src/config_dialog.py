import tkinter as tk
from tkinter import ttk
from typing import List
from ui_parts import create_model_dropdown, create_speaker_dropdown

CONFIG_WINDOW_SIZE = "400x500"
DROPDOWN_WIDTH = 30


class ConfigDialog(tk.Tk):
    def __init__(
        self,
        model_list,
        speaker_choices,
        character_files,
        scenario_files,
        load_scenario_content,
        load_character_content,
        initial=None,
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
        initial = initial or {}

        # キャラクター
        tk.Label(self, text="キャラクター選択").pack()
        self.character_var = tk.StringVar()
        self.character_combobox = ttk.Combobox(
            self, textvariable=self.character_var, state="readonly", width=30
        )
        self.character_combobox["values"] = character_files
        if character_files:
            idx = (
                character_files.index(initial.get("character"))
                if initial.get("character") in character_files
                else 0
            )
            self.character_combobox.current(idx)
        self.character_combobox.pack()
        self.character_combobox.bind("<<ComboboxSelected>>", self.update_system_prompt)

        # シナリオ
        tk.Label(self, text="シナリオ選択").pack()
        self.scenario_var = tk.StringVar()
        self.scenario_combobox = ttk.Combobox(
            self, textvariable=self.scenario_var, state="readonly", width=30
        )
        self.scenario_combobox["values"] = scenario_files
        if scenario_files:
            idx = (
                scenario_files.index(initial.get("scenario"))
                if initial.get("scenario") in scenario_files
                else 0
            )
            self.scenario_combobox.current(idx)
        self.scenario_combobox.pack()
        self.scenario_combobox.bind("<<ComboboxSelected>>", self.update_system_prompt)

        # モデル
        model_combobox, self.model_var = create_model_dropdown(
            self, model_list, width=30
        )
        self.model_combobox = model_combobox
        model_values = model_list if model_list else ["(取得失敗)"]
        if model_list:
            idx = (
                model_list.index(initial.get("model"))
                if initial.get("model") in model_list
                else 0
            )
            self.model_combobox.current(idx)

        # ボイス
        speaker_combobox, self.speaker_var = create_speaker_dropdown(
            self, speaker_choices, width=30
        )
        self.speaker_combobox = speaker_combobox
        speaker_values = speaker_choices if speaker_choices else ["(取得失敗)"]
        if speaker_choices:
            idx = (
                speaker_choices.index(initial.get("speaker"))
                if initial.get("speaker") in speaker_choices
                else 0
            )
            self.speaker_combobox.current(idx)

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

        # 開始ボタン
        self.start_button = tk.Button(self, text="開始", command=self.on_ok)
        self.start_button.pack(pady=(10, 2))
        # 終了ボタン
        self.exit_button = tk.Button(self, text="終了", command=self.on_exit)
        self.exit_button.pack(pady=(0, 10))
        self.check_services()

    def check_services(self):
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
            "### シナリオ ###\n"
            + scenario_content
            + "\n\n"
            + "### キャラクター設定 ###\n"
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

    def on_exit(self):
        self.destroy()
        import sys

        sys.exit(0)  # os._exit(0) は強制終了なので使わない


def show_config_dialog(
    model_list,
    speaker_choices,
    character_files,
    scenario_files,
    load_scenario_content,
    load_character_content,
    initial=None,
):
    dialog = ConfigDialog(
        model_list,
        speaker_choices,
        character_files,
        scenario_files,
        load_scenario_content,
        load_character_content,
        initial,
    )
    dialog.mainloop()
    return dialog.result
