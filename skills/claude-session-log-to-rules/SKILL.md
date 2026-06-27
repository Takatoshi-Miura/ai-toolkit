---
name: claude-session-log-to-rules
description: Claude Codeのセッションログ（~/.claude/projects/配下のJSONL、全プロジェクト横断）から過去のフィードバック・指示・承認を抽出し、~/.claude/CLAUDE.mdおよび~/.claude/rules/<project>.mdへの反映を提案する。「過去のフィードバックをルール化して」「セッションから学習して」「同じ指摘を繰り返してる」などの依頼時に使用。
allowed-tools: Bash, Read, Edit, Grep
user-invocable: true
disable-model-invocation: true
---

# claude-session-log-to-rules

Claude Codeの全プロジェクトのセッションログを横断的に解析し、過去に行ったフィードバック・指示・承認をルールファイルに落とし込む。同じ指摘を繰り返さないようにすることが目的。

## 役割

セッションログ解析の専門家として、ルール化候補を抽出し、既存ルールとの重複・矛盾を確認した上で、`~/.claude/CLAUDE.md`または`~/.claude/rules/<project>.md`への反映を提案する。

## 重要：このスキルの使い方

**各フェーズを順番に実行すること。フェーズを飛ばしてはならない。**

**制約事項：**
- JSONLを直接読まない。必ず`scripts/jsonl_to_markdown.py`でMarkdown化（Stage 1）→`scripts/extract_feedback_candidates.py`で候補抽出（Stage 2）の順に実行する（JSONLパースをBashで都度書かない）
- 「ルール化すべきか」「どのプロジェクト/グローバルの話か」「既存ルールと重複しないか」の判断はスクリプトに持たせず、本スキルの手順内でClaude自身が行う
- 編集対象は常に`~/.claude/CLAUDE.md`と`~/.claude/rules/*.md`（中間ファイルやsync工程は経由しない、直接編集）
- ルールファイルへの書き込みは必ず差分を提示し、ユーザーの承認を得てから行う（無断で書き込まない）

---

## Phase 0: Todo登録

**TodoWriteツールで以下を登録：**

```json
[
  {"content": "Phase 1: 候補抽出の実行", "activeForm": "候補を抽出中", "status": "pending"},
  {"content": "Phase 2: 候補の判断・分類", "activeForm": "候補を判断中", "status": "pending"},
  {"content": "Phase 3: 既存ルールとの重複・矛盾チェック", "activeForm": "重複・矛盾を確認中", "status": "pending"},
  {"content": "Phase 4: ルールファイルへの反映", "activeForm": "ルールファイルを更新中", "status": "pending"}
]
```

各フェーズ開始時に`in_progress`、完了時に`completed`に更新する。

---

## Phase 1: 候補抽出の実行

候補抽出は2段構成で行う。JSONLを直接読まず、必ず一度Markdownに変換してから候補抽出する（JSONLは生データが大きくトークン消費が大きいため、軽量なJSON候補リストに絞り込む前段としてMarkdown化を挟む）。

### 1-1. Stage 1: JSONL→Markdown変換

```bash
python3 ~/.claude/skills/claude-session-log-to-rules/scripts/jsonl_to_markdown.py convert \
  --output ~/Documents/ClaudeLogs/all-projects/all_<開始日>_<終了日>.md
```

期間オプションは指定しない（デフォルトで全期間を対象にする）。ユーザーが明示的に期間を指定した場合のみ`--since-days <N>`を付ける。出力先ファイル名の日付部分は`sessions`の`start_time`/`end_time`相当から決める。

`excluded_dirs`（worktree等）が存在する場合は一覧をユーザーに提示する。含めるべきものがあれば`--include-worktrees`を付けて再実行する。

このMarkdownは中間ファイルであり、必要に応じて人間が目視確認できる（Gitリポジトリ外の個人アーカイブ）。

### 1-2. Stage 2: Markdownから候補抽出

```bash
python3 ~/.claude/skills/claude-session-log-to-rules/scripts/extract_feedback_candidates.py scan \
  --input ~/Documents/ClaudeLogs/all-projects/all_<開始日>_<終了日>.md
```

`--input`にはStage 1の`output_path`を指定する。

### 1-3. 件数の確認

`candidates`が極端に少ない場合（数件程度）、正規表現の問題ではなくログの蓄積量自体が少ない可能性が高い（[EXTRACTION-REFERENCE.md](EXTRACTION-REFERENCE.md)参照）。`total_questions_scanned`を確認し、想定通りであればそのまま次に進む。

