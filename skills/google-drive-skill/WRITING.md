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

## セルハイライトワークフロー

### ステップ1：URLからファイルIDを抽出（共通セクション参照）

### ステップ2：ハイライト範囲と色を決定

形式: `シート名!開始セル:終了セル`（例: `Sheet1!A1:B2`）

色はオプション（デフォルト: yellow）。利用可能な色: yellow, light_yellow, green, light_green, blue, light_blue, red, light_red, orange, none（解除）

### ステップ3：スクリプトを実行

```bash
python3 scripts/highlight_cells.py <fileId> <range> [--color <color_name>]
```

### ステップ4：結果を確認

**成功時**: `"success": true` が出力される → 完了

---

## 行列操作ワークフロー

### ステップ1：URLからファイルIDを抽出（共通セクション参照）

### ステップ2：操作内容を決定

| 項目 | 値 |
|------|-----|
| action | `insert`（挿入）または `delete`（削除） |
| シート名 | 操作対象のシート名 |
| dimension | `rows`（行）または `columns`（列） |
| start | 開始位置（1ベース。行番号または列番号） |
| end | 終了位置（1ベース、包括的。省略時はstartと同じで1行/1列のみ） |

**列番号の対応表**: A=1, B=2, C=3, D=4, ...

### ステップ3：スクリプトを実行

```bash
python3 scripts/manage_dimension.py <fileId> <action> <シート名> <dimension> <start> [end] [--no-inherit]
```

### ステップ4：結果を確認

**成功時**: `"success": true` が出力される → 完了

**エラー時**: 「エラー対応」セクションを参照

---

## シート一括操作ワークフロー（バッチ）

同一スプレッドシートに対して**2つ以上の操作**を連続して行う場合に使用する。
1回の API コールで複数操作をまとめて実行するため、認証とメタデータ取得のオーバーヘッドを最小化できる。

### ステップ1：URLからファイルIDを抽出（共通セクション参照）

### ステップ2：操作リストをJSON配列で構築

各操作を以下の形式のオブジェクトで記述し、配列にまとめる：

| type | 必須パラメータ | オプション |
|------|--------------|-----------|
| `merge` | `range` | -- |
| `highlight` | `range` | `color`（デフォルト: yellow） |
| `insert_dimension` | `sheet`, `dimension`, `start` | `end`（デフォルト: start）, `inheritFromBefore`（デフォルト: true） |
| `delete_dimension` | `sheet`, `dimension`, `start` | `end`（デフォルト: start） |
| `add_sheet` | `title` | -- |
| `duplicate_sheet` | `sourceSheetId` | `newSheetName` |

### ステップ3：スクリプトを実行

```bash
python3 scripts/batch_sheets.py <fileId> '<json_operations>'
```

### ステップ4：結果を確認

**成功時**: `"success": true` と `totalOperations` が出力される → 完了

**エラー時**: `validationErrors` で問題の操作を確認し、修正して再実行

### 制約事項

- `add_sheet` で作成した新規シートへの同バッチ内での後続操作は不可
- 値の挿入（`insert_value.py` の sheets 機能）は別APIのためバッチに含められない
- 操作は指定した順序通りに実行される。行挿入後のセル結合など、順序依存がある場合はインデックスのずれに注意

### 使い分けガイド

| ユースケース | 推奨 |
|-------------|------|
| 単一操作 | 各専用スクリプト |
| 同種の複数操作（セル結合のみ） | `merge_cells_batch.py` または `batch_sheets.py` |
| 異種の複数操作（結合＋ハイライト＋行挿入） | **`batch_sheets.py`** |

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

### セルハイライト（highlight_cells.py）

```bash
python3 scripts/highlight_cells.py 1abc...xyz "Sheet1!A1:B2"
python3 scripts/highlight_cells.py 1abc...xyz "売上!C3:E5" --color light_green
python3 scripts/highlight_cells.py 1abc...xyz "Sheet1!A1:B2" --color none
```

**成功時の出力:**
```json
{
  "success": true,
  "fileId": "1abc...xyz",
  "fileType": "sheets",
  "operation": "highlight",
  "sheetName": "Sheet1",
  "sheetId": 0,
  "range": "Sheet1!A1:B2",
  "color": "yellow",
  "colorRgb": {"red": 1.0, "green": 1.0, "blue": 0.0},
  "highlightedRange": {"startRow": 1, "endRow": 2, "startCol": 1, "endCol": 2}
}
```

#### 色の指定

| 色名 | 用途 |
|------|------|
| `yellow`（デフォルト） | 編集箇所の強調 |
| `light_green` | 完了・正常を示す |
| `light_red` | 要注意箇所の強調 |
| `none` | ハイライト解除（白に戻す） |

---

### 行列操作（manage_dimension.py）

#### 行の挿入（3行目の前に2行挿入）

```bash
python3 scripts/manage_dimension.py 1abc...xyz insert "Sheet1" rows 3 4
```

**成功時の出力:**
```json
{
  "success": true,
  "fileId": "1abc...xyz",
  "fileType": "sheets",
  "operation": "insert_dimension",
  "action": "insert",
  "sheetName": "Sheet1",
  "sheetId": 0,
  "dimension": "rows",
  "start": 3,
  "end": 4,
  "count": 2,
  "inheritFromBefore": true
}
```

#### 列の挿入（B列の前に1列挿入）

```bash
python3 scripts/manage_dimension.py 1abc...xyz insert "Sheet1" columns 2
```

#### 行の削除（3行目から5行目を削除）

```bash
python3 scripts/manage_dimension.py 1abc...xyz delete "Sheet1" rows 3 5
```

**成功時の出力:**
```json
{
  "success": true,
  "fileId": "1abc...xyz",
  "fileType": "sheets",
  "operation": "delete_dimension",
  "action": "delete",
  "sheetName": "Sheet1",
  "sheetId": 0,
  "dimension": "rows",
  "start": 3,
  "end": 5,
  "count": 3
}
```

#### 列の削除（C列を削除）

```bash
python3 scripts/manage_dimension.py 1abc...xyz delete "Sheet1" columns 3
```

#### 書式継承なしで挿入

```bash
python3 scripts/manage_dimension.py 1abc...xyz insert "Sheet1" rows 3 4 --no-inherit
```

---

### シート一括操作（batch_sheets.py）

#### セル結合＋ハイライト＋行挿入を一括実行

```bash
python3 scripts/batch_sheets.py 1abc...xyz '[
  {"type": "merge", "range": "Sheet1!A1:B2"},
  {"type": "highlight", "range": "Sheet1!A1:B2", "color": "light_green"},
  {"type": "insert_dimension", "sheet": "Sheet1", "dimension": "rows", "start": 5, "end": 6}
]'
```

**成功時の出力:**
```json
{
  "success": true,
  "fileId": "1abc...xyz",
  "fileType": "sheets",
  "operation": "batch_sheets",
  "totalOperations": 3,
  "operations": [
    {"index": 0, "type": "merge", "range": "Sheet1!A1:B2", "status": "included"},
    {"index": 1, "type": "highlight", "range": "Sheet1!A1:B2", "color": "light_green", "status": "included"},
    {"index": 2, "type": "insert_dimension", "sheet": "Sheet1", "dimension": "rows", "start": 5, "end": 6, "status": "included"}
  ]
}
```

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
