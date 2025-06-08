import pytest
from unittest.mock import patch, mock_open
import chat
import os

# load_history, save_history, query_lmstudio, get_model_list のテスト


def test_load_history_file_exists(monkeypatch):
    data = '[{"role": "user", "content": "hi"}]'
    monkeypatch.setattr("os.path.exists", lambda x: True)
    m = mock_open(read_data=data)
    with patch("builtins.open", m):
        messages = chat.load_history(
            "sys", "sample_scenario.txt", "sample_character.txt"
        )
        assert messages == [{"role": "user", "content": "hi"}]


def test_load_history_file_not_exists(monkeypatch):
    monkeypatch.setattr("os.path.exists", lambda x: False)
    messages = chat.load_history(
        "sysmsg", "sample_scenario.txt", "sample_character.txt"
    )
    assert messages == [{"role": "system", "content": "sysmsg"}]


def test_save_history(tmp_path):
    messages = [{"role": "user", "content": "hi"}]
    os.environ["TMP_DIR"] = str(tmp_path)
    try:
        chat.save_history(messages, "sample_scenario.txt", "sample_character.txt")
        file_path = tmp_path / "sample_scenario__sample_character.json"
        assert file_path.exists()
        with open(file_path, encoding="utf-8") as f:
            data = f.read()
        assert "hi" in data
    finally:
        del os.environ["TMP_DIR"]


@patch("requests.post")
def test_query_lmstudio_success(mock_post):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {
        "choices": [{"message": {"content": "AI reply"}}]
    }
    reply, messages = chat.query_lmstudio("text", [], "model")
    assert reply == "AI reply"


@patch("requests.post")
def test_query_lmstudio_error(mock_post):
    mock_post.side_effect = Exception("fail")
    reply, messages = chat.query_lmstudio("text", [], "model")
    assert reply == ""


@patch("requests.get")
def test_get_model_list_success(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "data": [
            {"id": "m1"},
            {"id": "text-embedding-ada-002"},
            {"id": "m2"},
            {"id": "text-embedding-foo"},
        ]
    }
    models = chat.get_model_list()
    # text-embeddingで始まるものは除外される
    assert models == ["m1", "m2"]


@patch("requests.get")
def test_get_model_list_error(mock_get):
    mock_get.side_effect = Exception("fail")
    models = chat.get_model_list()
    assert models == []


@patch("chat.query_lmstudio")
def test_chat_with_lmstudio(mock_query):
    # ユーザー発言追加→AI応答追加→履歴が正しくなるか
    mock_query.return_value = ("AI reply", [])
    messages = []
    reply, new_messages = chat.chat_with_lmstudio("こんにちは", messages, "model")
    assert reply == "AI reply"
    assert new_messages[0]["role"] == "user"
    assert new_messages[0]["content"] == "こんにちは"
    assert new_messages[1]["role"] == "assistant"
    assert new_messages[1]["content"] == "AI reply"
