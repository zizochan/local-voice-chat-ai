import pytest
from unittest.mock import patch, mock_open
import chat

# load_history, save_history, query_lmstudio, get_model_list のテスト


def test_load_history_file_exists(monkeypatch):
    data = '[{"role": "user", "content": "hi"}]'
    monkeypatch.setattr("os.path.exists", lambda x: True)
    m = mock_open(read_data=data)
    with patch("builtins.open", m):
        messages = chat.load_history("sys")
        assert messages == [{"role": "user", "content": "hi"}]


def test_load_history_file_not_exists(monkeypatch):
    monkeypatch.setattr("os.path.exists", lambda x: False)
    messages = chat.load_history("sysmsg")
    assert messages == [{"role": "system", "content": "sysmsg"}]


def test_save_history(tmp_path):
    messages = [{"role": "user", "content": "hi"}]
    file_path = tmp_path / "messages.json"
    with patch("chat.HISTORY_FILE", str(file_path)):
        chat.save_history(messages)
        with open(file_path, encoding="utf-8") as f:
            assert "hi" in f.read()


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
    mock_get.return_value.json.return_value = {"data": [{"id": "m1"}, {"id": "m2"}]}
    models = chat.get_model_list()
    assert models == ["m1", "m2"]


@patch("requests.get")
def test_get_model_list_error(mock_get):
    mock_get.side_effect = Exception("fail")
    models = chat.get_model_list()
    assert models == []
