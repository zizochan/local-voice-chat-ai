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
    # on_exitでsys.exit(0)が呼ばれることを確認（SystemExit例外でテスト）
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

    monkeypatch.setattr("sys.exit", fake_exit)
    with pytest.raises(SystemExit):
        dialog.on_exit()
    assert called["exit"] == 0


def test_config_dialog_result_has_system(monkeypatch):
    # ConfigDialogのresultにはsystemキーが必ず含まれる
    from config_dialog import ConfigDialog

    dialog = ConfigDialog(
        model_list=["m1"],
        speaker_choices=["0:dummy"],
        character_files=["c1"],
        scenario_files=["s1"],
        load_scenario_content=lambda x: "scen",
        load_character_content=lambda x: "char",
    )
    dialog.character_var.set("c1")
    dialog.scenario_var.set("s1")
    dialog.model_var.set("m1")
    dialog.speaker_var.set("0:dummy")
    dialog.system_entry.delete("1.0", "end")
    dialog.system_entry.insert("1.0", "test system")
    dialog.on_ok()
    assert "system" in dialog.result
    assert dialog.result["system"] == "test system"
