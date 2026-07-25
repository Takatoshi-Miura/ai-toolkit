---
name: cloud-pm5-line-recommender
description: Claude Code のクラウドルーチンから毎日17時に呼び出され、環境変数の調査条件に基づき新婚旅行先を1件提案してLINEグループに通知する。クラウド実行専用スキル（ローカルのスケジュールタスクでは使わない）。「LINE 通知」「新婚旅行提案」などのキーワードが含まれる場合に使用。
allowed-tools: Read, Write, Bash, WebSearch, TodoWrite
user-invocable: true
disable-model-invocation: true
---

# cloud-pm5-line-recommender

Claude Code のクラウドルーチンから呼び出される想定で、毎日17時の実行時に新婚旅行先を1件調査し、LINE Messaging API でグループに通知する。設定・履歴・出力はすべてスキルディレクトリ内に内包する自己完結構成を取る。

## 役割

クラウドルーチンから渡された調査条件（環境変数）をもとに、新婚旅行先の候補を1件調査・選定し、LINE グループに通知する。

## 重要：このスキルの使い方

**各フェーズを順番に実行すること。フェーズを飛ばしてはならない。**

**制約事項：**
- 秘密情報（LINEチャンネルトークン・宛先groupId・調査条件）はすべて環境変数から読む。ファイルには一切書かない
- スキルディレクトリ（`skills/cloud-pm5-line-recommender/`）直下の references/CONFIG.md・references/history.md・output/ を読み書きする
- リトライはしない。送信失敗時は references/history.md に ERROR として記録して終了する
- references/history.md・output/ の変更は Phase 6 で git commit & push し、リポジトリ側に永続化する（クラウド実行はワークスペースが使い捨てのため）
- 本スキルはクラウドルーチン専用。時刻判定は行わない（ルーチン側で17時に発火済みの前提）

---

## Phase 0: Todo 登録

**TodoWrite ツールで以下を登録：**

```json
[
  {"content": "Phase 1: 環境変数・設定の読み込み", "status": "pending", "activeForm": "環境変数と設定を読み込み中"},
  {"content": "Phase 2: 調査・候補生成", "status": "pending", "activeForm": "候補を調査中"},
  {"content": "Phase 3: 選定・本文生成", "status": "pending", "activeForm": "本文を生成中"},
  {"content": "Phase 4: LINE 送信", "status": "pending", "activeForm": "LINE に送信中"},
  {"content": "Phase 5: 履歴更新・出力保存・push", "status": "pending", "activeForm": "履歴を更新しpush中"}
]
```

各フェーズ開始時に `in_progress`、完了時に `completed` に更新する。

---

## Phase 1: 環境変数・設定の読み込み

### 1-1. 環境変数の読み込み

以下の環境変数を確認する：

- `LINE_CHANNEL_ACCESS_TOKEN`: LINE Messaging API のトークン
- `LINE_GROUP_ID`: 送信先グループID
- `HONEYMOON_CONDITIONS`: 調査条件（JSON文字列）

いずれか未設定の場合は、その旨をエラー出力して終了する（Phase 2 以降には進まない）。

### 1-2. references/CONFIG.md・references/history.md の読み込み

- `references/CONFIG.md` を Read ツールで読み込み、除外条件・メッセージフォーマットを把握する
- `references/history.md` を Read ツールで読み込み、既存の提案先一覧（除外対象）を把握する

**成功確認**: 環境変数・調査条件・除外一覧が把握できた → Phase 2 へ

---

## Phase 2: 調査・候補生成

### 2-1. 候補の列挙

`HONEYMOON_CONDITIONS` の調査条件に合う候補を WebSearch で 5 件ほど列挙する。

**成功確認**: 候補が 3 件以上列挙できた → Phase 3 へ

---

## Phase 3: 選定・本文生成

### 3-1. 除外処理

Phase 1-2 で読み込んだ references/history.md の行に含まれる候補をすべて除外する。`HONEYMOON_CONDITIONS` の「避けたいもの」に合致するものも除外する。

### 3-2. ベスト 1 件の選定

残った候補から調査条件との整合性が最も高いものを 1 つ選ぶ。

### 3-3. 本文生成

references/CONFIG.md のメッセージフォーマットに沿って送信本文を組み立てる。おすすめ理由は references/chipoyo.md のスタイルに従う。

**成功確認**: 本文が生成できた → Phase 4 へ

---

## Phase 4: LINE 送信

以下のコマンドを Bash ツールで実行する（環境変数はプロセスに継承されるため `cd` は不要）：

```bash
python3 skills/cloud-pm5-line-recommender/scripts/send_line.py "<本文>" "$LINE_GROUP_ID"
```

