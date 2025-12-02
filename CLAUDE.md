# AI Toolkit - Claude Code Project Context

このリポジトリはClaude CodeのカスタムスラッシュコマンドやAI活用リソースを管理するツールキットです。

## プロジェクト構造

```
ai-toolkit/
├── slash-commands/   # カスタムスラッシュコマンド定義
├── agents/           # エージェント設定・定義
├── task/             # タスク定義ファイル（スラッシュコマンドから参照）
├── templates/        # 定型テンプレート・応答フォーマット
├── rules/            # ルールファイル・ポリシー
├── output-style/     # 出力スタイル設定
├── scripts/          # 自動化スクリプト（Python等）
└── .github/workflows/ # GitHub Actions ワークフロー（定期実行タスク用）
```

## ファイル命名規則

- スラッシュコマンド: `slash-commands/<command-name>.md`
- タスク定義: `task/<task-name>.md`
- エージェント: `agents/<agent-name>.md`
- テンプレート: `templates/<template-name>.md`

## 開発時の注意事項

- スラッシュコマンドは日本語で記述することが多い
- スラッシュコマンド定義内からタスクファイルのファイルパスを参照する形式をとっている
