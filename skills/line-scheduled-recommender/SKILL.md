---
name: line-scheduled-recommender
description: 実行時刻に応じて CONFIG.md のスケジュール表からテーマを自動選択し、web 検索で推薦コンテンツを生成して LINE グループに定期通知する。お出かけ提案・グルメ・マイホーム提案など複数テーマを 1 スキルで管理できる、Claude Code のルーチン（定期実行）専用スキル。「LINE 通知」「定期推薦」「お出かけ提案」などのキーワードが含まれる場合に使用。
allowed-tools: Read, Write, Bash, WebSearch, TodoWrite
user-invocable: true
disable-model-invocation: true
---

# line-scheduled-recommender

実行時刻に応じてテーマを自動選択し、LINE グループに定期通知する汎用スキル。Claude Code のルーチン（定期実行）から呼び出される想定で、設定・履歴・出力をすべてスキルディレクトリ内に内包する自己完結構成を取る。

## 役割

時刻ディスパッチャーとして、CONFIG.md のスケジュール表と現在時刻を照合し、該当テーマの推薦コンテンツを生成して LINE Messaging API で通知する。

## 重要：このスキルの使い方

**各フェーズを順番に実行すること。フェーズを飛ばしてはならない。**

**制約事項：**
- スキルディレクトリ（`~/.claude/skills/line-scheduled-recommender/`）直下のファイル（CONFIG.md, line_config.json, history.md）を読み書きする
- 秘密情報（channel access token）は line_config.json にのみ存在する
- リトライはしない。送信失敗時は history.md に ERROR として記録して終了する
- 時刻が一致しない場合は何もせず終了し、history.md には記録しない
- history.md は全テーマ共通の 1 ファイル。読み込み・追記時は必ず「テーマ」列で対象行を絞り込む

---

## Phase 0: Todo 登録

**TodoWrite ツールで以下を登録：**

```json
[
  {"content": "Phase 1: 時刻判定・テーマ選択", "status": "pending", "activeForm": "時刻を判定中"},
  {"content": "Phase 2: テーマ設定・履歴の読み込み", "status": "pending", "activeForm": "テーマ設定と履歴を読み込み中"},
  {"content": "Phase 3: 調査・候補生成", "status": "pending", "activeForm": "候補を調査中"},
  {"content": "Phase 4: 選定・本文生成", "status": "pending", "activeForm": "本文を生成中"},
  {"content": "Phase 5: LINE 送信", "status": "pending", "activeForm": "LINE に送信中"},
  {"content": "Phase 6: 履歴更新・出力保存", "status": "pending", "activeForm": "履歴を更新し出力を保存中"}
]
```

各フェーズ開始時に `in_progress`、完了時に `completed` に更新する。

---

## Phase 1: 時刻判定・テーマ選択

### 1-1. 現在時刻の取得

```bash
TZ=Asia/Tokyo date +"%H:%M"
```

取得した時刻を分に換算する（例: `07:15` → `7*60+15 = 435`）。

### 1-2. CONFIG.md の読み込みと照合

スキルディレクトリ直下の `CONFIG.md` を Read ツールで読み込み、スケジュール表の各行について：

```
予定時刻を分に換算
delta = 現在(分) - 予定(分)
0 ≤ delta ≤ 15 なら採用
```

**判定ケース例：**
- 現在 07:15, 予定 07:00 → delta=15 → 採用
- 現在 07:16, 予定 07:00 → delta=16 → スキップ
- 現在 06:59, 予定 07:00 → delta=-1 → スキップ

**一致なしの場合**: 「該当テーマなし（現在 HH:MM、スケジュール: ...）」とログ出力して終了。

**成功確認**: 採用テーマ ID が決定した → Phase 2 へ

---

## Phase 2: テーマ設定・履歴の読み込み

### 2-1. テーマセクションの読み込み

CONFIG.md の `# テーマ: {theme}` セクションから以下を把握する：
- 宛先 groupId（「宛先」セクションに `- groupId: C...` の記載があればそれを使用。省略されている場合は CONFIG.md 冒頭の「共通設定」に記載されたデフォルト宛先 groupId を使用する）
- 調査条件
- メッセージフォーマット

