---
name: skill-manager
description: プライベートスキル（~/.claude/skills/）の新規作成・更新・セルフチェックを、公式ベストプラクティスと過去フィードバックに基づいて行う。ベストプラクティス確認→要望ヒアリング→新規/更新判断→plan設計→承認ループ→作成/更新→セルフレビュー→フィードバックのルール化までを一貫実施。「スキル作成」「スキル作って」「新しいスキル」「スキル更新」「スキルレビュー」「スキルチェック」「skill作成」などの依頼で使用。
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, TodoWrite, AskUserQuestion, WebFetch
user-invocable: true
---

# プライベートスキル管理スキル

`~/.claude/skills/` 配下のプライベートスキルを、公式ベストプラクティスと過去のユーザーフィードバックに基づいて新規作成・更新・セルフチェックする。設計はユーザー承認を得てから実施し、最後にセルフレビューと指摘のルール化を行う。

日本語で回答すること。

## 役割

スキル管理の専門家として、公式ベストプラクティス（progressive disclosure、効果的な description、500行制限等）と過去フィードバックを踏まえ、実用的で発見されやすいスキルを設計・実装する。

## 重要：このスキルの使い方

**各フェーズを順番に実行すること。フェーズを飛ばしてはならない。**

**制約事項：**
- スキルはすべて **プライベートスキル** として `~/.claude/skills/<name>/` に直接作成・更新する（ai-toolkit リポジトリへの master 作成、README 更新、同期は不要）
- 設計はユーザー承認を得てから作成に着手する（無断で作成しない）
- SKILL.md 本体は **500行以下** に保ち、詳細は別ファイルに分離する（progressive disclosure）
- ファイル参照は SKILL.md から **1レベルの深さ** に保つ
- 作成/更新するスキルには、スキルの実体から抽出した **`README.md` を内包する**（`~/.claude/skills/<name>/README.md`）。内容は推測せず実体ベースで記述する（[README-TEMPLATE.md](README-TEMPLATE.md)）

---

## Phase 0: Todo登録

**TodoWriteツールで以下を登録：**

```json
[
  {"content": "Phase 1: 事前インプット確認", "activeForm": "Phase 1: ベストプラクティスと過去フィードバックを確認中", "status": "pending"},
  {"content": "Phase 2: 要望ヒアリング", "activeForm": "Phase 2: ユーザー要望をヒアリング中", "status": "pending"},
  {"content": "Phase 3: 新規/更新の判断", "activeForm": "Phase 3: 新規作成か更新かを判断中", "status": "pending"},
  {"content": "Phase 4: plan設計と承認", "activeForm": "Phase 4: 設計案を作成し承認取得中", "status": "pending"},
  {"content": "Phase 5: 作成/更新（README内包含む）", "activeForm": "Phase 5: スキルとREADMEを作成/更新中", "status": "pending"},
  {"content": "Phase 6: セルフレビュー", "activeForm": "Phase 6: ベストプラクティス準拠をセルフレビュー中", "status": "pending"},
  {"content": "Phase 7: ユーザー確認", "activeForm": "Phase 7: 生成内容をユーザーに確認中", "status": "pending"},
  {"content": "Phase 8: フィードバックのルール化", "activeForm": "Phase 8: 指摘をメモリに保存中", "status": "pending"}
]
```

各フェーズ開始時に `in_progress`、完了時に `completed` に更新する。

---

## Phase 1: 事前インプット確認

**要望を聞く前に、必ず以下2つを確認すること。**

### 1-1. ベストプラクティスの網羅確認

[BEST-PRACTICES.md](BEST-PRACTICES.md) を読み、公式ベストプラクティスの要点を網羅的に把握する。

- 最新情報の確認が必要な場合のみ、WebFetch で公式ドキュメントを取得する：
  `https://platform.claude.com/docs/ja/agents-and-tools/agent-skills/best-practices`

### 1-2. 過去フィードバックの確認（確実に読みにいく）

メモリシステムから、過去にユーザーから受けたフィードバックを **確実に** 確認する。

