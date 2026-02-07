---
name: sync-to-claude
description: ai-toolkitリポジトリの変更を~/.claude/に同期する。commands, agents, skillsを一方向コピー。「同期して」「反映して」「.claudeに反映」「sync」「デプロイ」「~/.claudeに反映」「同期」「反映」などの依頼で使用。
allowed-tools: Bash, Read, TodoWrite
user-invocable: true
disable-model-invocation: false
---

# ai-toolkit → ~/.claude/ 同期スキル

ai-toolkitリポジトリの commands, agents, skills を `~/.claude/` に一方向同期する。
ai-toolkitに存在するもののみコピーし、`~/.claude/` にしか存在しないファイルは一切触れない。

## 重要：このスキルの使い方

**各フェーズを順番に実行すること。フェーズを飛ばしてはならない。**

**制約事項：**
- 同期方向は ai-toolkit → ~/.claude/ の一方向のみ
- ~/.claude/ にしか存在しないファイル・ディレクトリは削除しない
- Pythonスクリプトのみを使用する（外部ツール不要）

---

## Phase 0: Todo登録

**TodoWriteツールで以下を登録：**

```json
[
  {"content": "Phase 1: 同期スクリプト実行", "activeForm": "同期スクリプトを実行中", "status": "pending"},
  {"content": "Phase 2: 結果の表示", "activeForm": "結果を表示中", "status": "pending"}
]
```

各フェーズ開始時に`in_progress`、完了時に`completed`に更新する。

---

## Phase 1: 同期スクリプト実行

### 1-1. スクリプトの実行

以下のコマンドを実行する：

```bash
python3 skills/sync-to-claude/scripts/sync.py
```

**成功確認**: JSON結果が出力された → Phase 2へ

---

## Phase 2: 結果の表示

### 2-1. 結果の整形

Phase 1のJSON出力から以下のマークダウン表を作成して表示する：

```markdown
## 同期結果

| カテゴリ | コピー | スキップ（変更なし） | エラー |
|---------|--------|-------------------|--------|
| commands | X件 | Y件 | Z件 |
| agents | X件 | Y件 | Z件 |
| skills | X件 | Y件 | Z件 |

### コピーされたファイル
- ...
```

- コピーされたファイルがある場合はファイル名を一覧表示
- エラーがある場合はエラー内容を表示
- 全てスキップの場合は「すべて最新です。変更はありません。」と表示
- `onlyInDest` がある場合は「~/.claude/ にのみ存在（同期対象外）」として一覧表示

**成功確認**: 結果が表示された → 完了

---

## エラー対応

| エラー | 対応 |
|-------|------|
| ディレクトリが見つからない | ai-toolkitリポジトリのパスを確認 |
| Permission denied | ~/.claude/ の書き込み権限を確認 |

## 注意事項

- `--dry-run` オプションで事前確認が可能: `python3 skills/sync-to-claude/scripts/sync.py --dry-run`
- 差分があるファイルのみコピーする（ファイル内容のハッシュ比較）
- skills/ はサブディレクトリ（scripts/等）も含めて再帰的にコピー
