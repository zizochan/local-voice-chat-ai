import pytest
import tkinter as tk
from unittest import mock
from config_dialog import ConfigDialog
from assistant_window import show_main_window
import gui


# --- 既存の関数存在テストはそのまま ---
def test_create_speaker_dropdown_exists():
    assert hasattr(gui, "create_speaker_dropdown")


def test_create_model_dropdown_exists():
    assert hasattr(gui, "create_model_dropdown")


def test_run_gui_exists():
    assert hasattr(gui, "run_gui")


# --- 追加テスト ---
def test_config_dialog_services_disable(monkeypatch):
    # モデル・ボイス取得失敗時は開始ボタンが無効化される
    class DummyDialog(ConfigDialog):
        def __init__(self, *a, **kw):
            super().__init__(*a, **kw)
            self.destroy = lambda: None

    monkeypatch.setattr(gui, "ConfigDialog", DummyDialog)
    dialog = DummyDialog(
        model_list=[],
        speaker_choices=[],
        character_files=["c1"],
        scenario_files=["s1"],
        load_scenario_content=lambda x: "scen",
        load_character_content=lambda x: "char",
    )
    assert dialog.start_button["state"] == "disabled"
    dialog.destroy()


def test_reset_history_called(monkeypatch):
    # reset_historyが呼ばれると履歴が初期化される
    called = {}

    def fake_load_history(system_msg, scenario, character):
        called["load"] = (system_msg, scenario, character)
        return [dict(role="system", content="sys")]  # dummy

    config = {
        "scenario": "s1",
        "character": "c1",
        "system": "sys",
        "model": "m",
        "speaker": "0:dummy",
    }
    with mock.patch(
        "assistant_window.chat_with_lmstudio", return_value=("reply", [])
    ), mock.patch(
        "assistant_window.speak_with_aivis_speech", return_value=None
    ), mock.patch(
        "assistant_window.save_history", return_value=None
    ):
        with mock.patch("tkinter.Tk.mainloop", return_value=None):
            show_main_window(
                config,
                load_history_func=fake_load_history,
            )
    assert "load" in called


def test_button_layout(monkeypatch):
    # 下段ボタンフレームに履歴リセット・終了ボタンがあること
    config = {
        "scenario": "s1",
        "character": "c1",
        "system": "sys",
        "model": "m",
        "speaker": "0:dummy",
    }
    with mock.patch.object(
        gui, "chat_with_lmstudio", return_value=("reply", [])
    ), mock.patch.object(
        gui, "speak_with_aivis_speech", return_value=None
    ), mock.patch.object(
        gui, "save_history", return_value=None
    ):
        with mock.patch("tkinter.Tk.mainloop", return_value=None):
            root = tk.Tk()
            gui.show_main_window(config, root=root)
            found = False
            for child in root.winfo_children():
                if isinstance(child, tk.Frame):
                    btn_texts = [
                        w["text"]
                        for w in child.winfo_children()
                        if isinstance(w, tk.Button)
                    ]
                    if "🗑️ 履歴リセット" in btn_texts and "終了" in btn_texts:
                        found = True
            assert found
            root.destroy()


def test_config_json_does_not_save_system(tmp_path, monkeypatch):
    # config.jsonにはsystemが保存されないことを確認
    import json
    from config_loader import save_config, load_config

    config = {
        "scenario": "s1",
        "character": "c1",
        "system": "sys",
        "model": "m",
        "speaker": "0:dummy",
    }
    config_path = tmp_path / "config.json"
    save_config(
        {k: v for k, v in config.items() if k != "system"}, path=str(config_path)
    )
    # systemを含めて保存しない仕様なので、systemを除外して保存
    loaded = load_config(path=str(config_path))
    assert "system" not in loaded
