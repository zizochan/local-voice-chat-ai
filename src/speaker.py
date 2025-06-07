import requests
import os
import logging
from typing import List

AIVIS_URL = "http://localhost:10101"


def get_speaker_choices() -> List[str]:
    """AIVIS APIから話者リストを取得し、選択肢リストを返す"""
    try:
        res = requests.get(f"{AIVIS_URL}/speakers")
        res.raise_for_status()
        speakers = res.json()
        choices = []
        for s in speakers:
            for style in s["styles"]:
                choices.append(f"{style['id']}: {s['name']}（{style['name']}）")
        return choices
    except Exception as e:
        logging.warning(f"⚠️ 話者リスト取得失敗: {e}")
        return ["(取得失敗)"]


def speak_with_aivis_speech(text: str, speaker_id: int = 1) -> None:
    """AIVIS APIで音声合成し、再生する"""
    print("🔊 AIVIS Speech に送信中...")
    headers = {"Content-Type": "application/json"}

    # Step1: audio_query 作成
    query_res = requests.post(
        f"{AIVIS_URL}/audio_query",
        params={"speaker": speaker_id, "text": text},
        headers=headers,
    )
    if query_res.status_code != 200:
        print("❌ audio_query 失敗")
        print(f"Status: {query_res.status_code}, Response: {query_res.text}")
        return

    query = query_res.json()

    # Step2: synthesis
    synth_res = requests.post(
        f"{AIVIS_URL}/synthesis",
        json=query,
        params={"speaker": speaker_id},
        headers=headers,
    )
    if synth_res.status_code != 200:
        print("❌ synthesis 失敗")
        print(f"Status: {synth_res.status_code}, Response: {synth_res.text}")
        return

    with open("tmp/output.wav", "wb") as f:
        f.write(synth_res.content)

    print("▶️ 再生中...")
    os.system("afplay tmp/output.wav")
