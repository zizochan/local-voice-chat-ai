import pytest
from unittest.mock import patch, MagicMock
import speaker


@patch("requests.get")
def test_get_speaker_choices_success(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = [
        {"name": "サンプルキャラクター", "styles": [{"id": 1, "name": "ノーマル"}]}
    ]
    choices = speaker.get_speaker_choices()
    assert choices == ["1: サンプルキャラクター（ノーマル）"]


@patch("requests.get")
def test_get_speaker_choices_error(mock_get):
    mock_get.side_effect = Exception("fail")
    choices = speaker.get_speaker_choices()
    assert choices == ["1: サンプルキャラクター"]


@patch("requests.post")
@patch("os.system")
def test_speak_with_aivis_speech_success(mock_system, mock_post, tmp_path):
    # audio_query
    mock_post.side_effect = [
        MagicMock(status_code=200, json=lambda: {"foo": "bar"}),
        MagicMock(status_code=200, content=b"WAVDATA"),
    ]
    with patch("builtins.open", new_callable=MagicMock()):
        speaker.speak_with_aivis_speech("テスト", 1)
    assert mock_post.call_count == 2
    assert mock_system.called


@patch("requests.post")
def test_speak_with_aivis_speech_audio_query_fail(mock_post):
    mock_post.return_value.status_code = 400
    mock_post.return_value.text = "error"
    speaker.speak_with_aivis_speech("テスト", 1)
    assert mock_post.call_count == 1


@patch("requests.post")
def test_speak_with_aivis_speech_synthesis_fail(mock_post):
    # audio_query success, synthesis fail
    mock_post.side_effect = [
        MagicMock(status_code=200, json=lambda: {"foo": "bar"}),
        MagicMock(status_code=400, text="error"),
    ]
    speaker.speak_with_aivis_speech("テスト", 1)
    assert mock_post.call_count == 2
