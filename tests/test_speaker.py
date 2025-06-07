import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

import pytest
from speaker import get_speaker_choices, speak_with_aivis_speech
from unittest.mock import patch, MagicMock


def test_get_speaker_choices_success(monkeypatch):
    # 正常系: モックで正常なリストを返す
    class MockResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return [{"name": "キャラA", "styles": [{"id": 1, "name": "ノーマル"}]}]

    monkeypatch.setattr("requests.get", lambda url: MockResponse())
    choices = get_speaker_choices()
    assert isinstance(choices, list)
    assert any("キャラA" in c for c in choices)


def test_get_speaker_choices_failure(monkeypatch):
    # 失敗時は(取得失敗)のみ返す
    def raise_exc(url):
        raise Exception("fail")

    monkeypatch.setattr("requests.get", raise_exc)
    choices = get_speaker_choices()
    assert choices == ["(取得失敗)"]


@patch("requests.post")
@patch("os.system")
def test_speak_with_aivis_speech_success(mock_system, mock_post, tmp_path):
    # audio_query
    mock_post.side_effect = [
        MagicMock(status_code=200, json=lambda: {"foo": "bar"}),
        MagicMock(status_code=200, content=b"WAVDATA"),
    ]
    with patch("builtins.open", new_callable=MagicMock()):
        speak_with_aivis_speech("テスト", 1)
    assert mock_post.call_count == 2
    assert mock_system.called


@patch("requests.post")
def test_speak_with_aivis_speech_audio_query_fail(mock_post):
    mock_post.return_value.status_code = 400
    mock_post.return_value.text = "error"
    speak_with_aivis_speech("テスト", 1)
    assert mock_post.call_count == 1


@patch("requests.post")
def test_speak_with_aivis_speech_synthesis_fail(mock_post):
    # audio_query success, synthesis fail
    mock_post.side_effect = [
        MagicMock(status_code=200, json=lambda: {"foo": "bar"}),
        MagicMock(status_code=400, text="error"),
    ]
    speak_with_aivis_speech("テスト", 1)
    assert mock_post.call_count == 2
