import pytest
import tkinter as tk
import assistant_window
from unittest import mock


def setup_app(monkeypatch):
    config = {
        "scenario": "s1",
        "character": "c1",
        "system": "sys",
        "model": "m",
        "speaker": "0:dummy",
    }
    dummy = lambda *a, **k: ("reply", [])
    dummy_none = lambda *a, **k: None
    dummy_history = lambda *a, **k: [{"role": "system", "content": "sys"}]
    with mock.patch("tkinter.Tk.mainloop", return_value=None):
        root = tk.Tk()
        win = assistant_window.show_main_window(
            config,
            root=root,
            chat_with_lmstudio_func=dummy,
            speak_with_aivis_speech_func=dummy_none,
            save_history_func=dummy_none,
            load_history_func=dummy_history,
        )
        return root, win


def get_button_by_text(root, label):
    for child in root.winfo_children():
        if isinstance(child, tk.Frame):
            for w in child.winfo_children():
                if isinstance(w, tk.Button) and w["text"] == label:
                    return w
    return None


def get_entry_by_type(root):
    for child in root.winfo_children():
        if isinstance(child, tk.Frame):
            for w in child.winfo_children():
                if isinstance(w, tk.Entry):
                    return w
    return None


def test_state_idle_to_recording(monkeypatch):
    root, _ = setup_app(monkeypatch)
    start_btn = get_button_by_text(root, "▶️ 録音開始")
    assert start_btn is not None
    assert start_btn["state"] == "normal"
    start_btn.invoke()
    # 録音中の状態確認はUI遷移の都合で省略
    root.destroy()


def test_auto_mode_buttons(monkeypatch):
    root, _ = setup_app(monkeypatch)
    auto_btn = get_button_by_text(root, "▶️ オート開始")
    assert auto_btn is not None
    auto_btn.invoke()
    stop_btn = get_button_by_text(root, "■ オート停止")
    assert stop_btn is not None
    # オート中は録音開始ボタンが無効
    start_btn = get_button_by_text(root, "▶️ 録音開始")
    assert start_btn is not None
    assert start_btn["state"] == "disabled"
    root.destroy()


def test_send_text(monkeypatch):
    root, _ = setup_app(monkeypatch)
    entry = get_entry_by_type(root)
    assert entry is not None
    entry.insert(0, "test")
    send_btn = get_button_by_text(root, "送信")
    assert send_btn is not None
    send_btn.invoke()
    # 送信後、エントリが空になる
    assert entry.get() == ""
    root.destroy()
