import json
import os
import requests
from typing import List, Dict, Any, Tuple
import logging

HISTORY_FILE = "tmp/messages.json"
LM_STUDIO_API_URL = "http://localhost:1234/v1"


def make_log_path(log_dir, scenario_filename, character_filename):
    if not scenario_filename or not character_filename:
        raise ValueError("scenario_filenameとcharacter_filenameは必須です")
    base = f"{os.path.splitext(scenario_filename)[0]}__{os.path.splitext(character_filename)[0]}.json"
    return os.path.join(log_dir, base)


def load_history(
    system_message: str, scenario_filename: str = None, character_filename: str = None
) -> List[Dict[str, Any]]:
    """履歴ファイルがあれば読み込み、なければsystemメッセージで初期化したリストを返す"""
    log_dir = os.environ.get("TMP_DIR") or os.path.join(
        os.path.dirname(__file__), "../tmp"
    )
    log_path = make_log_path(log_dir, scenario_filename, character_filename)
    if os.path.exists(log_path):
        with open(log_path, encoding="utf-8") as f:
            messages = json.load(f)
            print("📦 履歴読み込み完了")
            return messages
    else:
        print("🆕 新規セッション")
        return [{"role": "system", "content": system_message}]


def save_history(
    messages: List[Dict[str, Any]],
    scenario_filename: str = None,
    character_filename: str = None,
) -> None:
    """履歴をファイルに保存する"""
    log_dir = os.environ.get("TMP_DIR") or os.path.join(
        os.path.dirname(__file__), "../tmp"
    )
    log_path = make_log_path(log_dir, scenario_filename, character_filename)
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)


def query_lmstudio(
    text: str, messages: List[Dict[str, Any]], model_id: str
) -> Tuple[str, List[Dict[str, Any]]]:
    """LM Studio APIに会話を投げて応答を取得する"""
    print(f"💬 LM Studio送信開始")
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
        content = data["choices"][0]["message"]["content"].strip()
        print(f"💬 AI応答: {content}")
        return content, messages
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


def chat_with_lmstudio(
    text: str, messages: List[Dict[str, Any]], model_id: str
) -> Tuple[str, List[Dict[str, Any]]]:
    """
    ユーザー発言を履歴に追加し、AI応答も履歴に追加して返す
    """
    messages.append({"role": "user", "content": text})
    reply, _ = query_lmstudio(text, messages, model_id)
    messages.append({"role": "assistant", "content": reply})
    return reply, messages
