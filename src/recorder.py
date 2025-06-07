import pyaudio
import wave
from typing import Optional

WAV_FILENAME = "tmp/input.wav"
RECORD_SECONDS = 5
RATE = 16000


def record_audio(
    filename: str = WAV_FILENAME,
    duration: int = RECORD_SECONDS,
    rate: int = RATE,
    should_stop: Optional[callable] = None,
) -> None:
    """マイクから音声を録音し、WAVファイルとして保存する。should_stop()がTrueなら途中で中断"""
    print("🎙️ 録音開始...")
    p = pyaudio.PyAudio()
    stream = p.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=rate,
        input=True,
        frames_per_buffer=1024,
    )

    frames = []
    total_chunks = int(rate / 1024 * duration)
    for _ in range(total_chunks):
        if should_stop and should_stop():
            print("🛑 録音中断")
            break
        frames.append(stream.read(1024))

    print("🛑 録音終了")

    stream.stop_stream()
    stream.close()
    p.terminate()

    with wave.open(filename, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(rate)
        wf.writeframes(b"".join(frames))
