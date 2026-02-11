# 書き込みワークフロー

## 値挿入ワークフロー

### ステップ1：URLからファイルIDとタイプを抽出

[SKILL.md](SKILL.md) の「共通：URLからファイルIDとタイプを抽出」を参照。

### ステップ2：挿入内容と位置を決定

| fileType | target | content |
|----------|--------|---------|
| sheets | 範囲（例: `Sheet1!A1`） | JSON配列（例: `[["値1","値2"]]`） |
| docs | 文字位置（`-1`で末尾） | テキスト |
| presentations | スライド番号（0始まり） | テキスト |

### ステップ3：スクリプトを実行

```bash
python3 scripts/insert_value.py <fileId> <fileType> <target> <content> [options]
```

**オプション：**
- `--append`: sheets で末尾に追加
- `--bounds '{"x":100,"y":100,"width":400,"height":100}'`: presentations でテキストボックスの位置指定
- `--tab-id <tabId>`: docs でタブ指定

### ステップ4：結果を確認

**成功時**: `"success": true` が出力される → 完了

**エラー時**: 「エラー対応」セクションを参照

---

## 新規作成ワークフロー

### ステップ1：URLからファイルIDとタイプを抽出（共通セクション参照）

### ステップ2：新規要素の名前を決定

| fileType | 作成対象 |
|----------|----------|
| sheets | 新規シート |
| presentations | 新規スライド |
| docs | API制限により未サポート |

### ステップ3：スクリプトを実行

```bash
python3 scripts/create_element.py <fileId> <fileType> <name>
```

### ステップ4：結果を確認

**成功時**: `"success": true` と新規要素のIDが出力される → 完了

---

## コピーワークフロー

### ステップ1：URLからファイルIDとタイプを抽出（共通セクション参照）

### ステップ2：コピー元のIDを特定

| fileType | sourceId の形式 |
|----------|-----------------|
| sheets | シートID（数値） |
| presentations | スライドオブジェクトID（文字列） |

**シートIDの確認方法**: スプレッドシートを開いた時のURLの `#gid=123456` の数値部分

### ステップ3：スクリプトを実行

```bash
python3 scripts/copy_element.py <fileId> <fileType> <sourceId> [newName]
```

### ステップ4：結果を確認

**成功時**: `"success": true` とコピー先のIDが出力される → 完了

---

## セル結合ワークフロー

### ステップ1：URLからファイルIDを抽出（共通セクション参照）

### ステップ2：結合範囲を決定

形式: `シート名!開始セル:終了セル`（例: `Sheet1!A1:B2`）

### ステップ3：スクリプトを実行

```bash
python3 scripts/merge_cells.py <fileId> <range>
```

### ステップ4：結果を確認

**成功時**: `"success": true` が出力される → 完了

---

## セル一括結合ワークフロー

### ステップ1：URLからファイルIDを抽出（共通セクション参照）

### ステップ2：結合範囲のリストを作成

JSON配列形式で結合したい範囲をすべてリストアップ：

```json
["シート名!A4:A10", "シート名!A11:A20", "シート名!B4:B8"]
```

### ステップ3：スクリプトを実行

```bash
python3 scripts/merge_cells_batch.py <fileId> '<json_ranges>'
```

### ステップ4：結果を確認

**成功時**: `"success": true` と結合された範囲数（`totalRanges`）が出力される → 完了

**エラー時**: `validationErrors` で問題の範囲を確認し、修正して再実行

---

## 使用例と出力形式

### 値挿入（insert_value.py）

#### スプレッドシート - 範囲指定で値を挿入

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

#### スプレッドシート - 末尾に行を追加（--append）

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

#### ドキュメント - 末尾にテキストを挿入

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

#### ドキュメント - 特定位置・特定タブにテキストを挿入

```bash
python3 scripts/insert_value.py 1abc...xyz docs 50 "挿入テキスト"
python3 scripts/insert_value.py 1abc...xyz docs -1 "テキスト" --tab-id "t.abc123"
```

#### スライド - テキストボックスを追加

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
  "bounds": {"x": 100, "y": 100, "width": 400, "height": 100},
  "textLength": 14
}
```

#### スライド - 位置とサイズを指定

```bash
python3 scripts/insert_value.py 1abc...xyz presentations 0 "テキスト" --bounds '{"x":200,"y":300,"width":500,"height":150}'
```

---

### 新規作成（create_element.py）

#### 新規シート作成

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

#### 新規スライド作成

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

---

### 要素コピー（copy_element.py）

#### シートをコピー

シートIDはスプレッドシートのURL `#gid=123456` の数値部分。

```bash
python3 scripts/copy_element.py 1abc...xyz sheets 0 "売上データ（コピー）"
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

#### スライドをコピー

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

### セル結合（merge_cells.py）

```bash
python3 scripts/merge_cells.py 1abc...xyz "Sheet1!A1:B2"
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
  "mergedRange": {"startRow": 1, "endRow": 2, "startCol": 1, "endCol": 2}
}
```

---

### セル一括結合（merge_cells_batch.py）

```bash
python3 scripts/merge_cells_batch.py 1abc...xyz '["Sheet1!A4:A10","Sheet1!B4:B8","Sheet1!C4:C15"]'
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
    {"range": "Sheet1!A4:A10", "sheetId": 0, "mergedRange": {"startRow": 4, "endRow": 10, "startCol": 1, "endCol": 1}},
    {"range": "Sheet1!B4:B8", "sheetId": 0, "mergedRange": {"startRow": 4, "endRow": 8, "startCol": 2, "endCol": 2}},
    {"range": "Sheet1!C4:C15", "sheetId": 0, "mergedRange": {"startRow": 4, "endRow": 15, "startCol": 3, "endCol": 3}}
  ]
}
```

#### 単一範囲との使い分け

| ユースケース | 推奨スクリプト |
|-------------|---------------|
| 1つの範囲のみ結合 | `merge_cells.py` |
| 複数範囲を一括結合 | `merge_cells_batch.py` |

---

## エラー対応

### 共通エラー

| エラー | 対応 |
|-------|------|
| 認証エラー | [SETUP.md](SETUP.md) のセットアップワークフローを実行 |
| `Requested entity was not found.` | ファイルIDが正しいか確認 |
| `The caller does not have permission` | ファイルへの編集権限を確認 |

### スプレッドシート固有エラー

| エラー | 対応 |
|-------|------|
| シートが見つからない | `availableSheets` から正しいシート名を選択 |
| 無効な範囲形式 | `シート名!開始セル:終了セル` の形式で指定 |

### スライド固有エラー

| エラー | 対応 |
|-------|------|
| スライドインデックスが範囲外 | 0始まりで存在するスライド番号を指定 |
| スライドIDが見つからない | `availableSlides` から正しいIDを選択 |

---

## ヒント

### JSON配列の書き方

スプレッドシートへの値挿入では、2次元配列でデータを指定：

```bash
# 1行のデータ
'[["A1の値", "B1の値", "C1の値"]]'

# 複数行のデータ
'[["A1", "B1"], ["A2", "B2"], ["A3", "B3"]]'
```

### エスケープが必要な場合

```bash
# ダブルクォートを含むテキスト
python3 scripts/insert_value.py <fileId> docs -1 '彼は「こんにちは」と言った'

# 改行を含むテキスト
python3 scripts/insert_value.py <fileId> docs -1 $'1行目\n2行目\n3行目'
```
