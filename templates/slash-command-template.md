# スラッシュコマンドのテンプレート

以下のテンプレートを使用してスラッシュコマンドファイルを生成してください。
`{変数名}` の部分を適切な値に置き換えてください。

## テンプレート

```markdown
---
allowed-tools: {allowed_tools}
description: {description}
---

# 役割
{role}
日本語で回答すること。

# 手順
1. 2で読み取るmdファイルの内容を確認して全体像を把握し、TODOを作成してください
2. ~/Documents/Git/ai-toolkit/task/{command_name}.md のタスクを実施する
3. 上記のタスクが完了したら、総評として上記のmdファイルへのプロンプト修正提案を行う
```

## 変数の説明

| 変数名 | 説明 | 例 |
|--------|------|-----|
| `{allowed_tools}` | 使用するツール | `mcp__mcp-google-drive__*`, `Read, Write, Glob` |
| `{description}` | コマンドの説明（1行） | モバイルアプリ開発のスペシャリストとしてPRのコードレビューを実施 |
| `{role}` | AIの役割 | あなたはモバイルアプリ開発のスペシャリストです |
| `{command_name}` | コマンド名（kebab-case） | `review-code`, `analyze-performance` |