# Google Drive 書き込み操作リファレンス

このドキュメントでは、各スクリプトの詳細な使用例と出力形式を説明する。

## 目次

1. [値挿入（insert_value.py）](#値挿入insert_valuepy)
2. [新規作成（create_element.py）](#新規作成create_elementpy)
3. [要素コピー（copy_element.py）](#要素コピーcopy_elementpy)
4. [セル結合（merge_cells.py）](#セル結合merge_cellspy)
5. [セル一括結合（merge_cells_batch.py）](#セル一括結合merge_cells_batchpy)
6. [エラー対応](#エラー対応)

---

## 値挿入（insert_value.py）

### 基本構文

```bash
python3 scripts/insert_value.py <fileId> <fileType> <target> <content> [options]
```

### スプレッドシート（sheets）

#### 範囲指定で値を挿入

```bash
python3 scripts/insert_value.py 1abc...xyz sheets "Sheet1!A1" '[["値1","値2"],["値3","値4"]]'
```

**成功時の出力:**
```json
{
  "success": true,
  "fileId": "1abc...xyz",
  "fileType": "sheets",
  "target": "Sheet1!A1",
  "updatedCells": 4,
  "updatedRange": "Sheet1!A1:B2",
  "append": false
}
```

#### 末尾に行を追加（--append）

```bash
python3 scripts/insert_value.py 1abc...xyz sheets "Sheet1" '[["新しい行のデータ"]]' --append
```

**成功時の出力:**
```json
{
  "success": true,
  "fileId": "1abc...xyz",
  "fileType": "sheets",
  "target": "Sheet1",
  "updatedCells": 1,
  "updatedRange": "Sheet1!A10:A10",
  "append": true
}
```

### ドキュメント（docs）

#### 末尾にテキストを挿入

```bash
python3 scripts/insert_value.py 1abc...xyz docs -1 "追加するテキスト"
```

**成功時の出力:**
```json
{
  "success": true,
  "fileId": "1abc...xyz",
  "fileType": "docs",
  "location": 150,
  "originalLocation": -1,
  "textLength": 9,
  "tabId": null
}
```

#### 特定位置にテキストを挿入

```bash
python3 scripts/insert_value.py 1abc...xyz docs 50 "挿入テキスト"
```

#### 特定タブにテキストを挿入

```bash
python3 scripts/insert_value.py 1abc...xyz docs -1 "テキスト" --tab-id "t.abc123"
```

### スライド（presentations）

#### テキストボックスを追加

```bash
python3 scripts/insert_value.py 1abc...xyz presentations 0 "スライドに追加するテキスト"
```

**成功時の出力:**
```json
{
  "success": true,
  "fileId": "1abc...xyz",
  "fileType": "presentations",
  "slideIndex": 0,
  "slideId": "g12345",
  "textBoxId": "textbox_1705123456789",
  "bounds": {
    "x": 100,
    "y": 100,
    "width": 400,
    "height": 100
  },
  "textLength": 14
}
```

#### 位置とサイズを指定

```bash
python3 scripts/insert_value.py 1abc...xyz presentations 0 "テキスト" --bounds '{"x":200,"y":300,"width":500,"height":150}'
```

---

## 新規作成（create_element.py）

### 基本構文

```bash
python3 scripts/create_element.py <fileId> <fileType> <name>
```

### 新規シート作成

```bash
python3 scripts/create_element.py 1abc...xyz sheets "売上データ"
```

**成功時の出力:**
```json
{
  "success": true,
  "fileId": "1abc...xyz",
  "fileType": "sheets",
  "operation": "create",
  "sheetTitle": "売上データ",
  "sheetId": 123456789,
  "sheetIndex": 1
}
```

### 新規スライド作成

```bash
python3 scripts/create_element.py 1abc...xyz presentations "第2章: 詳細分析"
```

**成功時の出力:**
```json
{
  "success": true,
  "fileId": "1abc...xyz",
  "fileType": "presentations",
  "operation": "create",
  "slideTitle": "第2章: 詳細分析",
  "slideObjectId": "slide_1705123456789",
  "titleObjectId": "title_1705123456789"
}
```

### ドキュメント（未サポート）

```bash
python3 scripts/create_element.py 1abc...xyz docs "新しいタブ"
```

**エラー出力:**
```json
{
  "success": false,
  "fileId": "1abc...xyz",
  "fileType": "docs",
  "operation": "create",
  "error": "Google Docs API の制限により、ドキュメントへの新規タブ作成はサポートされていません",
  "note": "代替案として、手動でセクション見出しを追加することを検討してください"
}
```

---

## 要素コピー（copy_element.py）

### 基本構文

```bash
python3 scripts/copy_element.py <fileId> <fileType> <sourceId> [newName]
```

### シートをコピー

シートIDはスプレッドシートのURL `#gid=123456` の数値部分。

```bash
# 名前を指定してコピー
python3 scripts/copy_element.py 1abc...xyz sheets 0 "売上データ（コピー）"

# 名前を省略（自動生成）
python3 scripts/copy_element.py 1abc...xyz sheets 123456
```

**成功時の出力:**
```json
{
  "success": true,
  "fileId": "1abc...xyz",
  "fileType": "sheets",
  "operation": "copy",
  "sourceSheetId": 0,
  "newSheetId": 987654321,
  "newSheetName": "売上データ（コピー）",
  "newSheetIndex": 0
}
```

### スライドをコピー

スライドオブジェクトIDはプレゼンテーション情報から取得。

```bash
python3 scripts/copy_element.py 1abc...xyz presentations "g12345" "新しいスライド"
```

**成功時の出力:**
```json
{
  "success": true,
  "fileId": "1abc...xyz",
  "fileType": "presentations",
  "operation": "copy",
  "sourceSlideId": "g12345",
  "duplicatedSlideId": "slide_copy_1705123456789",
  "newSlideTitle": "新しいスライド"
}
```

---

## セル結合（merge_cells.py）

### 基本構文

```bash
python3 scripts/merge_cells.py <fileId> <range>
```

### 使用例

```bash
# A1からB2までのセルを結合
python3 scripts/merge_cells.py 1abc...xyz "Sheet1!A1:B2"

# 日本語シート名もサポート
python3 scripts/merge_cells.py 1abc...xyz "売上!C3:E5"
```

**成功時の出力:**
```json
{
  "success": true,
  "fileId": "1abc...xyz",
  "fileType": "sheets",
  "operation": "merge",
  "sheetName": "Sheet1",
  "sheetId": 0,
  "range": "Sheet1!A1:B2",
  "mergedRange": {
    "startRow": 1,
    "endRow": 2,
    "startCol": 1,
    "endCol": 2
  }
}
```

---

## セル一括結合（merge_cells_batch.py）

複数のセル範囲を1回のスクリプト実行で一括結合する。

### 基本構文

```bash
python3 scripts/merge_cells_batch.py <fileId> <json_ranges>
```

### 使用例

```bash
# 複数範囲を一括結合
python3 scripts/merge_cells_batch.py 1abc...xyz '["Sheet1!A4:A10","Sheet1!B4:B8","Sheet1!C4:C15"]'

# 日本語シート名もサポート
python3 scripts/merge_cells_batch.py 1abc...xyz '["因子表!B4:B15","因子表!C4:C10"]'
```

**成功時の出力:**
```json
{
  "success": true,
  "fileId": "1abc...xyz",
  "fileType": "sheets",
  "operation": "batch_merge",
  "totalRanges": 3,
  "mergedRanges": [
    {
      "range": "Sheet1!A4:A10",
      "sheetId": 0,
      "mergedRange": {"startRow": 4, "endRow": 10, "startCol": 1, "endCol": 1}
    },
    {
      "range": "Sheet1!B4:B8",
      "sheetId": 0,
      "mergedRange": {"startRow": 4, "endRow": 8, "startCol": 2, "endCol": 2}
    },
    {
      "range": "Sheet1!C4:C15",
      "sheetId": 0,
      "mergedRange": {"startRow": 4, "endRow": 15, "startCol": 3, "endCol": 3}
    }
  ]
}
```

**検証エラー時の出力:**
```json
{
  "success": false,
  "fileId": "1abc...xyz",
  "fileType": "sheets",
  "operation": "batch_merge",
  "error": "入力検証エラー",
  "validationErrors": [
    {"range": "Unknown!A1:A5", "error": "シート 'Unknown' が見つかりません"}
  ],
  "availableSheets": ["Sheet1", "因子表"]
}
```

### 単一範囲との使い分け

| ユースケース | 推奨スクリプト |
|-------------|---------------|
| 1つの範囲のみ結合 | `merge_cells.py` |
| 複数範囲を一括結合 | `merge_cells_batch.py` |
| テスト項目書の同一内容セル結合 | `merge_cells_batch.py` |

---

## エラー対応

### 共通エラー

#### 認証エラー

```json
{
  "success": false,
  "error": "認証に失敗しました"
}
```

**対処法**: [SETUP.md](SETUP.md) のセットアップワークフローを実行

#### ファイルが見つからない

```json
{
  "success": false,
  "error": "Requested entity was not found."
}
```

**対処法**: ファイルIDが正しいか確認。URLから正確にコピーすること。

#### 権限エラー

```json
{
  "success": false,
  "error": "The caller does not have permission"
}
```

**対処法**: ファイルへの編集権限があるか確認。必要に応じてファイルオーナーに権限を依頼。

### スプレッドシート固有エラー

#### シートが見つからない

```json
{
  "success": false,
  "fileId": "1abc...xyz",
  "fileType": "sheets",
  "operation": "merge",
  "range": "Unknown!A1:B2",
  "error": "シート \"Unknown\" が見つかりません",
  "availableSheets": ["Sheet1", "売上", "データ"]
}
```

**対処法**: `availableSheets` から正しいシート名を選択

#### 無効な範囲形式

```json
{
  "success": false,
  "error": "無効な範囲形式です。正しい形式: シート名!A1:B2"
}
```

**対処法**: 範囲は `シート名!開始セル:終了セル` の形式で指定

### スライド固有エラー

#### スライドインデックスが範囲外

```json
{
  "success": false,
  "fileId": "1abc...xyz",
  "fileType": "presentations",
  "slideIndex": 10,
  "error": "スライドインデックス 10 は範囲外です（全 5 スライド）"
}
```

**対処法**: 0から始まるインデックスで、存在するスライド番号を指定

#### スライドIDが見つからない

```json
{
  "success": false,
  "sourceSlideId": "invalid_id",
  "error": "指定されたスライドID 'invalid_id' が見つかりません",
  "availableSlides": ["スライド1: g12345", "スライド2: g67890"]
}
```

**対処法**: `availableSlides` から正しいスライドIDを選択

---

## ヒント

### ファイルIDの取得方法

Google DriveファイルのURLから `{fileId}` を抽出：

| ファイルタイプ | URL形式 |
|--------------|---------|
| スプレッドシート | `https://docs.google.com/spreadsheets/d/{fileId}/edit` |
| ドキュメント | `https://docs.google.com/document/d/{fileId}/edit` |
| スライド | `https://docs.google.com/presentation/d/{fileId}/edit` |

### シートIDの取得方法

スプレッドシートのURLの末尾 `#gid=123456` の数値部分がシートID。

### JSON配列の書き方

スプレッドシートへの値挿入では、2次元配列でデータを指定：

```bash
# 1行のデータ
'[["A1の値", "B1の値", "C1の値"]]'

# 複数行のデータ
'[["A1", "B1"], ["A2", "B2"], ["A3", "B3"]]'

# 数値と文字列の混在
'[["商品名", 1000, true]]'
```

### エスケープが必要な場合

シェルで特殊文字を含むテキストを扱う場合：

```bash
# ダブルクォートを含むテキスト
python3 scripts/insert_value.py <fileId> docs -1 '彼は「こんにちは」と言った'

# 改行を含むテキスト
python3 scripts/insert_value.py <fileId> docs -1 $'1行目\n2行目\n3行目'
```