1. メモリインデックスを読む：
   `~/.claude/projects/-Users-takatoshi-miura--claude/memory/MEMORY.md`
2. インデックスから、スキル作成に関連するフィードバック（`feedback` タイプや `create-skill`・`skill`・`private-skills` を含むもの）を特定し、該当ファイルを読む
3. 特に [[feedback-private-skills]]（スキル作成はすべてプライベート前提）を必ず反映する

**成功確認**: ベストプラクティスの要点と、過去フィードバックの内容を把握できた → Phase 2へ

---

## Phase 2: 要望ヒアリング

### 2-1. 記述式で要望を聞く

ユーザーに、どのようなスキルを作りたいかを **記述式** で質問する。以下を促す：

- **目的**: このスキルで何を実現したいか
- **発動条件**: どのような状況・キーワードで使いたいか
- **想定する動作**: どんな作業をさせたいか
- **必要なツール/外部連携**: ファイル操作・コマンド実行・MCP等

**成功確認**: ユーザーの要望が記述で得られた → Phase 3へ

---

## Phase 3: 新規/更新の判断

### 3-1. 既存スキルの確認

`~/.claude/skills/` を確認し、要望が **新規作成** か **既存スキルの更新** かを判断する：

```bash
ls -1 ~/.claude/skills/
```

- 類似・同名のスキルがあれば、その SKILL.md を読み、更新で対応できるか検討する
- 判断結果（新規 or 更新対象）をユーザーに明示する

### 3-2. 不足情報をまとめて質問

設計に必要な不足情報を、AskUserQuestion で **まとめて1回** で質問する（小出しにしない）。例：

- スキル名（kebab-case の候補を提示）
- ファイル構成（単体 / 分割）
- 自動発動の可否（user-invocable / disable-model-invocation）
- 必要なツール権限（allowed-tools）

**成功確認**: 新規/更新の判断が確定し、設計に必要な情報が揃った → Phase 4へ

---

## Phase 4: plan設計と承認

### 4-1. 設計案の作成

[BEST-PRACTICES.md](BEST-PRACTICES.md) と過去フィードバックを踏まえ、設計案を作成する。テンプレートは
`~/Documents/Git/ai-toolkit/templates/skill-template.md` を参照してよい。

### 4-2. 設計案の提示

以下のフォーマットでユーザーに提示する：

```
## Skill設計案

| 項目 | 内容 |
|------|------|
| スキル名 | {skill_name} |
| 配置先 | ~/.claude/skills/{skill_name}/ |
| 説明（description） | {description} |
| 許可ツール | {allowed_tools} |
| ファイル構成 | {files}（README.md を内包） |

### 発動条件
{trigger_conditions}

### 実行手順（Phase構成）
{steps}

この設計でよろしいですか？修正があればお知らせください。
```

### 4-3. 承認フィードバックループ

**承認が得られるまで** 修正と再提示を繰り返す。承認を得るまで Phase 5 に進まない。

**成功確認**: ユーザーから設計の承認が得られた → Phase 5へ

---

## Phase 5: 作成/更新

### 5-1. ファイル生成/更新

承認された設計に従い、`~/.claude/skills/<name>/` に直接ファイルを作成/更新する。

- **新規作成**: ディレクトリを作り、SKILL.md および分割ファイルを生成
- **更新**: 既存ファイルを Edit で修正
- SKILL.md 本体は 500行以下、参照は 1レベルの深さ
- description は三人称・「何をするか＋いつ使うか＋トリガー語」を含める

### 5-2. README.md の内包生成

スキル本体の生成/更新が終わったら、そのスキルの実体（SKILL.md・補助ファイル・スクリプト）から
**`~/.claude/skills/<name>/README.md` を内包生成**する（出力先は `~/Downloads/` ではなく**スキルディレクトリ内**）。

