---
name: session-log-to-markdown
description: Claude Codeのセッションログ（~/.claude/projects/配下のJSONL）を読みやすい1つのMarkdownファイルに変換・保存する。最新セッション、セッションID指定、カレントプロジェクトの全セッションに対応。「セッションログを保存して」「ログをMarkdownにして」「会話を書き出して」「このセッションを記録して」などの依頼時に使用。
allowed-tools: Bash, Read
user-invocable: true
---

# セッションログMarkdown化スキル

Claude Codeのセッションログ（JSONL）を読み込み、Question/Answer形式の読みやすい1つのMarkdownファイルに変換し、Gitリポジトリ外の個人アーカイブ領域に保存する。

## 役割

セッションログ変換のスペシャリストとして、対象セッションを特定し、`scripts/jsonl_to_markdown.py` を実行してMarkdown化し、結果を報告する。

## 重要：このスキルの使い方

**各フェーズを順番に実行すること。フェーズを飛ばしてはならない。**

**制約事項：**
- 変換処理は必ず `scripts/jsonl_to_markdown.py` 経由で行う（JSONLパースをBashで都度書かない）
- 出力先はデフォルトで `~/Documents/ClaudeLogs/<project-name>/`。リポジトリ内には保存しない
- 対象セッションが曖昧な場合はデフォルト（最新1件）を使う旨を一言確認する

---

## Phase 0: Todo登録

**TodoWriteツールで以下を登録：**

```json
[
  {"content": "Phase 1: 対象セッションの特定", "activeForm": "対象セッションを特定中", "status": "pending"},
  {"content": "Phase 2: JSONL→Markdown変換の実行", "activeForm": "変換を実行中", "status": "pending"},
  {"content": "Phase 3: 結果確認・報告", "activeForm": "結果を確認中", "status": "pending"}
]
```

各フェーズ開始時に`in_progress`、完了時に`completed`に更新する。

---

## Phase 1: 対象セッションの特定

### 1-1. セッション一覧の取得

```bash
python3 ~/Documents/Git/ai-toolkit/skills/session-log-to-markdown/scripts/jsonl_to_markdown.py list
```

カレントディレクトリ（cwd）から自動的にプロジェクトログディレクトリを算出する。`--project-dir <path>` で別プロジェクトを明示指定できる。

### 1-2. 対象モードの確定

ユーザー依頼の内容から対象を判定する：

| ユーザーの依頼例 | モード |
|---|---|
| 指定なし／「このセッションを保存して」 | `--latest`（デフォルト） |
| 「セッションID xxx を」 | `--session-id xxx`（複数可） |
| 「このプロジェクトの全部」 | `--all` |
| 「今週分」「6/1から6/7」 | `--since YYYY-MM-DD --until YYYY-MM-DD` |

対象が曖昧な場合は「最新セッション1件を対象にします」と一言確認してから進める。複数件が該当しうる依頼（全件・日付範囲）は、1-1で取得した一覧を見せてから進める。

**成功確認**: 変換対象のセッションが1件以上確定した → Phase 2へ

---

## Phase 2: JSONL→Markdown変換の実行

### 2-1. 出力先パスの決定

デフォルト規約：

- 単一セッション: `~/Documents/ClaudeLogs/<project-name>/<sessionId先頭8文字>_<YYYYMMDD_HHmm>.md`
- 複数セッション（`--all`/範囲指定）: `~/Documents/ClaudeLogs/<project-name>/all_<開始日>_<終了日>.md`

`<project-name>` はcwdのディレクトリ名（例: `ai-toolkit`）。

### 2-2. 変換スクリプトの実行

```bash
python3 ~/Documents/Git/ai-toolkit/skills/session-log-to-markdown/scripts/jsonl_to_markdown.py convert \
  --output ~/Documents/ClaudeLogs/<project-name>/<filename>.md \
  [--latest | --session-id <id> [--session-id <id2> ...] | --all | --since <date> --until <date>]
```

スクリプトは常にJSON（`success`, `output_path`, `sessions`, `skipped_lines`, `warnings`）をstdoutに出力する。

**成功確認**: exit code 0 かつ `success: true` → Phase 3へ。`success: false` の場合はエラー対応表を参照

---

## Phase 3: 結果確認・報告

### 3-1. 出力ファイルの確認

Readツールで出力ファイルの先頭部分を確認し、空ファイルや文字崩れがないか確認する。

### 3-2. 結果報告

以下を含めてユーザーに報告する：
- 保存先パス（`output_path`）
- 対象セッション数・各セッションのQ&A件数（`sessions`）
- スキップした行数（`skipped_lines`）と警告（`warnings`、ある場合のみ）
- `unchanged: true` の場合は「内容に変更がないため保存をスキップしました」と報告

**成功確認**: 報告完了

---

## 詳細リファレンス

- **出力フォーマット仕様**: [FORMAT.md](FORMAT.md)

## エラー対応

| エラー | 対応 |
|-------|------|
| プロジェクトログディレクトリが存在しない | cwdから算出したディレクトリ名を提示し、誤りがないか確認する |
| 指定`--session-id`のjsonlが見つからない | `list`の結果を提示し、IDの再確認を促す |
| JSONLの一部行でパース失敗 | スクリプトが自動的にスキップして継続する。`skipped_lines`の件数を報告するのみで再実行は不要 |
| 出力先ディレクトリの書き込み権限がない | エラーメッセージをそのまま提示し、別の出力先を確認する |
| セッションが空（0メッセージ） | 「対象セッションにメッセージがありません」と報告し、書き出しを行わない |

**エラーフィードバックループ**:
1. エラーメッセージを確認
2. 上記の表に従って対応
3. 該当フェーズを再実行
4. 成功するまで繰り返す

## 出力形式

[FORMAT.md](FORMAT.md) に準拠したMarkdownファイル。Question/Answerペアごとに見出しを分け、ツール呼び出しは要約1行＋`<details>`での詳細折りたたみで表現する。

## 注意事項

- 出力先はGitリポジトリ外（`~/Documents/ClaudeLogs/`）がデフォルト。リポジトリにログをコミットしない
- `thinking`ブロックは出力に含めない
- 既存ファイルと内容が同一の場合は書き換えを行わない
