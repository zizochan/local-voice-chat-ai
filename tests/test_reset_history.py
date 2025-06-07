import os
import sys
import pytest
import importlib
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
import chat


def test_reset_history(tmp_path):
    # テスト用の履歴ファイルを作成
    scenario_filename = "sample_scenario.txt"
    character_filename = "sample_character.txt"
    log_file = f"{os.path.splitext(scenario_filename)[0]}__{os.path.splitext(character_filename)[0]}.json"
    log_path = tmp_path / log_file
    messages = [{"role": "user", "content": "hi"}]
    old_tmp = os.environ.get("TMP_DIR")
    os.environ["TMP_DIR"] = str(tmp_path)
    try:
        chat.save_history(messages, scenario_filename, character_filename)
        assert log_path.exists()
        # reset_history相当の処理
        log_path.unlink()  # ファイル削除
        assert not log_path.exists()
        # 削除後はload_historyでsystemメッセージのみ
        loaded = chat.load_history("sysmsg", scenario_filename, character_filename)
        assert loaded == [{"role": "system", "content": "sysmsg"}]
    finally:
        if old_tmp is not None:
            os.environ["TMP_DIR"] = old_tmp
        else:
            del os.environ["TMP_DIR"]
