import pyaudio
import wave
import numpy as np
from typing import Optional

WAV_FILENAME = "tmp/input.wav"
MAX_SECONDS = 30  # 最大録音時間
RATE = 16000
SILENCE_THRESHOLD = 300  # 無音判定のRMSしきい値
SILENCE_CHUNKS = int(1.5 * RATE / 1024)  # 1.5秒分の無音で終了


def record_audio(
    filename: str = WAV_FILENAME,
    duration: int = MAX_SECONDS,
    rate: int = RATE,
    should_stop: Optional[callable] = None,
) -> None:
    """
    マイクから音声を録音し、WAVファイルとして保存する。
    ・should_stop()がTrueなら途中で中断
    ・音がしきい値を超えるまで待機し、超えたら録音開始
    ・無音が1.5秒続いたら自動終了
    ・最大30秒で強制終了
    """
    print("🎙️ 録音開始...（発話待機）")
    p = pyaudio.PyAudio()
    stream = p.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=rate,
        input=True,
        frames_per_buffer=1024,
    )

    frames = []
    silence_count = 0
    total_chunks = int(rate / 1024 * duration)
    started = False
    for _ in range(total_chunks):
        if should_stop and should_stop():
            print("🛑 録音中断")
            break
        data = stream.read(1024)
        audio_np = np.frombuffer(data, dtype=np.int16)
        rms = np.sqrt(np.mean(audio_np.astype(np.float64) ** 2))
        if not started:
            if rms > SILENCE_THRESHOLD:
                started = True
                print("🎤 発話検出、録音開始")
                frames.append(data)
                silence_count = 0
            # まだ発話が始まっていなければ何も保存しない
        else:
            frames.append(data)
            if rms < SILENCE_THRESHOLD:
                silence_count += 1
            else:
                silence_count = 0
            if silence_count >= SILENCE_CHUNKS:
                print("🛑 無音検出で録音終了")
                break
    print("🛑 録音終了")
    stream.stop_stream()
    stream.close()
    p.terminate()
    if frames:
        with wave.open(filename, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
            wf.setframerate(rate)
            wf.writeframes(b"".join(frames))
    else:
        print("⚠️ 発話が検出されませんでした")
