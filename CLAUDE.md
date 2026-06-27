# AI Toolkit - Claude Code Project Context

このリポジトリはClaude CodeのカスタムスラッシュコマンドやAI活用リソースを管理するツールキットです。

## プロジェクト構造

```
ai-toolkit/
├── .claude/           # Claude Code ローカル設定（settings.local.json等）
├── .github/workflows/ # GitHub Actions ワークフロー（定期実行タスク用）
├── agents/            # Task tool用サブエージェント定義
├── output-style/      # 出力スタイル設定（キャラクター別応答スタイル）
├── scripts/           # 自動化スクリプト（Python等）
├── statusline/        # ステータスライン表示スクリプト（~/.claude/statusline.cjsに同期）
└── skills/            # Skills定義（自動起動プロンプト）
```

## リソース作成ルール

### 命名規則

- エージェント: `agents/<name>.md`（kebab-case）
- スキル: `skills/<name>/SKILL.md`（kebab-case）

### 責務分離の判断基準

| リソース | 用途 | 判断基準 |
|---------|------|----------|
| **Skill** | 自動発動のドメイン知識・ワークフロー | Claudeが文脈から自動判断して適用すべきもの |
| **エージェント** | Task toolから委譲される専門タスク | 独立したコンテキストで実行すべきもの |

## プロンプト記述ルール

- 日本語で記述する（技術用語・コード識別子は英語のまま）
- SKILL.mdは**500行以下**に保つ（詳細はWORKFLOW.md等に分離）
- フロントマターの`description`は「何をするか + いつ使うか + トリガー用語」を必ず含める
- 副作用のあるワークフローは `disable-model-invocation: true` を設定する
