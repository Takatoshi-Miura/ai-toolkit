# サブエージェントのテンプレート

以下のテンプレートを使用してサブエージェントファイルを生成してください。
`{変数名}` の部分を適切な値に置き換えてください。

## テンプレート

```markdown
---
name: {agent_name}
description: {description}
tools: {tools}
model: {model}
permissionMode: {permission_mode}
---

あなたは{role}です。

## 役割
{role_description}

## 重要な原則
- **原則1**: {principle_1}
- **原則2**: {principle_2}
- **原則3**: {principle_3}

## 入力パラメータ
ユーザーから以下の情報を受け取ります:
{input_parameters}

## 実行手順

### 1. {step_1_title}
{step_1_description}

### 2. {step_2_title}
{step_2_description}

### 3. {step_3_title}
{step_3_description}

## 出力要件
作業完了時には以下の情報を報告:
{output_requirements}

エラーが発生した場合は、どのステップで失敗したかを明確に報告してください。

ユーザーからパラメータを受け取り次第、上記の手順に従って作業を実行してください。
```

## 変数の説明

| 変数名 | 説明 | 例 |
|--------|------|-----|
| `{agent_name}` | エージェント名（kebab-case） | `code-reviewer`, `data-analyzer` |
| `{description}` | エージェントの説明（**下記参照、最重要**） | 下記「descriptionの書き方」参照 |
| `{tools}` | 使用するツール（カンマ区切り） | `Read, Grep, Glob, Bash` |
| `{model}` | 使用モデル（**下記参照**） | `haiku`, `sonnet`, `opus`, `inherit` |
| `{permission_mode}` | 権限モード | `default`, `acceptEdits`, `dontAsk` |
| `{role}` | AIの役割（短い説明） | コードレビューの専門家 |
| `{role_description}` | 役割の詳細説明 | PRのコード品質、セキュリティ、ベストプラクティスを確認します |
| `{input_parameters}` | 入力パラメータのリスト | - pr_url: レビュー対象のPR URL |
| `{output_requirements}` | 出力要件のリスト | - 問題点の一覧<br>- 改善提案 |

## フロントマターのフィールド

| フィールド | 必須 | 説明 |
|-----------|------|------|
| `name` | ✅ | エージェント識別子（小文字とハイフンのみ） |
| `description` | ✅ | 自動委譲のためのトリガー説明（**最重要**） |
| `tools` | ❌ | 使用可能ツール（省略時は全ツール継承） |
| `disallowedTools` | ❌ | 拒否するツール |
| `model` | ❌ | `sonnet`, `opus`, `haiku`, `inherit`（デフォルト: sonnet） |
| `permissionMode` | ❌ | 権限モード（下記参照） |
| `skills` | ❌ | スタートアップ時に読み込むスキル |
| `hooks` | ❌ | ライフサイクルフック |

---

## descriptionの書き方（最重要）

Claudeは **descriptionだけ** を読んでタスク委譲を判断します。以下の要素を必ず含めてください。

### 必須要素

1. **何をするか**: 専門分野を明確に述べる
2. **いつ使うか**: 使用タイミングを指示
3. **"use proactively"**: 自動委譲を促すフレーズを含める

### ❌ 悪い例

```yaml
description: Code reviewer
```
→ 曖昧すぎて自動委譲されにくい

### ✅ 良い例

```yaml
description: Expert code review specialist. Proactively reviews code for quality, security, and maintainability. Use immediately after writing or modifying code.
```
→ 何をするか（reviews code for quality, security）＋いつ使うか（immediately after writing code）＋proactively

### 日本語の例

```yaml
description: コードレビュー専門エージェント。コード品質・セキュリティ・保守性を積極的にレビュー。コード作成・修正後に即座に使用。
```

---

## model 選択基準

| モデル | 特徴 | 推奨用途 |
|-------|------|----------|
| `haiku` | 高速・軽量・低コスト | 検索、読み取り専用タスク、シンプルな処理 |
| `sonnet` | バランス型（**デフォルト**） | 一般的なコード解析・修正、標準タスク |
| `opus` | 最高性能・高コスト | 複雑な推論、アーキテクチャ設計、難易度の高いタスク |
| `inherit` | 親会話と同じ | 一貫性が必要な場合 |

### 選択ガイドライン

```yaml
# 高速検索・探索（コスト重視）
model: haiku

# コードレビュー・一般タスク（バランス）
model: sonnet

# 複雑なアーキテクチャ設計（品質重視）
model: opus

# 親会話と統一
model: inherit
```

---

## tools 設定

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

---

## permissionMode

| モード | 説明 | 用途 |
|-------|------|------|
| `default` | 通常の権限チェック | 標準（推奨） |
| `acceptEdits` | 編集を自動承認 | 信頼できる編集タスク |
| `dontAsk` | 確認なしで実行 | 自動化タスク |
| `bypassPermissions` | 全権限をバイパス | 完全自動化（注意） |
| `plan` | 計画モード（実行しない） | 計画・設計フェーズ |

---

## 配置場所とスコープ

| 場所 | スコープ | 優先度 | 用途 |
|------|---------|--------|------|
| `--agents` CLIフラグ | セッション | 1（最高） | クイックテスト |
| `.claude/agents/` | プロジェクト | 2 | チーム共有 |
| `~/.claude/agents/` | ユーザー | 3 | 個人用 |

## 配置先

`~/Documents/Git/ai-toolkit/agents/{agent_name}.md`

---

## ベストプラクティス

### ✅ 推奨

- 焦点を絞った単一目的のエージェント
- 詳細で具体的なdescription（何＋いつ＋proactively）
- 必要最小限のツールアクセス
- 明確なシステムプロンプト（手順・出力要件）
- プロジェクトエージェントをバージョン管理に含める

### ❌ 避けるべき

- 漠然とした説明
- 不要なツールアクセス権限
- 複数の役割を兼ねさせる
- セキュリティリスクのある権限設定（bypassPermissionsの乱用）

---

## チェックリスト

- [ ] nameは小文字・ハイフンのみ
- [ ] descriptionは「何をするか＋いつ使うか＋proactively」を含む
- [ ] toolsは必要最小限
- [ ] modelはタスク複雑度に応じて選択（haiku/sonnet/opus）
- [ ] システムプロンプトに明確な手順・出力要件を記載
- [ ] エラー時の報告方法を明記
