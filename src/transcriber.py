import os
import wave
import numpy as np
import warnings
from faster_whisper import WhisperModel

WAV_FILENAME = "tmp/input.wav"
MODEL_SIZE = "base"

# faster-whisperのRuntimeWarningを抑制
warnings.filterwarnings(
    "ignore", category=RuntimeWarning, module="faster_whisper.feature_extractor"
)


def is_almost_silent(filename: str) -> bool:
    try:
        with wave.open(filename, "rb") as wf:
            n_frames = wf.getnframes()
            if n_frames < 1000:
                return True
            frames = wf.readframes(n_frames)
            audio = np.frombuffer(frames, dtype=np.int16)
            if audio.size == 0:
                return True
            rms = np.sqrt(np.mean(audio.astype(np.float64) ** 2))
            if rms < 10:
                return True
            return False
    except Exception as e:
        print(f"⚠️ WAVファイル検証エラー: {e}")
        return True


def transcribe_audio(filename: str = WAV_FILENAME) -> str:
    """Whisperで音声ファイルを文字起こしし、テキストを返す。無音時は空文字を返す"""
    print("🧠 Whisperで文字起こし中...")
    if (
        not os.path.exists(filename)
        or os.path.getsize(filename) < 1024
        or is_almost_silent(filename)
    ):
        # ユーザーに伝えるために例外を投げる
        raise RuntimeError("音声が認識できませんでした。もう一度録音してください。")
    model = WhisperModel(MODEL_SIZE, compute_type="int8")
    segments, _ = model.transcribe(filename, beam_size=5, language="ja")
    full_text = "".join([seg.text for seg in segments])
    print("📝 認識結果:", full_text)
    if not full_text.strip():
        raise RuntimeError("音声が認識できませんでした。もう一度録音してください。")
    return full_text
