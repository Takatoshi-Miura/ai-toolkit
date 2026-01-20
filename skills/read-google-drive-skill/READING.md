# 読み取り詳細リファレンス

使用例、出力形式、高度な使い方の詳細。

## 目次

- 使用例（全体読み取り）
- 使用例（部分読み取り）
- 出力形式
- エラーメッセージと対応

## 使用例（全体読み取り）

### スプレッドシート全体

```bash
python3 scripts/read_drive_file.py 1abc...xyz sheets
```

### ドキュメント全体

```bash
python3 scripts/read_drive_file.py 1abc...xyz docs
```

### スライド全体

```bash
python3 scripts/read_drive_file.py 1abc...xyz presentations
```

## 使用例（部分読み取り）

### 特定シートを読み取り

```bash
python3 scripts/read_drive_file.py 1abc...xyz sheets "売上"
```

### 特定タブを読み取り

```bash
python3 scripts/read_drive_file.py 1abc...xyz docs "概要"
```

### 特定ページを読み取り

```bash
python3 scripts/read_drive_file.py 1abc...xyz presentations 3
```

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
