# transcriber.py

from faster_whisper import WhisperModel
from typing import Optional

WAV_FILENAME = "tmp/input.wav"
MODEL_SIZE = "base"


def transcribe_audio(filename: str = WAV_FILENAME) -> str:
    """Whisperで音声ファイルを文字起こしし、テキストを返す"""
    print("🧠 Whisperで文字起こし中...")
    model = WhisperModel(MODEL_SIZE, compute_type="int8")
    segments, _ = model.transcribe(filename, beam_size=5, language="ja")
    full_text = "".join([seg.text for seg in segments])
    print("📝 認識結果:", full_text)
    return full_text
