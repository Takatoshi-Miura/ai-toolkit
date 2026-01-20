---
name: read-redmine-skill
description: Read Redmine ticket details. Automatically triggered when user shares a Redmine URL (containing /issues/ path) and asks to read, check, or reference the ticket. Also activates for phrases like "このチケット見て", "Redmine読んで", "チケット確認して", "チケットの内容を教えて", "PBIを確認".
allowed-tools: mcp__mcp-redmine__redmine_get_detail
---

# Redmineチケット読み取りスキル

RedmineチケットのURLからチケット詳細（タイトル、説明、ステータス、履歴等）を自動的に読み取ります。

## 発動条件

このスキルは以下の状況で自動的に適用されます：

- Redmine URL（`/issues/` を含むURL）が含まれ、読み取りを依頼されたとき
- 「チケット見て」「確認して」「内容を教えて」などのキーワードとURLが組み合わさったとき
- PBI（Product Backlog Item）の確認を依頼されたとき（RedmineがPBI管理に使われている場合）

## 手順

### 1. URL確認

ユーザーのメッセージからRedmine URLを抽出する。

URLが提供されていない場合は、ユーザーに質問して提供してもらう：
```
RedmineチケットのURLを教えてください。
例: https://redmine.example.com/issues/123
```

### 2. チケット読み取り

`mcp__mcp-redmine__redmine_get_detail` を使用してチケット情報を取得する。

**取得される情報:**
- チケット番号
- タイトル
- 説明
- ステータス
- 優先度
- 担当者
- 期日
- カスタムフィールド
- 履歴（journals）

### 3. 情報提示

取得した情報をユーザーに分かりやすく整形して提示する。

## 出力形式

```markdown
## Redmineチケット情報

- **チケット番号**: #123
- **タイトル**: （タイトル）
- **ステータス**: （ステータス）
- **優先度**: （優先度）
- **担当者**: （担当者名）
- **期日**: （期日）

### 説明
（チケットの説明内容）

### 最近の更新
（履歴から重要な更新を抽出）
```

## 注意事項

- URLからチケットIDを抽出する（例: `/issues/123` → ID: 123）
- 履歴（journals）が長い場合は、最新の数件のみ表示
- 日本語で回答すること
