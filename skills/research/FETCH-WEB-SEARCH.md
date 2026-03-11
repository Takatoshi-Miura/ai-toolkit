# Web検索ワークフロー

キーワードでWeb検索し、上位10件のタイトルとリンクを取得する。

日本語で回答すること。

## TodoWrite チェックリスト

```json
[
  {"content": "Phase 1: 検索ワードの入力", "activeForm": "検索ワードを入力中", "status": "pending"},
  {"content": "Phase 2: Web検索の実行", "activeForm": "Web検索を実行中", "status": "pending"},
  {"content": "Phase 3: 結果の表示", "activeForm": "結果を表示中", "status": "pending"}
]
```

---

## Phase 1: 検索ワードの入力

**Phase 1開始時**: TodoWriteで「Phase 1」を `in_progress` に更新

ユーザーに検索ワードを質問する。

**成功確認**: 検索ワードが入力された → Phase 2へ

**Phase 1完了時**: TodoWriteで「Phase 1」を `completed` に更新

---

## Phase 2: Web検索の実行

**Phase 2開始時**: TodoWriteで「Phase 2」を `in_progress` に更新

WebSearchツールを使って検索ワードで検索し、ヒットした記事を上から10件取得する。

- MCPは使用しない
- 検索結果からタイトルとリンクを順番通りに抽出する

**成功確認**: 上位10件の検索結果が取得できた → Phase 3へ

**Phase 2完了時**: TodoWriteで「Phase 2」を `completed` に更新

---

## Phase 3: 結果の表示

**Phase 3開始時**: TodoWriteで「Phase 3」を `in_progress` に更新

以下の出力形式に従って結果を表示する：

```
## タイトル
- [タイトル1]
- [タイトル2]
...（10件）

## リンク集
- [リンク1]
- [リンク2]
...（10件、タイトルと順番対応）
```

**Phase 3完了時**: TodoWriteで「Phase 3」を `completed` に更新

---

## エラー対応

| エラー | 対応 |
|-------|------|
| 検索結果が0件 | 検索ワードを変えて再試行を提案 |
| ネットワークエラー | ネットワーク接続を確認し、再実行を案内 |
