import pytest
import tkinter as tk
from config_dialog import ConfigDialog


def test_config_dialog_buttons():
    # 正常なリストを渡した場合、開始・終了ボタンが存在すること
    dialog = ConfigDialog(
        model_list=["m1"],
        speaker_choices=["0:dummy"],
        character_files=["c1"],
        scenario_files=["s1"],
        load_scenario_content=lambda x: "scen",
        load_character_content=lambda x: "char",
    )
    # ボタンのテキストを取得
    btn_texts = [w["text"] for w in dialog.winfo_children() if isinstance(w, tk.Button)]
    assert "開始" in btn_texts
    assert "終了" in btn_texts
    dialog.destroy()


def test_config_dialog_exit(monkeypatch):
    # on_exitでos._exit(0)が呼ばれることを確認（SystemExit例外でテスト）
    dialog = ConfigDialog(
        model_list=["m1"],
        speaker_choices=["0:dummy"],
        character_files=["c1"],
        scenario_files=["s1"],
        load_scenario_content=lambda x: "scen",
        load_character_content=lambda x: "char",
    )
    called = {}

    def fake_exit(code):
        called["exit"] = code
        raise SystemExit

    monkeypatch.setattr("os._exit", fake_exit)
    with pytest.raises(SystemExit):
        dialog.on_exit()
    assert called["exit"] == 0
