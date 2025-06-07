import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

import pytest
from main import (
    get_character_list,
    load_character_content,
    get_scenario_list,
    load_scenario_content,
)
from chat import load_history, save_history


def test_get_character_list():
    characters = get_character_list()
    assert isinstance(characters, list)
    assert any(c.endswith(".txt") for c in characters)
    assert "sample_character.txt" in characters


def test_load_character_content():
    content = load_character_content("sample_character.txt")
    assert "AIアシスタント" in content


@pytest.mark.parametrize(
    "character_file",
    [
        "sample_character.txt",
    ],
)
def test_character_content_not_empty(character_file):
    content = load_character_content(character_file)
    assert content.strip() != ""


def test_logfile_per_scenario_character(tmp_path):
    messages = [{"role": "system", "content": "テスト"}]
    scenario_filename = "sample_scenario.txt"
    character_filename = "sample_character.txt"
    log_file = f"{os.path.splitext(scenario_filename)[0]}__{os.path.splitext(character_filename)[0]}.json"
    log_path = tmp_path / log_file
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
