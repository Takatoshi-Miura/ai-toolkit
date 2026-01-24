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
├── skills/            # Skills定義（自動起動プロンプト）
├── commands/          # カスタムスラッシュコマンド定義
├── task/              # タスク定義ファイル（スラッシュコマンドから参照）
└── templates/         # テンプレート・リファレンス資料
```

## ファイル命名規則

- スラッシュコマンド: `commands/<command-name>.md`
- タスク定義: `task/<task-name>.md`
- エージェント: `agents/<agent-name>.md`
- スキル: `skills/<skill-name>/SKILL.md`
- テンプレート: `templates/<template-name>.md`

## 開発時の注意事項

- スラッシュコマンドは日本語で記述することが多い
- スラッシュコマンド定義内から`task/`のファイルパスを参照する形式をとっている
- 新しいスラッシュコマンドを作成する際は`templates/slash-command-template.md`を参照
- 新しいタスクを作成する際は`templates/task-template.md`を参照
- 新しいエージェントを作成する際は`templates/agent-template.md`を参照
- 新しいスキルを作成する際は`templates/skill-template.md`を参照

## 必須: 変更後のメンテナンス

**重要**: このリポジトリ内のファイルを追加・更新・削除した場合は、必ず `manage-resources` スキルのメンテナンスワークフローを実行すること。

このワークフローは以下をチェック・修正します：
- 責務分離の原則に違反していないか（Skills/コマンド/task/Agentの適切な配置）
- フロントマター・必須セクションの形式チェック
- 依存関係の整合性（壊れた参照がないか）
- READMEとの整合性

変更を完了する前に必ず実行し、指摘があれば対応してからコミットすること。

**実行方法**:
- `/manage-resources` を実行し、「3. メンテナンス」を選択
- または直接メンテナンスワークフローを参照: `skills/manage-resources/WORKFLOW-MAINTAIN.md`
