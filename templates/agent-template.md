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
| `{description}` | エージェントの説明（Taskツールでの自動選択に使用） | コードレビュー専門エージェント |
| `{tools}` | 使用するツール（カンマ区切り） | `Read, Grep, Glob, Bash` |
| `{model}` | 使用モデル（省略可） | `haiku`, `sonnet`, `opus` |
| `{role}` | AIの役割（短い説明） | コードレビューの専門家 |
| `{role_description}` | 役割の詳細説明 | PRのコード品質、セキュリティ、ベストプラクティスを確認します |
| `{input_parameters}` | 入力パラメータのリスト | - pr_url: レビュー対象のPR URL |
| `{output_requirements}` | 出力要件のリスト | - 問題点の一覧<br>- 改善提案 |

## フロントマターのフィールド

| フィールド | 必須 | 説明 |
|-----------|------|------|
| `name` | Yes | エージェント識別子（小文字とハイフンのみ） |
| `description` | Yes | 自動委譲のためのトリガー説明 |
| `tools` | No | 使用可能ツール（省略時は全ツール継承） |
| `model` | No | `sonnet`, `opus`, `haiku` または省略（継承） |

## 配置先

`~/Documents/Git/ai-toolkit/agents/{agent_name}.md`

## 注意事項

- サブエージェントは独立したコンテキスト窓を持つ
- Taskツールの `subagent_type` パラメータで呼び出される
- `description` はTaskツールでの自動選択に使用されるため、キーワードを含めること
- 専門特化したタスクに適している
