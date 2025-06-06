# chat.py

import json
import os
import requests
from typing import List, Dict, Any, Tuple
import logging

HISTORY_FILE = "tmp/messages.json"
LM_STUDIO_API_URL = "http://localhost:1234/v1"


def load_history(system_message: str) -> List[Dict[str, Any]]:
    """履歴ファイルがあれば読み込み、なければsystemメッセージで初期化したリストを返す"""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            messages = json.load(f)
            print("📦 履歴読み込み完了")
            return messages
    else:
        print("🆕 新規セッション")
        return [{"role": "system", "content": system_message}]


def save_history(messages: List[Dict[str, Any]]) -> None:
    """履歴をファイルに保存する"""
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)


def query_lmstudio(
    text: str, messages: List[Dict[str, Any]], model_id: str
) -> Tuple[str, List[Dict[str, Any]]]:
    """LM Studio APIに会話を投げて応答を取得する"""
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": model_id,
        "messages": messages,
    }
    try:
        response = requests.post(
            f"{LM_STUDIO_API_URL}/chat/completions",
            headers=headers,
            json=payload,
            timeout=60,
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip(), messages
    except Exception as e:
        logging.warning(f"⚠️ LM Studio エラー: {e}")
        return "", messages


def get_model_list() -> List[str]:
    """利用可能なモデル一覧を取得する"""
    try:
        response = requests.get(f"{LM_STUDIO_API_URL}/models", timeout=10)
        response.raise_for_status()
        data = response.json()
        model_ids = [model["id"] for model in data.get("data", [])]
        return model_ids
    except Exception as e:
        logging.warning(f"⚠️ モデル一覧取得エラー: {e}")
        return []
