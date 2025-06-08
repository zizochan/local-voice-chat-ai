import pytest
import tkinter as tk
from assistant_window import show_main_window
from unittest import mock


def test_show_main_window_buttons(monkeypatch):
    # 下段ボタンフレームに履歴リセット・終了ボタンがあること
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
            root = tk.Tk()
            show_main_window(config, root=root)
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
