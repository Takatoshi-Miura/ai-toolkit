---
name: coding
description: コーディングタスクを統括するオーケストレーター。モバイルアプリ開発、MCP開発、SportsNote iOS開発、OpenSpecプロポーザル作成、FE開発に対応。
allowed-tools: Task, AskUserQuestion, Read, Write, Glob, Grep, Edit, Bash
user-invocable: true
disable-model-invocation: true
---

# コーディング オーケストレーター

モバイルアプリ開発、MCP開発、SportsNote iOS開発、OpenSpecプロポーザル作成、およびFE開発のコーディングタスクを統括し、情報収集から実装・テストまでの一連のワークフローを効率的に進行します。

日本語で回答すること。

---

## Phase 0: 開発対象の選択

### 0-1. ユーザーに開発対象を質問

AskUserQuestionツールで以下の選択肢を提示:

| # | 開発対象 | 説明 |
|---|---------|------|
| 1 | モバイルアプリ開発 | Redmineチケットベースの実装タスク（情報収集→計画→実装→テスト→完了） |
| 2 | MCP開発 | MCPサーバーの新規作成・ツール追加・ツール更新 |
| 3 | SportsNote iOS開発 | SportsNote iOSアプリの機能追加・修正・改善（要件ヒアリング→計画→実装→レビュー→ドキュメント更新） |
| 4 | OpenSpecプロポーザル作成 | ai-code-tracker確認・セットアップ後、/opsx:newでプロポーザルを作成 |
| 5 | FE開発 | FE（React/TypeScript）の機能追加・修正・改善（要件ヒアリング→Git準備→計画→実装→セルフチェック） |

### 0-2. 選択に応じて分岐

- **モバイルアプリ開発を選択** → [WORKFLOW-MOBILE.md](WORKFLOW-MOBILE.md) を参照して実行
- **MCP開発を選択** → [WORKFLOW-MCP.md](WORKFLOW-MCP.md) を参照して実行
- **SportsNote iOS開発を選択** → [WORKFLOW-SPORTSNOTE.md](WORKFLOW-SPORTSNOTE.md) を参照して実行
- **OpenSpecプロポーザル作成を選択** → [WORKFLOW-OPENSPEC-PROPOSAL.md](WORKFLOW-OPENSPEC-PROPOSAL.md) を参照して実行
- **FE開発を選択** → [WORKFLOW-FE.md](WORKFLOW-FE.md) を参照して実行

**重要**: 選択されたワークフローに記載されているTodoWriteチェックリストを使用して進捗管理すること。

---

## 使用するサブエージェント・スキル

### モバイルアプリ開発

| リソース | 用途 | 呼び出しPhase |
|---------|------|--------------|
| `/redmine-skill` | Redmineチケット読み取り | Phase 1 |
| `/google-drive-skill` | 概要設計書・テスト項目書読み取り | Phase 1 |
| `Plan` | 実装計画の立案 | Phase 2 |

### MCP開発

| リソース | 用途 |
|---------|------|
| `Plan` | 実装計画の立案 |
| `scripts/analyze_mcp_server.py` | 既存MCPサーバーのツール一覧自動抽出 |

### SportsNote iOS開発

| リソース | 用途 | 呼び出しPhase |
|---------|------|--------------|
| `Plan` | 調査・実装計画の立案 | Phase 2 |
| `doc/*.md` | 仕様書の参照・更新 | Phase 1, 5 |
| `CLAUDE.md` | ビルドコマンド・コーディング規約の参照 | Phase 2, 3 |

### OpenSpecプロポーザル作成

| リソース | 用途 | 呼び出しPhase |
|---------|------|--------------|
| `aict` | AI/人間のコード生成量の計測 | Phase 1 |
| `/opsx:new` | OpenSpec変更の新規作成 | Phase 2 |

### FE開発

| リソース | 用途 | 呼び出しPhase |
|---------|------|--------------|
| `aict` | AI/人間のコード生成量の計測 | Phase 2 |
| `Plan` | 実装計画の立案 | Phase 3 |
| `CLAUDE.md` | ビルド・テスト・Lint等のコマンド参照 | Phase 3, 4 |
| `coding-standards.md` | コーディング規約の参照 | Phase 5 |

---

## エラー対応

| エラー | 対応 |
|-------|------|
| 情報不足 | AskUserQuestionで追加情報を収集 |
| サブエージェント失敗 | エラーメッセージを分析し再試行（最大3回） |
| ビルド失敗 | エラーメッセージを分析し修正支援 |
| 参考実装が見つからない | パスの確認、エラーメッセージ表示 |

---

## 注意事項

- 各Phaseは順序通りに実行（依存関係あり）
- サブエージェントへの指示は具体的かつ明確に
- エラー発生時は該当Phaseで停止し、ユーザーに報告
- Phase完了ごとにTodoWriteで進捗を更新
- 作成・変更前に必ずユーザーの承認を得る
