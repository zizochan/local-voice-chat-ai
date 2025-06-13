# local-voice-chat-ai

## 概要

**local-voice-chat-ai**は、ローカル環境で動作する日本語音声対話AIアシスタントです。音声認識（Whisper/faster-whisper）、音声合成（AivisSpeech）、大規模言語モデル（LM Studio等）を組み合わせ、GUI上でキャラクターとの自然な会話を実現します。

- 音声によるAIチャット（入力・出力対応）
- キャラクターやシナリオの切り替え
- 会話履歴の保存・リセット
- LM StudioやAivisSpeechなどローカルAPIとの連携

## 必要な環境

- Python 3.12
- macOS（afplayによる音声再生を利用）
- LM Studio（ローカルLLMサーバー: http://localhost:1234）
- AivisSpeech（音声合成サーバー: http://localhost:10101）

### 事前インストール（Homebrew）

以下のコマンドで必要なライブラリをインストールしてください。

```sh
brew install tcl-tk@8
brew install portaudio
brew install pkg-config
```

#### asdfでtcl-tk対応のPythonをインストールする例

asdfを利用する場合、以下のように環境変数を指定してPythonをインストールしてください。

```sh
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

```sh
poetry install
```

## セットアップ手順

1. LM Studioを起動し、利用したいモデルをロード
2. AivisSpeechを起動
3. 本リポジトリをクローンし、依存ライブラリをインストール

```sh
git clone https://github.com/yourname/local-voice-chat-ai.git
cd local-voice-chat-ai
poetry install
```

## 起動方法

```sh
poetry run python src/main.py
```

初回起動時に設定ダイアログが表示されます。

## キャラクター・シナリオの追加

- `characters/` フォルダにキャラクター設定（.txt）を追加
- `scenarios/` フォルダにシナリオ（.txt）を追加
- `random_speech/` フォルダにランダム発言ファイル（.txt）を追加

## 使い方

1. モデル・話者・キャラクター・シナリオ・ランダム発言ファイルを選択
2. 「開始」ボタンでメイン画面へ
3. 「録音開始」→マイクで話しかける→AIが応答・音声再生
4. 「送信」ボタンでテキスト入力も可能
5. 「ランダム発言」ボタンでファイルからランダム発言
6. 「履歴リセット」で会話履歴を初期化

## テスト

```sh
PYTHONPATH=src poetry run pytest tests/
```

- テスト実行時、`random_speech/` フォルダ内のファイルが一時的に書き換えられる場合があります。

## コード整形（black）

Pythonコードの自動整形にはblackを利用しています。次のコマンドで全ファイルを整形できます。

```sh
poetry run black **/*.py
```

## ライセンス

MIT License

---

※ LM Studio・AivisSpeechの導入・利用方法は各公式ドキュメントを参照し、それぞれのライセンス・利用規約を遵守してください。