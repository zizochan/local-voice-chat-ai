import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

import pytest
from main import get_scenario_list, load_scenario_content
from chat import load_history, save_history
import json


def test_get_scenario_list():
    scenarios = get_scenario_list()
    assert isinstance(scenarios, list)
    assert any(s.endswith(".txt") for s in scenarios)
    assert "sample_scenario.txt" in scenarios


def test_load_scenario_content():
    content = load_scenario_content("sample_scenario.txt")
    assert "全力でユーザーのサポートして下さい。" in content


@pytest.mark.parametrize(
    "scenario_file",
    ["sample_scenario.txt"],
)
def test_scenario_content_not_empty(scenario_file):
    content = load_scenario_content(scenario_file)
    assert content.strip() != ""


def test_logfile_per_scenario(tmp_path):
    import os
    import json

    messages = [{"role": "system", "content": "テスト"}]
    scenario_filename = "sample_scenario.txt"
    character_filename = "sample_character.txt"
    log_file = f"{os.path.splitext(scenario_filename)[0]}__{os.path.splitext(character_filename)[0]}.json"
    log_path = tmp_path / log_file
    # TMP_DIR環境変数を一時的に上書き
    old_tmp = os.environ.get("TMP_DIR")
    os.environ["TMP_DIR"] = str(tmp_path)
    try:
        save_history(messages, scenario_filename, character_filename)
        assert log_path.exists()
        loaded = load_history("テスト", scenario_filename, character_filename)
        assert loaded[0]["content"] == "テスト"
    finally:
        if old_tmp is not None:
            os.environ["TMP_DIR"] = old_tmp
        else:
            del os.environ["TMP_DIR"]
