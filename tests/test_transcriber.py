import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from unittest.mock import patch, MagicMock
import transcriber


@patch("transcriber.is_almost_silent", return_value=False)
@patch("transcriber.WhisperModel")
def test_transcribe_audio(mock_model, mock_silent, tmp_path):
    mock_instance = mock_model.return_value
    mock_instance.transcribe.return_value = ([MagicMock(text="こんにちは。")], None)

    test_file = tmp_path / "input.wav"
    # 1024バイト以上のダミーWAVファイルを作成
    with open(test_file, "wb") as f:
        f.write(b"RIFF" + b"\x00" * 1024)
    result = transcriber.transcribe_audio(filename=str(test_file))
    assert "こんにちは" in result
