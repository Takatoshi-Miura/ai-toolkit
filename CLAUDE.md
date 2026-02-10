# AI Toolkit - Claude Code Project Context

このリポジトリはClaude CodeのカスタムスラッシュコマンドやAI活用リソースを管理するツールキットです。

## プロジェクト構造

```
ai-toolkit/
├── .claude/           # Claude Code ローカル設定（settings.local.json等）
├── .github/workflows/ # GitHub Actions ワークフロー（定期実行タスク用）
├── agents/            # Task tool用サブエージェント定義
├── commands/          # カスタムスラッシュコマンド定義
├── output-style/      # 出力スタイル設定（キャラクター別応答スタイル）
├── rules/             # ルールファイル（~/.claude/rules/に同期、paths指定で条件適用）
├── scripts/           # 自動化スクリプト（Python等）
├── skills/            # Skills定義（自動起動プロンプト）
└── templates/         # テンプレート・リファレンス資料
```

## リソース作成ルール

### 命名規則

- コマンド: `commands/<name>.md`（kebab-case）
- エージェント: `agents/<name>.md`（kebab-case）
- スキル: `skills/<name>/SKILL.md`（kebab-case）
- ルール: `rules/<name>.md`（kebab-case、pathsフロントマターで適用条件を指定）
- テンプレート: `templates/<name>.md`

### 作成前の必須手順

新しいリソースを作成する際は、該当テンプレートを**必ず**参照すること:
- コマンド → `templates/slash-command-template.md`
- エージェント → `templates/agent-template.md`
- スキル → `templates/skill-template.md`

### 責務分離の判断基準

| リソース | 用途 | 判断基準 |
|---------|------|----------|
| **Skill** | 自動発動のドメイン知識・ワークフロー | Claudeが文脈から自動判断して適用すべきもの |
| **コマンド** | `/xxx` で明示的に呼び出す操作 | ユーザーが意図的にトリガーするもの |
| **エージェント** | Task toolから委譲される専門タスク | 独立したコンテキストで実行すべきもの |
| **ルール** | 横断プロジェクトで自動適用される規約 | pathsで特定ファイル種別にスコープすべきもの |

## プロンプト記述ルール

- 日本語で記述する（技術用語・コード識別子は英語のまま）
- SKILL.mdは**500行以下**に保つ（詳細はWORKFLOW.md等に分離）
- フロントマターの`description`は「何をするか + いつ使うか + トリガー用語」を必ず含める
- 副作用のあるワークフローは `disable-model-invocation: true` を設定する

## 必須: 変更後のメンテナンス

**重要**: このリポジトリ内のファイルを追加・更新・削除した場合は、必ず `manage-resources` スキルのメンテナンスワークフローを実行すること。

このワークフローは以下をチェック・修正します：
- 責務分離の原則に違反していないか（Skills/コマンド/Agentの適切な配置）
- フロントマター・必須セクションの形式チェック
- 依存関係の整合性（壊れた参照がないか）
- READMEとの整合性

変更を完了する前に必ず実行し、指摘があれば対応してからコミットすること。

**実行方法**:
- `/manage-resources` を実行し、「3. メンテナンス」を選択
- または直接メンテナンスワークフローを参照: `skills/manage-resources/WORKFLOW-MAINTAIN.md`
