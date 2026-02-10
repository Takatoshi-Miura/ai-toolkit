---
name: manage-resources
description: Claude Codeリソース(スラッシュコマンド、サブエージェント、Skills)の新規作成・更新・メンテナンス・同期を統括。「コマンド作成」「スキル作成」「エージェント作成」「コマンド更新」「プロンプトメンテナンス」「同期して」「反映して」「.claudeに反映」「sync」「デプロイ」「~/.claudeに反映」「同期」「反映」などで自動適用。
allowed-tools: Write, Read, Edit, Glob, Task, AskUserQuestion, Bash, TodoWrite
user-invocable: true
---

# リソース管理スキル

Claude Codeのリソース(スラッシュコマンド、サブエージェント、Skills)の新規作成・更新・メンテナンス・同期を統括するスキルです。

日本語で回答すること。

## 概要

このスキルは4つの主要な操作をサポートします:

1. **新規作成**: 新しいスラッシュコマンド、サブエージェント、Skillを作成
2. **更新**: 既存リソースを修正・改善
3. **メンテナンス**: リポジトリ全体の整合性チェック・リファクタリング
4. **同期**: ai-toolkitリポジトリの変更を~/.claude/に反映

最初にユーザーに操作タイプを質問し、選択されたワークフローに分岐します。

---

## ワークフロー概要

**TodoWriteで進捗管理すること:**

```
リソース管理進捗:
- [ ] Phase 0: 操作タイプの選択
- [ ] Phase 1-N: (選択されたワークフローに応じて動的に設定)
```

---

## Phase 0: 操作タイプの選択

### 0-1. ユーザーに操作タイプを質問

AskUserQuestionツールで以下の選択肢を提示:

| # | 操作タイプ | 説明 |
|---|-----------|------|
| 1 | 新規作成 | 新しいスラッシュコマンド、サブエージェント、Skillを作成 |
| 2 | 更新 | 既存リソースを修正・改善 |
| 3 | メンテナンス | リポジトリ全体の整合性チェック・リファクタリング |
| 4 | 同期 | ai-toolkitの変更を~/.claude/に一方向同期 |

### 0-2. 選択に応じて分岐

ユーザーの選択に基づいて、該当するワークフローファイルを参照し実行する:

- **新規作成を選択** → [WORKFLOW-CREATE.md](WORKFLOW-CREATE.md) を参照して実行
- **更新を選択** → [WORKFLOW-UPDATE.md](WORKFLOW-UPDATE.md) を参照して実行
- **メンテナンスを選択** → [WORKFLOW-MAINTAIN.md](WORKFLOW-MAINTAIN.md) を参照して実行
- **同期を選択** → [WORKFLOW-SYNC.md](WORKFLOW-SYNC.md) を参照して実行

**重要**: 選択されたワークフローに記載されているTodoWriteチェックリストを使用して、Phase 0以降の進捗を管理すること。

---

## ベストプラクティス参照

リソースタイプ別の詳細ガイド:

- **スラッシュコマンド**: [BEST-PRACTICES-COMMAND.md](BEST-PRACTICES-COMMAND.md)
- **サブエージェント**: [BEST-PRACTICES-AGENT.md](BEST-PRACTICES-AGENT.md)
- **Skills**: [BEST-PRACTICES-SKILL.md](BEST-PRACTICES-SKILL.md)

各ワークフロー内で、リソースタイプに応じた適切なベストプラクティスファイルを参照してください。

---

## 注意事項

### 全ワークフロー共通

- 各ワークフロー完了後は整合性検証を実行
- 生成・更新前に必ずユーザーの承認を得る
- 既存リソースとの重複を避ける
- 命名規則: kebab-case

### 新規作成時

- テンプレートファイルを必ず参照する:
  - スラッシュコマンド: `~/Documents/Git/ai-toolkit/templates/slash-command-template.md`
  - サブエージェント: `~/Documents/Git/ai-toolkit/templates/agent-template.md`
  - Skill: `~/Documents/Git/ai-toolkit/templates/skill-template.md`
- Planサブエージェントを使用して設計案を作成
- README.mdを必ず更新

### 更新時

- 変更前の内容を必ずユーザーに提示
- 大幅な構造変更の場合は新規作成を提案
- descriptionを変更する場合は、自動発動への影響を説明

### メンテナンス時

- `analyze_prompts.py` スクリプトを実行して現状分析
- Planサブエージェントで修正計画を立案
- 修正は必ずユーザー承認後に実施

---

## 完了後の推奨事項

全てのワークフロー完了後、以下を推奨:

1. **変更内容の確認**
   ```bash
   git diff
   ```

2. **整合性検証** (新規作成・更新の場合)
   - このスキルを再度呼び出し、「3. メンテナンス」を選択
   - または直接 `WORKFLOW-MAINTAIN.md` を参照して検証を実行

3. **動作確認**
   - スラッシュコマンド: `/{command_name}` で呼び出しテスト
   - サブエージェント: Taskツールでの呼び出しテスト
   - Skill: 発動条件に合致する依頼でテスト

4. **~/.claude/ への同期** (新規作成・更新の場合)
   - このスキルを再度呼び出し、「4. 同期」を選択して変更を反映

---

## 発動キーワード

このスキルは以下のキーワードを含む依頼で自動的に発動します:

- **新規作成関連**: 「コマンド作成」「スキル作成」「エージェント作成」「サブエージェント作成」
- **更新関連**: 「コマンド更新」「スキル更新」「エージェント更新」
- **メンテナンス関連**: 「プロンプトメンテナンス」「責務分離」「maintain-prompts」
- **同期関連**: 「同期して」「反映して」「.claudeに反映」「sync」「デプロイ」「~/.claudeに反映」「同期」「反映」

---

## トラブルシューティング

### Phase 0で選択肢が表示されない

→ AskUserQuestionツールを使用して選択肢を提示してください

### ワークフローファイルが見つからない

→ ファイルパスを確認: `~/Documents/Git/ai-toolkit/skills/manage-resources/WORKFLOW-*.md`

### Planサブエージェントが失敗する

→ 既存パターンの参照先ディレクトリが正しいか確認してください

### README更新時にセクションが見つからない

→ README.mdの構造を確認し、適切なセクション見出しを検索してください

---

## リファレンス

- 計画書: `/Users/it6210/.claude/plans/whimsical-percolating-zebra.md`
- 公式ドキュメント: [Claude Code Skills Best Practices](https://platform.claude.com/docs/ja/agents-and-tools/agent-skills/best-practices)
