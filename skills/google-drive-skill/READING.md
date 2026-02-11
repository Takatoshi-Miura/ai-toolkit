# 読み取りワークフロー

## ワークフロー手順

### ステップ1：URLからファイルIDとタイプを抽出

[SKILL.md](SKILL.md) の「共通：URLからファイルIDとタイプを抽出」を参照。

### ステップ2：部分指定の有無を判断

| ユーザーの依頼 | partName |
|--------------|----------|
| 「〇〇シートを読んで」「売上タブ」 | `"〇〇"` |
| 「3ページ目を見せて」 | `3` |
| 「このドキュメントを読んで」「全体」 | 省略 |

### ステップ3：スクリプトを実行

```bash
python3 scripts/read_drive_file.py <fileId> <fileType> [partName]
```

### ステップ4：結果を確認

**成功時**: JSON形式で内容が出力される → 完了

**エラー時のフィードバックループ**:

1. エラーメッセージを確認
2. 以下の表に従って対応
3. ステップ3を再実行
4. 成功するまで繰り返す

| エラー | 対応 |
|-------|------|
| python3: command not found | [SETUP.md](SETUP.md) のトラブルシューティングを参照 |
| 認証エラー / トークンエラー | [SETUP.md](SETUP.md) のセットアップワークフローを実行 |
| ModuleNotFoundError | [SETUP.md](SETUP.md) のステップ1を実行 |
| シート/タブが見つからない | エラーメッセージの `availableSheets` から正しい名前を使用 |

---

## 使用例

### 全体読み取り

```bash
# スプレッドシート全体
python3 scripts/read_drive_file.py 1abc...xyz sheets

# ドキュメント全体
python3 scripts/read_drive_file.py 1abc...xyz docs

# スライド全体
python3 scripts/read_drive_file.py 1abc...xyz presentations
```

### 部分読み取り

```bash
# 特定シートを読み取り
python3 scripts/read_drive_file.py 1abc...xyz sheets "売上"

# 特定タブを読み取り
python3 scripts/read_drive_file.py 1abc...xyz docs "概要"

# 特定ページを読み取り
python3 scripts/read_drive_file.py 1abc...xyz presentations 3
```

---

## 出力形式

### 成功時（スプレッドシート）

```json
{
  "success": true,
  "fileId": "1abc...xyz",
  "fileType": "sheets",
  "partName": "売上",
  "structure": {
    "sheets": [
      {"title": "売上", "sheetId": 0},
      {"title": "経費", "sheetId": 123456}
    ]
  },
  "content": {
    "sheetName": "売上",
    "values": [["日付", "金額"], ["2024/01/01", "10000"]]
  }
}
```

### 成功時（ドキュメント）

```json
{
  "success": true,
  "fileId": "1abc...xyz",
  "fileType": "docs",
  "structure": {
    "tabs": [
      {"tabId": "t.0", "title": "概要", "level": 0},
      {"tabId": "t.1", "title": "詳細", "level": 0}
    ]
  },
  "content": [
    {"tabId": "t.0", "title": "概要", "text": "ドキュメントの内容..."}
  ]
}
```

### 成功時（スライド）

```json
{
  "success": true,
  "fileId": "1abc...xyz",
  "fileType": "presentations",
  "structure": {
    "totalPages": 10,
    "title": "プレゼンテーションタイトル"
  },
  "content": [
    {"pageNumber": 1, "objectId": "p", "text": "タイトルスライド"},
    {"pageNumber": 2, "objectId": "p1", "text": "内容..."}
  ]
}
```

---

## エラーメッセージと対応

### シート/タブが見つからない

```json
{
  "error": "シート \"売り上げ\" が見つかりません",
  "availableSheets": ["売上", "経費", "在庫"]
}
```

**対応**: `availableSheets` に表示された正しい名前を使用して再実行

### 認証エラー

```json
{
  "success": false,
  "error": "認証に失敗しました"
}
```

**対応**: [SETUP.md](SETUP.md) のセットアップワークフローを実行

### ページ番号が範囲外

```json
{
  "error": "ページ 15 は存在しません",
  "totalPages": 10
}
```

**対応**: `totalPages` 以下のページ番号を指定して再実行