`warnings`に件数過多の指摘があれば、ユーザーに期間を絞るか確認する。

**成功確認**: `candidates`の一覧が得られた（0件でもユーザーが確認していればよい） → Phase 2へ

---

## Phase 2: 候補の判断・分類

各candidateを読み、以下を判断する（判断基準は[RULE-FORMAT-REFERENCE.md](RULE-FORMAT-REFERENCE.md)参照）。

### 2-1. ルール化対象外の除外

- スキル定義文の混入（`# XXX Skill`等の見出しで始まる長文、ドキュメント調の文章）
- 開発と無関係な雑談・個人的相談
- 一時的な作業指示（特定ファイル名・パスを指定した単発依頼）、その場限りの相づち

### 2-2. プロジェクト名 / グローバルの判定

`cwd`・`project_dir_name`・`context_excerpt`・本文中のファイルパス言及やプロジェクト名キーワードから判定する。cwdは「どこで話したか」であり「何のプロジェクトの話か」ではない点に注意する。

### 2-3. テーマごとの集約

複数セッション・複数プロジェクトで言われた同趣旨の指摘は1つに統合する。元発言（セッションID・日時）を引用元として残す。

**成功確認**: ルール化候補リスト（テーマ・対象スコープ・元発言引用付き）が確定した → Phase 3へ

---

## Phase 3: 既存ルールとの重複・矛盾チェック

### 3-1. 既存ファイルの読み込み

対象スコープに該当するファイルを`Read`する。
- グローバル候補 → `~/.claude/CLAUDE.md`
- プロジェクト別候補 → 該当する`~/.claude/rules/*.md`（存在しなければ新規作成対象）

### 3-2. 分類

[DEDUP-REFERENCE.md](DEDUP-REFERENCE.md)のチェックリストに従い、各候補を「新規追加」「既存セクションへの追記」「矛盾（要確認）」「完全重複（スキップ）」に分類する。矛盾がある場合はユーザーに確認する。

**成功確認**: 全候補が4分類のいずれかに割り振られた → Phase 4へ

---

## Phase 4: ルールファイルへの反映

### 4-1. 差分の提示

「新規追加」「既存セクションへの追記」に分類された候補について、変更内容（新規ファイルは全文、既存ファイルは追記箇所）をユーザーに提示し、承認を得る。

### 4-2. 編集の実行

承認された変更のみ`Edit`または`Write`で反映する。
- グローバル → `~/.claude/CLAUDE.md`
- プロジェクト別 → `~/.claude/rules/<project-kebab-case>.md`（新規ファイルは[RULE-FORMAT-REFERENCE.md](RULE-FORMAT-REFERENCE.md)の書式に従い、frontmatterの`paths`も設定する）

**成功確認**: 承認された変更が全て反映された → 完了報告

---

## エラー対応

| エラー | 対応 |
|-------|------|
| `~/.claude/projects/`が存在しない/空 | セッションログがまだ存在しないことを報告し、処理を終了する |
| JSONLの一部行でパース失敗（Stage 1） | `jsonl_to_markdown.py`が自動的にスキップして継続する。`skipped_lines`の件数を報告するのみで再実行は不要 |
| 候補が0件（Stage 2） | 「ルール化候補が見つかりませんでした」と報告し、期間を広げるか確認する |
| 既存ルールとの矛盾が見つかった | 自動で上書きせず、ユーザーに新旧どちらを採用するか確認する |

**エラーフィードバックループ**:
1. エラーメッセージを確認
2. 上記の表に従って対応
3. 該当フェーズを再実行
4. 成功するまで繰り返す

## 出力形式

Phase 4でユーザーに提示する差分は、ファイルパスと追加/変更される箇条書きを明示したMarkdown形式。最終報告では、反映したルールファイル一覧・スキップした候補数を含める。

## 注意事項

- 編集対象は`~/.claude/CLAUDE.md`・`~/.claude/rules/*.md`そのもの（直接編集して良い）
- ルールファイルへの書き込みは必ずユーザー承認後に行う
- スクリプトに「ルール化すべきか」の判断ロジックを持たせない。判断は常にPhase 2〜3でClaude自身が行う
- Stage 1の中間Markdown（`~/Documents/ClaudeLogs/all-projects/`）はGitリポジトリ外の個人アーカイブ。リポジトリにコミットしない
