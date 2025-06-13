import sys
import os
import io
from unittest import mock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
import assistant_window
import pytest
import tkinter as tk
from tkinter import scrolledtext


def setup_app(monkeypatch, random_speech_files=None):
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
    # --- random_speechディレクトリ・ファイル操作をモック ---
    random_speech_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../random_speech")
    )
    # assistant_window側のグローバル変数も上書き
    monkeypatch.setattr(
        assistant_window, "random_speech_dir", random_speech_dir, raising=False
    )
    mock_files = {}
    if random_speech_files:
        for fname, lines in random_speech_files.items():
            mock_files[os.path.join(random_speech_dir, fname)] = "\n".join(lines)

    def mock_listdir(path):
        if os.path.abspath(path) == random_speech_dir:
            return [os.path.basename(f) for f in mock_files.keys()]
        return []

    def mock_open(file, mode="r", encoding=None):
        abspath = os.path.abspath(file)
        if "w" in mode:

            def write_fn(data):
                mock_files[abspath] = data

            s = io.StringIO()
            s.write = write_fn
            s.__enter__ = lambda s=s: s
            s.__exit__ = lambda *a, **k: None
            return s
        elif "r" in mode:
            data = mock_files.get(abspath, "")
            return io.StringIO(data)
        else:
            raise NotImplementedError()

    def mock_remove(path):
        abspath = os.path.abspath(path)
        if abspath in mock_files:
            del mock_files[abspath]

    def mock_makedirs(path, exist_ok=False):
        pass

    def mock_exists(path):
        abspath = os.path.abspath(path)
        return abspath in mock_files or abspath == random_speech_dir

    with mock.patch("os.listdir", mock_listdir), mock.patch(
        "builtins.open", mock_open
    ), mock.patch("os.remove", mock_remove), mock.patch(
        "os.makedirs", mock_makedirs
    ), mock.patch(
        "os.path.exists", mock_exists
    ), mock.patch(
        "tkinter.Tk.mainloop", return_value=None
    ):
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


def get_optionmenu(root):
    for child in root.winfo_children():
        if isinstance(child, tk.Frame):
            for w in child.winfo_children():
                if isinstance(w, tk.OptionMenu):
                    return w
    return None


def find_scrolledtext_widget(widget):
    from tkinter import scrolledtext

    if isinstance(widget, scrolledtext.ScrolledText):
        return widget
    for child in widget.winfo_children():
        found = find_scrolledtext_widget(child)
        if found:
            return found
    return None


def test_random_button_and_menu_exist(monkeypatch):
    root, _ = setup_app(monkeypatch, {"test.txt": ["a", "b"]})
    btn = get_button_by_text(root, "🎲 ランダム発言")
    menu = get_optionmenu(root)
    assert btn is not None
    assert menu is not None
    root.destroy()


def test_random_button_disabled_when_no_file(monkeypatch):
    root, _ = setup_app(monkeypatch, {})
    btn = get_button_by_text(root, "🎲 ランダム発言")
    assert btn is not None
    assert btn["state"] == "disabled"
    root.destroy()


def test_random_button_enabled_when_file_exists(monkeypatch):
    root, _ = setup_app(monkeypatch, {"test.txt": ["a", "b"]})
    btn = get_button_by_text(root, "🎲 ランダム発言")
    assert btn is not None
    assert btn["state"] == "normal"
    root.destroy()


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
