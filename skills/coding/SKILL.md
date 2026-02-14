---
name: coding
description: モバイルアプリ開発の実装タスクを統括するオーケストレーター。情報収集から実装計画、コード実装、テストまでの一連のワークフローを専門サブエージェントを活用して効率的に進行。「実装したい」「コーディング」「開発タスク」などで使用。
allowed-tools: Task, AskUserQuestion, Read, Bash
user-invocable: true
disable-model-invocation: true
---

# 実装タスク オーケストレーター

モバイルアプリ開発プロジェクトの実装タスクを統括し、情報収集から実装・テストまでの一連のワークフローを専門サブエージェントを活用して効率的に進行します。

日本語で回答すること。

## ワークフロー概要

**TodoWriteで以下の項目を作成して進捗管理すること：**

```
- Phase 1: 情報収集
- Phase 2: 実装計画
- Phase 3: 実装
- Phase 4: テスト（条件付き）
- Phase 5: 完了処理
```

## 必要な入力情報

Phase 1でユーザーから以下を収集する：

| 項目 | 必須 | 例 |
|------|------|-----|
| RedmineチケットURL | ✅ | https://redmine.example.com/issues/12345 |
| 概要設計書URL | ❌ | Google Drive URL |
| テスト項目書URL | ❌ | Google Drive URL（シート名指定可） |
| 実装したいこと | ❌ | 追加の共有事項 |

## Phase概要

### Phase 1: 情報収集
ユーザーへの質問、Redmine/Google Driveからのデータ取得を行う。
→ 詳細: [REFERENCE.md#phase-1-情報収集](REFERENCE.md#phase-1-情報収集)

### Phase 2: 実装計画
`Plan` サブエージェントで実装計画を立案し、ユーザー承認を得る。
→ 詳細: [REFERENCE.md#phase-2-実装計画](REFERENCE.md#phase-2-実装計画)

### Phase 3: 実装
`code-implementer` サブエージェントで実装を実行。
→ 詳細: [REFERENCE.md#phase-3-実装](REFERENCE.md#phase-3-実装)

### Phase 4: テスト（条件付き）
新規ビジネスロジック追加時のみ `test-writer` サブエージェントでテスト作成。
→ 詳細: [REFERENCE.md#phase-4-テスト](REFERENCE.md#phase-4-テスト)

### Phase 5: 完了処理
全Phaseの完了確認と総評を作成。
→ 詳細: [REFERENCE.md#phase-5-完了処理](REFERENCE.md#phase-5-完了処理)

## 使用するサブエージェント・スキル

| リソース | 用途 | 呼び出しPhase |
|---------|------|--------------|
| `/redmine-skill` | Redmineチケット読み取り | Phase 1 |
| `/google-drive-skill` | 概要設計書・テスト項目書読み取り | Phase 1 |
| `Plan` | 実装計画の立案 | Phase 2 |
| `code-implementer` | コード実装、ビルド確認 | Phase 3 |
| `test-writer` | テストコード作成（条件付き） | Phase 4 |

## 出力フォーマット

各Phase完了時に以下の形式で報告：

```markdown
## Phase X 完了報告

### 実施内容
- （実施した内容を箇条書き）

### 成果物
- （生成されたファイル、URL等）

### 次のPhaseへの引き継ぎ事項
- （次のPhaseで必要な情報）
```

## 注意事項

- 各Phaseは順序通りに実行（依存関係あり）
- サブエージェントへの指示は具体的かつ明確に
- エラー発生時は該当Phaseで停止し、ユーザーに報告
- Phase完了ごとにTodoWriteで進捗を更新
