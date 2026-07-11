# line-scheduled-recommender（line-scheduled-recommender）

## 1. 概要

- **何をするスキルか**: 実行時刻に応じて CONFIG.md のスケジュール表からテーマ（お出かけ提案・おやつ・晩ごはん・マイホーム提案・新婚旅行先提案など）を自動選択し、web 検索で推薦コンテンツを生成して LINE グループに定期通知する
- **発動条件**:
  - 自動発動キーワード: なし（`disable-model-invocation: true` のため、モデルによる自動発動はしない）
  - スラッシュ呼び出し: `/line-scheduled-recommender` で可能
  - 自動発動: なし（明示呼び出しのみ）
- **依存の有無**: LINE Messaging API の channel access token（`line_config.json`）、Python 3（`scripts/send_line.py` の実行に使用）
- **想定する利用シーン**: Claude Code のルーチン（定期実行）から「line-scheduled-recommender スキルを使って、LINE グループに通知して」のようなプロンプトで毎日/毎週呼び出し、時刻に応じたテーマの推薦を自動送信する

## 2. 事前準備（セットアップ）

以下の手順は [SETUP.md](SETUP.md) に詳細がある。

1. `line_config.json` に LINE Messaging API の channel access token を記入する
2. `CONFIG.md` 冒頭の「共通設定」にデフォルト宛先 groupId を記入する（テーマ個別に別グループへ送りたい場合のみ、該当テーマの「宛先」セクションに上書き記載する）
3. `CONFIG.md` のスケジュール表を編集し、実行したい時刻とテーマを設定する
4. CONFIG.md のスケジュール表の時刻ごとに、Claude Code のルーチン（定期実行）を登録する

## 3. 使い方

- **呼び出し方法**: `/line-scheduled-recommender`、または Claude Code のルーチンから「line-scheduled-recommender スキルを使って、LINE グループに通知して」のようなプロンプトで実行
- **入力例**: 呼び出し時の追加入力は不要（CONFIG.md のスケジュール表と現在時刻から自動判定する）
- **出力例**:
  - LINE グループへの推薦メッセージ送信
  - `history.md` への送信結果（成功時はタイトル・URL、失敗時は ERROR 内容）の追記
  - `output/<YYYY-MM-DD>_<theme>.md` への送信本文の保存（送信成功時のみ）
- **手順**:
  1. 現在時刻と CONFIG.md のスケジュール表を照合し、該当テーマを決定（一致なしなら何もせず終了）
  2. テーマの調査条件・宛先 groupId・メッセージフォーマットと、history.md の該当テーマの履歴を読み込む
  3. web 検索で候補を調査
  4. 履歴・除外条件で絞り込み、ベスト1件を選定して本文を生成
  5. LINE に送信
  6. history.md に追記し、送信成功時は output/ にも本文を保存
- **使う際のテクニック・コツ**: 時刻一致の許容幅は現在時刻が予定時刻の 0〜15 分後まで。テーマ追加は CONFIG.md の編集のみで完結し、history.md は全テーマ共通のため新規作成不要

## 4. 保守・拡張ガイド

### ファイル構成

| ファイル | 役割 |
|---------|------|
| SKILL.md | 時刻判定〜LINE送信〜履歴更新までの手順本体 |
| SETUP.md | 初期セットアップ・Claude Codeルーチン登録・テーマ追加方法 |
| CONFIG.md | 共通設定（デフォルト宛先groupId）・スケジュール表・テーマごとの調査条件とメッセージフォーマット |
| chipoyo.md | 各テーマのメッセージ生成時に参照するキャラクタースタイル定義 |
| history.md | 全テーマ共通の送信履歴（日付・テーマ・タイトル・URL・備考） |
| line_config.json | LINE Messaging API の channel access token（秘密情報、バージョン管理対象外） |
| scripts/send_line.py | LINE Messaging API への push メッセージ送信スクリプト |
| output/ | テーマ・日付ごとの送信本文の保存先 |

### 修正時の手順と注意点

- テーマの条件・メッセージフォーマットを変えたい場合は CONFIG.md の該当テーマセクションのみを編集すればよい（SKILL.md の変更は不要）
- 時刻判定ロジックや送信・履歴更新の流れ自体を変える場合は SKILL.md の該当 Phase を編集する
- LINE 送信方法（API・リトライ挙動等）を変える場合は `scripts/send_line.py` を編集する
- `line_config.json` はバージョン管理システムにコミットしない

### 依存

- ツール: Read, Write, Bash, WebSearch, TodoWrite（`allowed-tools` に記載）
- MCP / 外部: LINE Messaging API（`line_config.json` の channel access token が必要）

### 動作確認・テスト方法

- `/line-scheduled-recommender` を手動実行し、以下を確認する
  - 現在時刻が CONFIG.md のスケジュールに一致するテーマが選択されること
  - LINE グループへの送信が成功すること
  - `history.md` に該当テーマの行が追記されること
  - `output/<YYYY-MM-DD>_<theme>.md` に送信本文が保存されること
