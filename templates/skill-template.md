# Skillのテンプレート

以下のテンプレートを使用してSKILL.mdファイルを生成してください。
`{変数名}` の部分を適切な値に置き換えてください。

## テンプレート

```markdown
---
name: {skill_name}
description: {description}
allowed-tools: {allowed_tools}
---

# {skill_title}

## 概要
{overview}

## 発動条件
このスキルは以下の状況で自動的に適用されます：
{trigger_conditions}

## 手順

### 1. {step_1_title}
{step_1_description}

### 2. {step_2_title}
{step_2_description}

### 3. {step_3_title}
{step_3_description}

## 出力形式
{output_format}

## 注意事項
{notes}
```

## 変数の説明

| 変数名 | 説明 | 例 |
|--------|------|-----|
| `{skill_name}` | スキル名（kebab-case） | `pdf-processor`, `data-analyzer` |
| `{description}` | スキルの説明（自動発動の判断に使用、最大1024字） | PDFファイルを処理する際に使用 |
| `{allowed_tools}` | 許可なしで使用できるツール | `Read, Grep, Glob` |
| `{skill_title}` | スキルのタイトル | PDF処理スキル |
| `{overview}` | スキルの概要説明 | PDFファイルからデータを抽出し、構造化された形式で出力します |
| `{trigger_conditions}` | 発動条件のリスト | - PDFファイルの処理を依頼された時<br>- PDFからのデータ抽出を求められた時 |
| `{output_format}` | 出力形式の説明 | マークダウン形式でデータを整形して出力 |
| `{notes}` | 注意事項 | 大きなPDFは分割して処理する |

## フロントマターのフィールド

| フィールド | 必須 | 説明 |
|-----------|------|------|
| `name` | Yes | スキル識別子（小文字、数字、ハイフンのみ、最大64字） |
| `description` | Yes | Claudeがスキル適用判断に使う説明文（最大1024字） |
| `allowed-tools` | No | スキル有効時に許可なしで使えるツール |

## 配置先

`~/Documents/Git/ai-toolkit/skills/{skill_name}/SKILL.md`

## 注意事項

- Skillsはモデル起動型（Claudeが自動判断で適用）
- `description` は自動発動の判断に使用されるため、キーワードを自然な言葉で含めること
