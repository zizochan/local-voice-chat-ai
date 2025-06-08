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
    # 本物のAPIを絶対に呼ばないようにダミー関数を渡す
    dummy = lambda *a, **k: ("reply", [])
    dummy_none = lambda *a, **k: None
    with mock.patch("tkinter.Tk.mainloop", return_value=None):
        root = tk.Tk()
        show_main_window(
            config,
            root=root,
            chat_with_lmstudio_func=dummy,
            speak_with_aivis_speech_func=dummy_none,
            save_history_func=dummy_none,
            load_history_func=lambda *a, **k: [],
        )
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
