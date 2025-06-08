# local-voice-chat-ai

## 概要

local-voice-chat-aiは、ローカル環境で動作する日本語音声対話AIアシスタントです。音声認識（Whisper/faster-whisper）、音声合成（AIVIS Speech）、大規模言語モデル（LM Studio等）を組み合わせ、GUI上でキャラクターとの自然な会話を実現します。

- 音声入力・音声出力によるAIチャット
- キャラクター・シナリオ切り替え
- 会話履歴の保存・リセット
- LM StudioやAIVIS SpeechなどローカルAPIと連携

## 必要な環境

- Python 3.12
- macOS（afplayによる音声再生を利用）
- LM Studio（ローカルLLMサーバー, http://localhost:1234）
- AIVIS Speech（音声合成サーバー, http://localhost:10101）

### 事前インストール（Homebrew）

以下のコマンドで必要なライブラリをインストールしてください：

```
brew install tcl-tk@8
brew install portaudio
brew install pkg-config
```

#### asdfでtcl-tk対応のPythonをインストールする例

asdfを使ってtcl-tk対応のPythonをインストールする場合、以下のように環境変数を指定してインストールしてください

```
PATH="$(brew --prefix tcl-tk@8)/bin:$PATH" \
LDFLAGS="-L$(brew --prefix tcl-tk@8)/lib" \
CPPFLAGS="-I$(brew --prefix tcl-tk@8)/include" \
PKG_CONFIG_PATH="$(brew --prefix tcl-tk@8)/lib/pkgconfig" \
CFLAGS="-I$(brew --prefix tcl-tk@8)/include" \
PYTHON_CONFIGURE_OPTS="--with-tcltk-includes='-I$(brew --prefix tcl-tk@8)/include' --with-tcltk-libs='-L$(brew --prefix tcl-tk@8)/lib -ltcl8.6 -ltk8.6'" \
asdf install python 3.12.11
```

## 依存ライブラリ

- faster-whisper
- pyaudio
- requests
- tkinter
- pytest

インストールはPoetry推奨です。

```
poetry install
```

## セットアップ

1. LM Studioを起動し、利用したい日本語モデルをロード
2. AIVIS Speechを起動
3. 本リポジトリをクローンし、依存ライブラリをインストール

```
git clone https://github.com/yourname/local-voice-chat-ai.git
cd local-voice-chat-ai
poetry install
```

## 起動方法

```
poetry run python src/main.py
```

初回起動時に設定ダイアログが表示されます。

## 使い方

1. モデル・話者・キャラクター・シナリオを選択
2. 「開始」ボタンでメイン画面へ
3. 「録音開始」→マイクで話しかける→AIが応答・音声再生
4. 「送信」ボタンでテキスト入力も可能
5. 「履歴リセット」で会話履歴を初期化
6. 「オート開始」で自動会話モード

## キャラクター・シナリオの追加

- `characters/` フォルダにキャラクター設定（.txt）を追加
- `scenarios/` フォルダにシナリオ（.txt）を追加

## テスト

```
poetry run pytest
```

## コード整形（black）

Pythonコードの自動整形にはblackを利用しています。次のコマンドで全ファイルを整形できます：

```
poetry run black **/*.py
```

## ライセンス

MIT License

---

※ LM Studio・AIVIS Speechの導入・利用方法は各公式ドキュメントを参照してください。