### 2-2. 履歴の読み込み

スキルディレクトリ直下の `history.md` を Read ツールで読み込み、「テーマ」列が `{theme}` と一致する行を抽出して除外対象の一覧を把握する。

**成功確認**: groupId・調査条件・除外一覧が把握できた → Phase 3 へ

---

## Phase 3: 調査・候補生成

### 3-1. 事前情報の収集（テーマに応じて実施）

- **outing テーマ**: 対象日の天気を WebSearch で確認。雨天なら屋内中心に切り替え
- **book テーマ**: スキップ可

### 3-2. 候補の列挙

CONFIG.md の調査条件に合う候補を WebSearch で 5 件ほど列挙する。

**成功確認**: 候補が 3 件以上列挙できた → Phase 4 へ

---

## Phase 4: 選定・本文生成

### 4-1. 除外処理

Phase 2-2 で抽出した `{theme}` の履歴に含まれる候補をすべて除外する。CONFIG.md の「避けたいもの」に合致するものも除外する。

### 4-2. ベスト 1 件の選定

残った候補から調査条件との整合性が最も高いものを 1 つ選ぶ。

### 4-3. 本文生成

CONFIG.md のメッセージフォーマットに沿って送信本文を組み立てる。

**成功確認**: 本文が生成できた → Phase 5 へ

---

## Phase 5: LINE 送信

以下のコマンドを Bash ツールで実行する（スキルディレクトリを cwd として `line_config.json` を読むため、`cd` してから実行する）：

```bash
cd ~/.claude/skills/line-scheduled-recommender && python3 scripts/send_line.py "<本文>" "<Phase 2-1 で決定した groupId>"
```

- exit code 0 → 成功。Phase 6 へ
- exit code 0 以外 → 失敗。エラー内容を記録して Phase 6 へ

**成功確認**: exit code 0 で終了した → Phase 6 へ

---

## Phase 6: 履歴更新・出力保存

### 6-1. history.md への追記

スキルディレクトリ直下の `history.md` の末尾に、共通テーブル形式で 1 行追記する：

- **送信成功時**: `| YYYY-MM-DD | {theme} | {選定タイトル/スポット名} | {URLがあれば記載、なければ -} | - |`
- **送信失敗時**: `| YYYY-MM-DD | {theme} | - | - | ERROR: {エラー内容} |`

### 6-2. output への保存

送信成功時のみ、送信した本文をそのまま `output/<YYYY-MM-DD>_<theme>.md` に保存する（送信失敗時は保存しない）。

**成功確認**: history.md への追記と（送信成功時は）output への保存が完了した → 完了

---

## 詳細リファレンス

- **セットアップ**: [SETUP.md](SETUP.md)

## エラー対応

| エラー | 対応 |
|-------|------|
| line_config.json が見つからない | スキルディレクトリ直下に line_config.json が存在するか確認。SETUP.md を参照 |
| HTTPError 401 / 403 | line_config.json の channel_access_token を確認・更新 |
| HTTPError 400 (invalid group ID) | CONFIG.md の該当テーマの groupId（または共通設定のデフォルト）が正しいか確認 |
| 候補が除外後に 0 件 | history.md の該当テーマの行を確認し、古い記録のアーカイブを検討 |
| 該当テーマなしで頻繁に終了する | CONFIG.md のスケジュール表の時刻と、Claude Code のルーチン実行時刻設定を確認 |

## 出力形式

- 最終的に「送信成功: {テーマ} - {選定内容}」または「送信失敗: {エラー内容}」を報告する
- history.md の追記内容、および（送信成功時は）output への保存先パスも合わせて報告する

## 注意事項

- CONFIG.md は人が日常的に編集する想定。テーマの追加・削除・スケジュール変更はこのファイルのみで完結する
- 新テーマを追加する場合は、CONFIG.md にスケジュール行とテーマセクションを追記する（history.md は全テーマ共通のため新規作成不要）
- line_config.json はバージョン管理システムにコミットしない
- 本スキルは Claude Code のルーチン（定期実行）から呼び出される想定。ルーチンの登録・変更は SETUP.md を参照
