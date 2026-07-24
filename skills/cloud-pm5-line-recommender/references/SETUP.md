# cloud-pm5-line-recommender セットアップ

## 前提条件

- LINE Messaging API チャネルが作成済みで、channel access token を入手済みであること
- bot を通知したい LINE グループに招待済みであること
- Claude Code のクラウドルーチン（Claudeデスクトップアプリから作成）が利用可能なプランであること
- クラウドルーチンの実行環境に、このリポジトリへの push 権限が付与されていること（references/history.md・output/ の永続化に使用）

---

## セットアップ手順

### 1. Claudeデスクトップアプリでクラウドルーチンを作成

1. Claudeデスクトップアプリでルーチンの新規作成画面を開く
2. 実行対象のリポジトリとして、このスキルが含まれるリポジトリを選択する
3. Instructions（実行内容）欄に以下を記載する：
   ```
   /cloud-pm5-line-recommender
   ```
4. スケジュールを「毎日 17:00（ローカルタイムゾーン）」に設定する

### 2. 環境変数の登録

ルーチンが使用する環境（Environment）の設定画面で、以下の環境変数を登録する：

| 変数名 | 内容 |
|--------|------|
| `LINE_CHANNEL_ACCESS_TOKEN` | LINE Messaging API の channel access token |
| `LINE_GROUP_ID` | 通知先の LINE グループ ID |
| `HONEYMOON_CONDITIONS` | 調査条件（JSON文字列）。キーの例: エリア・旅行時期・泊数・予算・出発地・避けたいもの・同行者・補足。値はClaudeデスクトップアプリの環境変数設定画面で直接入力する（このファイルには具体値を記載しない） |

> **注意**: 環境変数は環境（Environment）単位で共有される。複数のルーチン・スキルで同じ環境を使う場合は、変数名の衝突に注意すること。

### 3. 動作確認

ルーチンを一度手動実行し、以下を確認する：
- LINE グループへの送信が成功すること
- `references/history.md` に1行追記されること
- `output/<YYYY-MM-DD>_honeymoon.md` に送信本文が保存されること
- references/history.md・output/ の変更がリポジトリに commit & push されること

---

## groupId の取得方法

1. bot を通知したい LINE グループに招待する
2. webhook ハンドラがある場合は、グループ内で誰かが発言した際のイベント JSON から `source.groupId` を取得
3. webhook 未実装の場合：
   - LINE Developers コンソールで webhook URL を requestbin などのテスト受信サービスに一時変更
   - グループで一言発言してイベントを受信
   - `source.groupId` を取得後、元の設定に戻す
4. 取得した groupId を環境変数 `LINE_GROUP_ID` に登録する

---

## 運用上の注意

- 本スキルはクラウドルーチン専用。ローカルの Desktop Scheduled Tasks からは呼び出さない（ローカル実行したい場合は既存の `line-scheduled-recommender` スキルを使う）
- `references/history.md` が肥大化しても動作に支障はないが、気になる場合は古い記録を別ファイルに退避する
- 調査条件を変更したい場合は、references/CONFIG.md ではなく環境変数 `HONEYMOON_CONDITIONS` を更新する

## 変更が起きたときの対応箇所

| やりたいこと | 編集するもの |
|---|---|
| 実行時刻を変えたい | クラウドルーチンのスケジュール設定 |
| 調査条件を変えたい | 環境変数 `HONEYMOON_CONDITIONS` |
| 宛先グループを変えたい | 環境変数 `LINE_GROUP_ID` |
| メッセージの見た目を変えたい | references/CONFIG.md のメッセージフォーマット |
| ロジックを変えたい | SKILL.md |
| LINE 送信方法を変えたい | scripts/send_line.py |
| トークンを更新したい | 環境変数 `LINE_CHANNEL_ACCESS_TOKEN` |
