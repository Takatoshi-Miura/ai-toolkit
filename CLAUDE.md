# AI Toolkit - Claude Code Project Context

このリポジトリはClaude CodeのカスタムスラッシュコマンドやAI活用リソースを管理するツールキットです。

## プロジェクト構造

```
ai-toolkit/
├── .claude/           # Claude Code ローカル設定（settings.local.json等）
├── .github/workflows/ # GitHub Actions ワークフロー（定期実行タスク用）
├── agents/            # Task tool用サブエージェント定義
├── output-style/      # 出力スタイル設定（キャラクター別応答スタイル）
├── rules/             # コード生成ルール・ポリシー
├── scripts/           # 自動化スクリプト（Python等）
├── slash-commands/    # カスタムスラッシュコマンド定義
├── task/              # タスク定義ファイル（スラッシュコマンドから参照）
└── templates/         # テンプレート・リファレンス資料
```

## ファイル命名規則

- スラッシュコマンド: `slash-commands/<command-name>.md`
- タスク定義: `task/<task-name>.md`
- エージェント: `agents/<agent-name>.md`
- テンプレート: `templates/<template-name>.md`

## 開発時の注意事項

- スラッシュコマンドは日本語で記述することが多い
- スラッシュコマンド定義内から`task/`のファイルパスを参照する形式をとっている
- 新しいスラッシュコマンドを作成する際は`templates/slash-command-template.md`を参照
- 新しいタスクを作成する際は`templates/task-template.md`を参照
