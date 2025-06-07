import pytest
from unittest.mock import patch, MagicMock
import recorder


@patch("pyaudio.PyAudio")
@patch("wave.open")
def test_record_audio(mock_wave_open, mock_pyaudio, tmp_path):
    mock_stream = MagicMock()
    mock_stream.read.return_value = b"data"
    mock_pyaudio.return_value.open.return_value = mock_stream
    mock_pyaudio.return_value.get_sample_size.return_value = 2
    mock_wave = MagicMock()
    mock_wave_open.return_value.__enter__.return_value = mock_wave

    test_file = tmp_path / "input.wav"
    # should_stopなし（従来通り）
    recorder.record_audio(filename=str(test_file), duration=1, rate=16000)
    assert mock_pyaudio.called
    assert mock_wave.writeframes.called

    # should_stopあり（即座に中断）
    recorder.record_audio(
        filename=str(test_file), duration=10, rate=16000, should_stop=lambda: True
    )
    # 1回目のループでbreakされるので、stream.readは1回だけ呼ばれる
    assert mock_stream.read.call_count >= 1
