---
name: coding
description: コーディングタスクを統括するオーケストレーター。モバイルアプリ開発（Redmineチケットベースの情報収集→実装計画→コード実装→テスト→完了処理）とMCP開発（新規サーバー作成・ツール追加・ツール更新）の両方に対応。「実装したい」「コーディング」「開発タスク」「MCP」「MCPサーバー」「ツール追加」「ツール更新」「サーバー作成」などで使用。
allowed-tools: Task, AskUserQuestion, Read, Write, Glob, Grep, Edit, Bash
user-invocable: true
disable-model-invocation: true
---

# コーディング オーケストレーター

モバイルアプリ開発およびMCP開発のコーディングタスクを統括し、情報収集から実装・テストまでの一連のワークフローを効率的に進行します。

日本語で回答すること。

---

## Phase 0: 開発対象の選択

### 0-1. ユーザーに開発対象を質問

AskUserQuestionツールで以下の選択肢を提示:

| # | 開発対象 | 説明 |
|---|---------|------|
| 1 | モバイルアプリ開発 | Redmineチケットベースの実装タスク（情報収集→計画→実装→テスト→完了） |
| 2 | MCP開発 | MCPサーバーの新規作成・ツール追加・ツール更新 |

### 0-2. 選択に応じて分岐

- **モバイルアプリ開発を選択** → [WORKFLOW-MOBILE.md](WORKFLOW-MOBILE.md) を参照して実行
- **MCP開発を選択** → [WORKFLOW-MCP.md](WORKFLOW-MCP.md) を参照して実行

**重要**: 選択されたワークフローに記載されているTodoWriteチェックリストを使用して進捗管理すること。

---

## 使用するサブエージェント・スキル

### モバイルアプリ開発

| リソース | 用途 | 呼び出しPhase |
|---------|------|--------------|
| `/redmine-skill` | Redmineチケット読み取り | Phase 1 |
| `/google-drive-skill` | 概要設計書・テスト項目書読み取り | Phase 1 |
| `Plan` | 実装計画の立案 | Phase 2 |
| `code-implementer` | コード実装、ビルド確認 | Phase 3 |
| `test-writer` | テストコード作成（条件付き） | Phase 4 |

### MCP開発

| リソース | 用途 |
|---------|------|
| `Plan` | 実装計画の立案 |
| `scripts/analyze_mcp_server.py` | 既存MCPサーバーのツール一覧自動抽出 |

---

## エラー対応

| エラー | 対応 |
|-------|------|
| 情報不足 | AskUserQuestionで追加情報を収集 |
| サブエージェント失敗 | エラーメッセージを分析し再試行（最大3回） |
| ビルド失敗 | エラーメッセージを分析し修正支援 |
| 参考実装が見つからない | パスの確認、エラーメッセージ表示 |

---

## 詳細リファレンス

- **モバイル開発ワークフロー**: [WORKFLOW-MOBILE.md](WORKFLOW-MOBILE.md)
- **MCP開発ワークフロー**: [WORKFLOW-MCP.md](WORKFLOW-MCP.md)
- **共通リファレンス**: [REFERENCE.md](REFERENCE.md)

---

## 注意事項

- 各Phaseは順序通りに実行（依存関係あり）
- サブエージェントへの指示は具体的かつ明確に
- エラー発生時は該当Phaseで停止し、ユーザーに報告
- Phase完了ごとにTodoWriteで進捗を更新
- 作成・変更前に必ずユーザーの承認を得る
