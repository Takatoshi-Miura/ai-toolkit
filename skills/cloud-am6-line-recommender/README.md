# マイホーム提案LINE通知（cloud-am6-line-recommender）

## 1. 概要

- **何をするスキルか**: 環境変数の調査条件をもとにマイホーム（マンション）候補を1件調査し、LINE Messaging API でグループに通知する。Claude Code のクラウドルーチンから毎日6時に呼び出されるクラウド実行専用スキル
- **発動条件**:
  - 自動発動キーワード: なし（`disable-model-invocation: true` のため、モデルによる自動発動はしない）
  - スラッシュ呼び出し: `/cloud-am6-line-recommender` で可能
  - 自動発動: なし（明示呼び出しのみ）
- **依存の有無**: LINE Messaging API の channel access token（環境変数 `LINE_CHANNEL_ACCESS_TOKEN`）、Python 3（`scripts/send_line.py` の実行に使用）
- **想定する利用シーン**: Claude Code のクラウドルーチン（Claudeデスクトップアプリから作成）が毎日6時に `/cloud-am6-line-recommender` を実行し、マイホーム候補の提案をLINEグループに自動送信する

## 2. 事前準備（セットアップ）

以下の手順は [references/SETUP.md](references/SETUP.md) に詳細がある。

1. Claudeデスクトップアプリでクラウドルーチンを作成し、Instructions欄に `/cloud-am6-line-recommender` を記載する
2. スケジュールを毎日6:00（ローカルタイムゾーン）に設定する
3. ルーチンの環境（Environment）に、環境変数 `LINE_CHANNEL_ACCESS_TOKEN`・`LINE_GROUP_ID`・`MYHOME_CONDITIONS`（JSON文字列の調査条件）を登録する
4. クラウドルーチンの実行環境に、このリポジトリへの push 権限が付与されていることを確認する（references/history.md・output/ の永続化に使用）

## 3. 使い方

- **呼び出し方法**: `/cloud-am6-line-recommender`（クラウドルーチンのInstructions欄から自動実行、または手動実行）
- **入力例**: 呼び出し時の追加入力は不要（環境変数の調査条件から自動生成する）
- **出力例**:
  - LINE グループへのマイホーム候補提案メッセージ送信
  - `references/history.md` への送信結果（成功時はタイトル・URL、失敗時は ERROR 内容）の追記
  - `output/<YYYY-MM-DD>_myhome.md` への送信本文の保存（送信成功時のみ）
  - references/history.md・output/ の変更を git commit & push してリポジトリに永続化
- **手順**:
  1. 環境変数（トークン・groupId・調査条件）と references/CONFIG.md・references/history.md を読み込む
  2. web 検索で候補を5件ほど調査
  3. references/history.md の履歴・除外条件で絞り込み、ベスト1件を選定して本文を生成
  4. LINE に送信
  5. references/history.md に追記し、送信成功時は output/ にも本文を保存したうえで git commit & push
- **使う際のテクニック・コツ**: 時刻判定は行わない（クラウドルーチン側で6時に発火済みの前提）。調査条件を変えたい場合はファイルではなく環境変数 `MYHOME_CONDITIONS` を更新する

## 4. 保守・拡張ガイド

### ファイル構成

| ファイル | 役割 |
|---------|------|
| SKILL.md | 環境変数読み込み〜調査〜LINE送信〜履歴更新・push までの手順本体 |
| references/SETUP.md | クラウドルーチンの作成手順・環境変数登録手順・groupId取得方法 |
| references/CONFIG.md | 除外条件・メッセージフォーマット（非機密ロジックのみ。調査条件・groupId・トークンは環境変数） |
| references/chipoyo.md | メッセージ生成時に参照するキャラクタースタイル定義 |
| references/history.md | 送信履歴（日付・タイトル・URL・備考）。既存 line-scheduled-recommender の myhome テーマ分（58件）を初期データとして引き継ぎ済み |
| scripts/send_line.py | LINE Messaging API への push メッセージ送信スクリプト（環境変数 `LINE_CHANNEL_ACCESS_TOKEN` からトークンを読む） |
| output/ | 送信本文の保存先。既存 line-scheduled-recommender の myhome 出力4件を引き継ぎ済み |

### 修正時の手順と注意点

- 調査条件・宛先・トークンを変えたい場合は、references/CONFIG.md ではなく環境変数（`MYHOME_CONDITIONS` / `LINE_GROUP_ID` / `LINE_CHANNEL_ACCESS_TOKEN`）を編集する
- メッセージフォーマット・除外条件を変えたい場合は references/CONFIG.md を編集する（SKILL.md の変更は不要）
- 時刻判定ロジックや送信・履歴更新の流れ自体を変える場合は SKILL.md の該当 Phase を編集する
- LINE 送信方法（API・リトライ挙動等）を変える場合は `scripts/send_line.py` を編集する
- 本スキルはクラウド実行専用。ローカルの Desktop Scheduled Tasks からは呼び出さない（ローカル実行したい場合は既存の `line-scheduled-recommender` スキルを使う）

### 依存

- ツール: Read, Write, Bash, WebSearch, TodoWrite（`allowed-tools` に記載）
- MCP / 外部: LINE Messaging API（環境変数 `LINE_CHANNEL_ACCESS_TOKEN` が必要）、git push 権限（references/history.md・output/ の永続化に使用）

### 動作確認・テスト方法

- `/cloud-am6-line-recommender` をクラウドルーチンから手動実行し、以下を確認する
  - LINE グループへの送信が成功すること
  - `references/history.md` に1行追記されること
  - `output/<YYYY-MM-DD>_myhome.md` に送信本文が保存されること
  - references/history.md・output/ の変更が git commit & push されリポジトリに反映されること
- ローカルでの事前確認として、環境変数未設定の状態で `python3 scripts/send_line.py` を実行し、`LINE_CHANNEL_ACCESS_TOKEN が設定されていません` というエラーが出ることを確認できる