1. [README-TEMPLATE.md](README-TEMPLATE.md) の4セクション雛形（概要 / 事前準備 / 使い方 / 保守・拡張ガイド）に沿って組み立てる
2. 各項目は **5-1 で生成したスキルの実体から抽出**する（推測・脚色をしない）
   - 発動キーワード・発動条件 → `description` と `user-invocable` / `disable-model-invocation` から
   - ファイル構成・依存 → ディレクトリ内ファイルと `allowed-tools` から
   - 事前準備 → SETUP.md / requirements.txt / 認証記述から（不要なら「準備不要」と明記）
3. **更新の場合**: 既存 README.md があれば実体に合わせて Edit で更新、なければ新規作成する

**成功確認**: スキル本体と README.md が作成/更新された → Phase 6へ

---

## Phase 6: セルフレビュー

### 6-1. チェックリストによる検証

[REVIEW-CHECKLIST.md](REVIEW-CHECKLIST.md) に沿って、生成したスキルがベストプラクティスに準拠しているかを **網羅的に** セルフレビューする。

- スキル本体に加え、**内包した README.md の整合性**（発動キーワード・ファイル名・依存ツール・出力先がスキルの実体と一致しているか）も同チェックリストで検証する
- 不備が見つかった項目は Phase 5 に戻って修正する
- すべての必須項目を満たすまで繰り返す

**成功確認**: チェックリストの必須項目をすべて満たした → Phase 7へ

---

## Phase 7: ユーザー確認

### 7-1. 生成内容の提示

作成/更新したファイルの内容と配置先をユーザーに提示し、最終確認を依頼する。

- 使用方法（`/{skill_name}` での呼び出し、または自動発動条件）を説明する

**成功確認**: ユーザーが内容を確認した → Phase 8へ

---

## Phase 8: フィードバックのルール化

### 8-1. 指摘をメモリに保存

このセッションでユーザーから受けた指摘・修正・好みを、次回以降に活かせるよう **メモリシステムに保存** する。

保存先: `~/.claude/projects/-Users-takatoshi-miura--claude/memory/`

1. 既存メモリに同趣旨のものがないか確認（あれば更新、なければ新規）
2. `feedback` タイプのメモリファイルを作成/更新（frontmatter + 本文に **Why** と **How to apply** を記載）
3. `MEMORY.md` に1行ポインタを追記
4. 関連メモリは `[[name]]` でリンクする

> このフェーズで保存した内容は、次回このスキルの Phase 1-2 で必ず読み込まれ、設計に反映される。

**成功確認**: フィードバックがメモリに保存され、MEMORY.md に反映された → 完了

---

## 詳細リファレンス

- **ベストプラクティス要点**: [BEST-PRACTICES.md](BEST-PRACTICES.md)
- **セルフレビュー用チェックリスト**: [REVIEW-CHECKLIST.md](REVIEW-CHECKLIST.md)
- **README.md 内包テンプレート**: [README-TEMPLATE.md](README-TEMPLATE.md)

## エラー対応

| エラー | 対応 |
|-------|------|
| メモリディレクトリ/MEMORY.md が見つからない | パスを確認。存在しなければ Write で新規作成（mkdir 不要、直接書き込み） |
| 既存スキルと名前が衝突 | Phase 3 に戻り、別名またはユーザー承認のうえ更新に切り替える |
| descriptionが1024文字超過 | 要点を残して簡潔化し再確認 |
| SKILL.mdが500行超過 | 詳細を別ファイルへ分離（progressive disclosure） |
| README.md の記述がスキルの実体と食い違う | 推測で埋めた箇所が原因。Phase 5-2 に戻り実体ベースに書き直す |

**エラーフィードバックループ**:
1. エラー内容を確認
2. 上記表に従って対応
3. 該当フェーズを再実行
4. 成功するまで繰り返す

## 注意事項

- スキル作成はすべてプライベート前提（[[feedback-private-skills]]）。ai-toolkit への作成・README 更新・同期は行わない
- `/manage-resources` はcommand/agent/skill の3種＋ai-toolkit master 運用を扱う汎用スキル。本スキルはプライベートスキル特化の軽量版
- 公式の `description` は三人称で書く（一人称・二人称は発見性を損なう）