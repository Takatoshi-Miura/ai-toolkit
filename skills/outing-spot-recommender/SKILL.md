---
name: outing-spot-recommender
description: 条件に沿ったお出かけスポットを 1 つ選び、LINE グループに送信する。working folder の CONFIG.md(宛先・調査条件・メッセージフォーマット)と history.md(履歴)を参照し、line_config.json の認証情報で LINE Messaging API に push する。週次のお出かけ提案、外出先の自動選定などで使用。「お出かけ」「スポット」「提案」「LINE通知」などのキーワードが含まれる場合に使用。
allowed-tools: Read, Write, Bash, WebSearch, TodoWrite
user-invocable: true
disable-model-invocation: true
---

# outing-spot-recommender

週末のお出かけ先を 1 件選定し、LINE グループに自動通知するスキル。

## 役割

お出かけスポット選定のアシスタントとして、CONFIG.md の条件と history.md の履歴をもとに、web 検索で最適なスポットを選定し、LINE Messaging API で通知する。

## 重要：このスキルの使い方

**各フェーズを順番に実行すること。フェーズを飛ばしてはならない。**

**制約事項：**
- working folder 直下のファイル(CONFIG.md, history.md, line_config.json)を読み書きする。スキルフォルダ内ではない
- 秘密情報(channel access token)は line_config.json にのみ存在する。スキル本体やプロンプトに埋め込まない
- リトライはしない。送信失敗時は history.md に ERROR として記録して終了する

---

## Phase 0: Todo 登録

**TodoWrite ツールで以下を登録：**

```json
[
  {"content": "Phase 1: 設定・履歴の読み込み", "status": "pending", "activeForm": "設定・履歴を読み込み中"},
  {"content": "Phase 2: 天気・候補調査", "status": "pending", "activeForm": "天気・候補を調査中"},
  {"content": "Phase 3: スポット選定・本文生成", "status": "pending", "activeForm": "スポットを選定中"},
  {"content": "Phase 4: LINE 送信", "status": "pending", "activeForm": "LINE に送信中"},
  {"content": "Phase 5: 履歴更新", "status": "pending", "activeForm": "履歴を更新中"}
]
```

各フェーズ開始時に `in_progress`、完了時に `completed` に更新する。

---

## Phase 1: 設定・履歴の読み込み

### 1-1. CONFIG.md の読み込み

working folder 直下の `CONFIG.md` を Read ツールで読み込み、以下を把握する：
- 宛先 groupId
- 調査条件(エリア・移動手段・ジャンル・避けたいもの・同行者・対象日ルール)
- メッセージフォーマット

### 1-2. history.md の読み込み

working folder 直下の `history.md` を Read ツールで読み込み、除外対象スポット一覧を把握する。

**成功確認**: groupId・調査条件・除外スポット一覧が把握できた → Phase 2 へ

---

## Phase 2: 天気・候補調査

### 2-1. 対象日の決定

CONFIG.md の「対象日」ルールに従って対象日を決定する(デフォルトは次の土曜日)。

### 2-2. 天気確認

対象日の天気を WebSearch で確認する。雨天の場合は CONFIG.md の指示に従って屋内中心に切り替える。

### 2-3. 候補の列挙

CONFIG.md の調査条件に合う候補を WebSearch で 5 件ほど列挙する。
- 「車で行ける場所を優先」の指示がある場合、駐車場の有無・台数・料金も併せて調査する
- 公式 URL・Google Maps URL も収集する

**成功確認**: 候補が 5 件以上列挙できた → Phase 3 へ

---

## Phase 3: スポット選定・本文生成

### 3-1. 除外処理

history.md に含まれる場所をすべて候補から除外する。CONFIG.md の「避けたいもの」に合致するスポットも除外する。

### 3-2. ベスト 1 件の選定

残った候補から、調査条件との整合性が最も高いものを 1 つ選ぶ。

### 3-3. 本文生成

CONFIG.md のメッセージフォーマットに沿って送信本文を組み立てる。

**成功確認**: 本文が生成できた → Phase 4 へ

---

## Phase 4: LINE 送信

### 4-1. スクリプト実行

以下のコマンドを Bash ツールで実行する：

```bash
python scripts/send_line.py "<本文>" "<CONFIG.md の groupId>"
```

- exit code 0 → 成功。Phase 5 へ
- exit code 0 以外 → 失敗。エラー内容を記録して Phase 5 へ

**成功確認**: スクリプトが exit code 0 で終了した → Phase 5 へ

---

## Phase 5: 履歴更新

### 5-1. history.md への追記

- **送信成功時**: `history.md` に `YYYY-MM-DD | スポット名` の 1 行を追記
- **送信失敗時**: `history.md` に `YYYY-MM-DD | ERROR: <エラー内容>` を追記

**成功確認**: history.md の追記が完了した → 完了

---

## 詳細リファレンス

- **セットアップ**: [SETUP.md](SETUP.md)

## エラー対応

| エラー | 対応 |
|-------|------|
| line_config.json が見つからない | working folder に line_config.json が存在するか確認。SETUP.md を参照 |
| HTTPError 401 / 403 | line_config.json の channel_access_token を確認・更新 |
| HTTPError 400 (invalid group ID) | CONFIG.md の groupId が正しいか確認。SETUP.md の groupId 取得方法を参照 |
| 候補が除外後に 0 件 | history.md を確認し、過去の除外が多すぎる場合はアーカイブを検討 |

**エラーフィードバックループ**:
1. エラーメッセージを確認
2. 上記の表に従って対応
3. 該当フェーズを再実行
4. 成功するまで繰り返す(LINE 送信はリトライしない)

## 出力形式

- 最終的に「送信成功: {スポット名}」または「送信失敗: {エラー内容}」を報告する
- history.md の追記内容も合わせて報告する

## 注意事項

- CONFIG.md は人が日常的に編集する想定。季節やコンディションで「避けたいもの」「ジャンル」を書き換えるだけで挙動が変わる
- history.md が肥大化した場合は、古い記録を別ファイルにアーカイブする運用を検討する
- line_config.json はバージョン管理システムにコミットしない
