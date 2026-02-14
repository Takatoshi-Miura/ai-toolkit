# 読み取りワークフロー

## ワークフロー手順

### ステップ1: URLからチケットIDを抽出

[SKILL.md](SKILL.md) の「共通: URLからチケットIDを抽出」を参照。

### ステップ2: スクリプトを実行

```bash
python3 scripts/get_redmine_ticket.py <ticket_id>
```

### ステップ3: 結果を確認

**成功時**: JSON形式でチケット情報が出力される → ステップ4へ

**エラー時のフィードバックループ**:

1. エラーメッセージを確認
2. 以下の表に従って対応
3. ステップ2を再実行
4. 成功するまで繰り返す

| エラー | 対応 |
|-------|------|
| python3: command not found | [SETUP.md](SETUP.md) のトラブルシューティングを参照 |
| Redmine設定がありません | [SETUP.md](SETUP.md) のセットアップ手順を実行 |
| HTTP 403: Forbidden | APIキーの権限を確認 |
| HTTP 404: Not Found | チケットIDが正しいか確認 |

### ステップ4: 情報提示

取得した情報を以下のテンプレートに従って整形し、ユーザーに提示する。

---

## 出力形式

### スクリプトの成功時出力

```json
{
  "success": true,
  "id": 12345,
  "subject": "チケットタイトル",
  "description": "チケットの説明内容",
  "status": "進行中",
  "priority": "通常",
  "assigned_to": "担当者名",
  "due_date": "2025-03-31",
  "custom_fields": [
    {"id": 1, "name": "フィールド名", "value": "値"}
  ],
  "journals": [
    {
      "id": 1,
      "user": "ユーザー名",
      "notes": "コメント内容",
      "created_on": "2025-01-15T10:30:00Z",
      "details": []
    }
  ]
}
```

### ユーザーへの提示テンプレート

```markdown
## Redmineチケット情報

- **チケット番号**: #12345
- **タイトル**: （subject）
- **ステータス**: （status）
- **優先度**: （priority）
- **担当者**: （assigned_to）
- **期日**: （due_date）

### 説明
（description の内容）

### カスタムフィールド
（custom_fields がある場合のみ表示）

### 最近の更新
（journals の最新数件を表示。件数が多い場合は最新5件程度に絞る）
```

---

## 使用例

### 基本的な使用

```bash
# チケット番号を指定して取得
python3 scripts/get_redmine_ticket.py 12345
```

### URLからの抽出例

| URL | 抽出されるID |
|-----|-------------|
| `https://redmine.example.com/issues/12345` | `12345` |
| `https://redmine.example.com/issues/12345#note-5` | `12345` |
| `https://redmine.example.com/issues/12345?tab=history` | `12345` |