- exit code 0 → 成功。Phase 5 へ
- exit code 0 以外 → 失敗。エラー内容を記録して Phase 5 へ

**成功確認**: exit code 0 で終了した → Phase 5 へ

---

## Phase 5: 履歴更新・出力保存・push

### 5-1. references/history.md への追記

`references/history.md` の末尾に 1 行追記する：

- **送信成功時**: `| YYYY-MM-DD | honeymoon | {選定タイトル/スポット名} | {URLがあれば記載、なければ -} | - |`
- **送信失敗時**: `| YYYY-MM-DD | honeymoon | - | - | ERROR: {エラー内容} |`

### 5-2. output への保存

送信成功時のみ、送信した本文をそのまま `output/<YYYY-MM-DD>_honeymoon.md` に保存する（送信失敗時は保存しない）。

### 5-3. git commit & push・PR作成・自動マージ

references/history.md（および送信成功時は output/ の新規ファイル）を専用ブランチで commit し、PR 作成後に main へ自動マージする。

**注意**: クラウド実行環境は毎回新しい使い捨てブランチ（`claude/xxx` 等）で作業する。このブランチのまま `git push` するだけでは main に反映されず、次回実行時に history.md の更新内容を参照できない（重複提案の原因になる）。必ず PR 作成・マージまで行うこと。

```bash
git add skills/cloud-pm5-line-recommender/references/history.md skills/cloud-pm5-line-recommender/output/
git commit -m "chore: cloud-pm5-line-recommender history 更新 ($(date +%Y-%m-%d))"
git push origin HEAD

gh pr create --title "chore: cloud-pm5-line-recommender history 更新 ($(date +%Y-%m-%d))" \
  --body "クラウドルーチンによる自動更新（history.md 追記・output 保存）" \
  --base main

gh pr merge --auto --squash --delete-branch
```

- `git push` / `gh pr create` に失敗した場合はエラーとして明示的に報告する（「history.md の永続化に失敗しました。次回実行時に重複提案の可能性があります」）
- `gh pr merge --auto` が失敗した場合（ブランチ保護等でマージできない場合）も同様にエラー内容を報告する。この場合 PR 自体は作成済みなので、手動マージが必要な旨を明記する
- `--delete-branch` により、マージ成功後は使い捨てブランチ（`claude/xxx` 等）がリモートから自動削除される。これによりマージ済みブランチが放置・蓄積されるのを防ぐ

**成功確認**: references/history.md への追記・（送信成功時は）output への保存・PR 作成・main への自動マージが完了した → 完了

---

## エラー対応

| エラー | 対応 |
|-------|------|
| `LINE_CHANNEL_ACCESS_TOKEN` / `LINE_GROUP_ID` / `HONEYMOON_CONDITIONS` が未設定 | クラウドルーチンの環境変数設定を確認する。references/SETUP.md を参照 |
| HTTPError 401 / 403 | `LINE_CHANNEL_ACCESS_TOKEN` を確認・更新 |
| HTTPError 400 (invalid group ID) | `LINE_GROUP_ID` が正しいか確認 |
| 候補が除外後に 0 件 | references/history.md の内容を確認し、古い記録のアーカイブを検討 |
| `outbound network policy denied api.line.me:443` | クラウド環境のネットワークアクセス設定で `api.line.me` への発信が許可されていない。環境のネットワークポリシー設定でアクセスを許可する |
| git push 失敗 | クラウドルーチンの環境にリポジトリへの書き込み権限があるか確認 |
| `gh pr create` / `gh pr merge --auto` 失敗 | PR は作成済みだが自動マージできない場合がある（ブランチ保護等）。手動マージが必要な旨を報告する |

## 出力形式

- 最終的に「送信成功: honeymoon - {選定内容}」または「送信失敗: {エラー内容}」を報告する
- references/history.md の追記内容、output への保存先パス、git push の成否も合わせて報告する

## 詳細リファレンス

- **セットアップ**: [references/SETUP.md](references/SETUP.md)
- **設定（除外条件・メッセージフォーマット）**: [references/CONFIG.md](references/CONFIG.md)
- **メッセージスタイル定義**: [references/chipoyo.md](references/chipoyo.md)
- **送信履歴**: [references/history.md](references/history.md)

## 注意事項

- 本スキルはクラウドルーチン専用。ローカルの Desktop Scheduled Tasks からは呼び出さない
- 調査条件・宛先・トークンはすべて環境変数管理。references/CONFIG.md やこのリポジトリに実データを書き込まない
- 調査条件を変更したい場合は、クラウドルーチンの環境変数 `HONEYMOON_CONDITIONS` を更新する（ファイル編集は不要）
