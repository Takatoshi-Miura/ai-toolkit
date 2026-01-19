---
name: subagent-best-practice
description: Claude Codeサブエージェント作成・設計時にベストプラクティスを提供。「エージェント作成」「サブエージェント」「agents」「新しいエージェント」「エージェント設計」などの文脈で自動適用。descriptionの書き方、tools設定、model選択基準（haiku/sonnet/opus）、permissionMode設定などの公式推奨事項を提供。
allowed-tools: Read, Glob
user-invocable: false
---

# サブエージェント ベストプラクティス

Claude Code公式ドキュメントに基づくサブエージェント作成のベストプラクティスです。

## エージェントファイルの基本構造

```markdown
---
name: code-reviewer
description: Expert code review specialist. Proactively reviews code for quality, security, and maintainability.
tools: Read, Grep, Glob, Bash
model: inherit
permissionMode: default
---

You are a senior code reviewer ensuring high standards.

When invoked:
1. Run git diff to see recent changes
2. Focus on modified files
3. Begin review immediately

Review checklist:
- Code is clear and readable
- Proper error handling
- No exposed secrets
- Good test coverage

Provide feedback organized by priority:
- Critical issues (must fix)
- Warnings (should fix)
- Suggestions (consider improving)
```

## フロントマターフィールド

| フィールド | 必須 | 説明 |
|-----------|------|------|
| `name` | ✅ | 小文字とハイフンの一意の識別子 |
| `description` | ✅ | Claudeが委譲を判断する基準（詳細に記述） |
| `tools` | ❌ | 使用可能なツール（省略時はすべて継承） |
| `disallowedTools` | ❌ | 拒否するツール |
| `model` | ❌ | `sonnet`/`opus`/`haiku`/`inherit`（デフォルト: sonnet） |
| `permissionMode` | ❌ | 権限モード |
| `skills` | ❌ | 読み込むスキル |

## Description の書き方（最重要）

Claudeは **descriptionだけ** を読んでタスク委譲を判断します。

### ❌ 悪い例
```yaml
description: Code reviewer
```

### ✅ 良い例
```yaml
description: Expert code review specialist. Proactively reviews code for quality, security, and maintainability. Use immediately after writing or modifying code.
```

### 必須要素
1. **何をするか**: 専門分野を明確に述べる
2. **いつ使うか**: 使用タイミングを指示
3. **"use proactively"**: 自動委譲を促すフレーズを含める

## Model 選択基準

| モデル | 特徴 | 用途 |
|-------|------|------|
| `haiku` | 高速・軽量 | 検索、読み取り専用タスク、シンプルな処理 |
| `sonnet` | バランス型（デフォルト） | 一般的なコード解析・修正 |
| `opus` | 最高性能 | 複雑な推論、アーキテクチャ設計 |
| `inherit` | 親と同じ | 一貫性が必要な場合 |

### 選択ガイドライン

```yaml
# 高速検索・探索
model: haiku

# コードレビュー・一般タスク
model: sonnet

# 複雑なアーキテクチャ設計
model: opus

# 親会話と統一
model: inherit
```

## Tools 設定

### 利用可能なツール

- `Read` - ファイル読み取り
- `Write` - ファイル作成
- `Edit` - ファイル編集
- `Bash` - ターミナルコマンド
- `Grep` - テキスト検索
- `Glob` - ファイルマッチング

### 設定パターン

```yaml
# 読み取り専用レビュアー
tools: Read, Grep, Glob, Bash
disallowedTools: Write, Edit

# 完全なアクセス
tools: Read, Write, Edit, Bash, Grep, Glob

# 特定ツールのみ
tools: Bash, Read
```

## Permission Mode

| モード | 説明 |
|-------|------|
| `default` | 通常の権限チェック |
| `acceptEdits` | 編集を自動承認 |
| `dontAsk` | 確認なしで実行 |
| `bypassPermissions` | 全権限をバイパス |
| `plan` | 計画モード（実行しない） |

## 配置場所とスコープ

| 場所 | スコープ | 優先度 | 用途 |
|------|---------|--------|------|
| `--agents` CLIフラグ | セッション | 1（最高） | クイックテスト |
| `.claude/agents/` | プロジェクト | 2 | チーム共有 |
| `~/.claude/agents/` | ユーザー | 3 | 個人用 |

## 実践的な例

### コードレビュアー

```markdown
---
name: code-reviewer
description: Expert code review specialist. Proactively reviews code for quality, security, and maintainability. Use immediately after writing or modifying code.
tools: Read, Grep, Glob, Bash
model: inherit
---

You are a senior code reviewer.

When invoked:
1. Run git diff to see recent changes
2. Focus on modified files
3. Begin review immediately

Review checklist:
- Code is clear and readable
- No duplicated code
- Proper error handling
- No exposed secrets
- Good test coverage

Provide feedback by priority:
- Critical issues (must fix)
- Warnings (should fix)
- Suggestions (consider)
```

### デバッガー

```markdown
---
name: debugger
description: Debugging specialist for errors, test failures, and unexpected behavior. Use proactively when encountering any issues.
tools: Read, Edit, Bash, Grep, Glob
---

You are an expert debugger.

When invoked:
1. Capture error message and stack trace
2. Identify reproduction steps
3. Isolate the failure location
4. Implement minimal fix
5. Verify solution works

For each issue, provide:
- Root cause explanation
- Specific code fix
- Prevention recommendations
```

### 探索エージェント（高速）

```markdown
---
name: explorer
description: Fast codebase exploration. Use for quick file searches, pattern matching, and code navigation.
tools: Read, Grep, Glob
model: haiku
---

You are a fast codebase explorer.

Focus on:
- Quick file discovery
- Pattern matching
- Code navigation

Return concise results with file paths and line numbers.
```

## ベストプラクティス

### ✅ 推奨

- 焦点を絞った単一目的のエージェント
- 詳細で具体的なdescription
- 必要最小限のツールアクセス
- 明確なシステムプロンプト
- プロジェクトエージェントをバージョン管理に含める

### ❌ 避けるべき

- 漠然とした説明
- 不要なツールアクセス権限
- 複数の役割を兼ねさせる
- セキュリティリスクのある権限設定

## チェックリスト

- [ ] nameは小文字・ハイフンのみ
- [ ] descriptionは詳細（何をするか・いつ使うか）
- [ ] toolsは必要最小限
- [ ] modelはタスク複雑度に応じて選択
- [ ] システムプロンプトに明確な手順を記載

## 参考: 既存エージェントの確認

```bash
# プロジェクトのエージェント一覧
ls -la .claude/agents/

# 個人のエージェント一覧
ls -la ~/.claude/agents/
```
