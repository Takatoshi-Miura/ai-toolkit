---
name: research
description: 調査系タスクを統合管理するスキル。Web検索・GooglePlayConsole更新情報収集・Claude Codechangelog確認を提供する。「/research」で呼び出すか、調査系の依頼で使用。
allowed-tools: WebFetch, WebSearch, Bash, TodoWrite
user-invocable: true
disable-model-invocation: true
---

# リサーチスキル

調査系タスクを統合管理するスキル。Web検索・PlayConsole・Claude Changelog の3つの調査ワークフローを提供する。

日本語で回答すること。

## 重要：このスキルの使い方

**各フェーズを順番に実行すること。フェーズを飛ばしてはならない。**

**制約事項：**
- MCPツールは使用しない
- ユーザーの最初の発言から調査タイプが明確な場合は、Phase 1のメニュー提示をスキップして直接ルーティングしてよい

---

## Phase 0: Todo登録

**TodoWriteツールで以下を登録：**

```json
[
  {"content": "Phase 1: 調査タイプの選択", "activeForm": "調査タイプを選択中", "status": "pending"},
  {"content": "Phase 2: 選択したワークフローの実行", "activeForm": "調査ワークフローを実行中", "status": "pending"}
]
```

各フェーズ開始時に`in_progress`、完了時に`completed`に更新する。

---

## Phase 1: 調査タイプの選択

以下のメニューをユーザーに提示し、番号で選択してもらう：

```
どの調査を実行しますか？番号を入力してください。

| # | 調査タイプ | 説明 |
|---|-----------|------|
| 1 | Web検索 | キーワードでWeb検索し、上位10件のタイトルとリンクを取得する |
| 2 | Google Play Console 更新情報 | 過去30日間のPlayConsole関連の更新情報を公式ソース4件から収集する |
| 3 | Claude Code Changelog確認 | 前回確認日以降の変更内容を取得・解説し、確認日を記録する |
```

---

## Phase 2: ワークフローへのルーティング

ユーザーの選択に基づいて、該当するワークフローファイルを参照し実行する:

- **「1」または「Web検索」** → [FETCH-WEB-SEARCH.md](FETCH-WEB-SEARCH.md) を参照して実行
- **「2」または「PlayConsole」** → [RESEARCH-PLAY-CONSOLE.md](RESEARCH-PLAY-CONSOLE.md) を参照して実行
- **「3」または「Changelog」** → [CHECK-CLAUDE-CHANGELOG.md](CHECK-CLAUDE-CHANGELOG.md) を参照して実行

**重要**: 選択されたワークフローに記載されているTodoWriteチェックリストを使用して、以降の進捗を管理すること。

---

## ワークフロー一覧

| # | ワークフロー | 説明 | 参照ファイル |
|---|------------|------|------------|
| 1 | Web検索 | キーワード検索で記事を取得 | [FETCH-WEB-SEARCH.md](FETCH-WEB-SEARCH.md) |
| 2 | PlayConsole更新情報 | 公式4ソースから過去30日分を収集 | [RESEARCH-PLAY-CONSOLE.md](RESEARCH-PLAY-CONSOLE.md) |
| 3 | Claude Changelog確認 | 前回確認日以降の変更内容を解説 | [CHECK-CLAUDE-CHANGELOG.md](CHECK-CLAUDE-CHANGELOG.md) |
