---
name: read-google-drive-skill
description: Read Google Drive files. When a specific part name is mentioned (in quotes, brackets, or as a distinct phrase like "read 〇〇"), check structure first to find matching sheet/tab/page, then read that part. Otherwise read the entire file.
allowed-tools: mcp__mcp-google-drive__g_drive_read_file, mcp__mcp-google-drive__g_drive_read_file_part, mcp__mcp-google-drive__g_drive_get_file_structure
---

# Google Drive ファイル読み取りスキル

Google Driveのスプレッドシート、ドキュメント、スライドを適切なツールを使い分けて読み取ります。

## 重要：部分指定の判断ルール

ユーザーが以下のような形式で特定の名前を指定した場合は、**必ず構造確認→部分読み取り**を行う：

- 「〇〇を読んで」（〇〇がファイル全体を指していない場合）
- 「"〇〇"を読んで」（引用符で囲まれている）
- 「『〇〇』を読んで」（カギカッコで囲まれている）
- 「〇〇シートを読んで」
- 「〇〇タブを読んで」
- 「〇ページ目を読んで」

**例：**
- ❌「このドキュメントを読んで」→ 全体読み取り
- ✅「ワークフロー入力できるを読んで」→ 部分読み取り（タブ名として検索）
- ✅「売上を読んで」→ 部分読み取り（シート名として検索）

## 対応ファイルタイプ

| ファイルタイプ | fileType値 | 部分指定パラメータ |
|--------------|-----------|------------------|
| スプレッドシート | `sheets` | `range`（例: `シート名!A1:Z100`） |
| ドキュメント | `docs` | `tabId`（タブID） |
| スライド | `presentations` | `pageNumber`（1から開始） |

## 読み取り手順

### 1. ファイルIDの取得

URLからファイルIDを抽出する：
- スプレッドシート: `https://docs.google.com/spreadsheets/d/{fileId}/edit`
- ドキュメント: `https://docs.google.com/document/d/{fileId}/edit`
- スライド: `https://docs.google.com/presentation/d/{fileId}/edit`

### 2. 読み取り方法の判断

```
ユーザーが特定の部分名を指定した？（上記の判断ルール参照）
├─ YES → 構造確認 + 部分読み取り（手順3へ）
└─ NO  → 全体読み取り（手順4へ）
```

### 3. 部分読み取り（部分名が指定された場合）

#### 3-1. スプレッドシートの場合

1. `g_drive_get_file_structure` でシート一覧を取得
2. 指定された名前に一致または部分一致するシートを探す
3. `g_drive_read_file_part` で該当シートを読み取り
   - `range`: `シート名!A1:Z1000`（必要に応じて範囲調整）

```
例: 「売上を読んで」
→ g_drive_get_file_structure(fileId, "sheets")
→ 「売上」に一致するシートを探す
→ g_drive_read_file_part(fileId, "sheets", range="売上!A1:Z1000")
```

#### 3-2. ドキュメントの場合

1. `g_drive_get_file_structure` でタブ一覧を取得
2. 指定された名前に一致または部分一致するタブを探す
3. `g_drive_read_file_part` で該当タブを読み取り

```
例: 「ワークフロー入力できるを読んで」
→ g_drive_get_file_structure(fileId, "docs")
→ 「ワークフロー入力できる」に一致するタブを探す
→ g_drive_read_file_part(fileId, "docs", tabId="取得したtabId")
```

#### 3-3. スライドの場合

1. `g_drive_read_file_part` で指定ページを読み取り
   - `pageNumber`: 指定された番号（1から開始）

```
例: 「3ページ目を見せて」
→ g_drive_read_file_part(fileId, "presentations", pageNumber=3)
```

### 4. 全体読み取り（特に指定がない場合）

`g_drive_read_file` でファイル全体を読み取り

```
例: 「このスプレッドシートを読んで」
→ g_drive_read_file(fileId, "sheets")
```

## 注意事項

- スプレッドシートの範囲指定では、シート名に空白や特殊文字が含まれる場合はシングルクォートで囲む（例: `'売上 2024'!A1:Z100`）
- ドキュメントのタブ名とtabIdは異なるため、必ず構造取得でtabIdを確認する
- スライドのページ番号は1から開始（0ではない）
- 名前が一致しない場合は、ユーザーに確認するか、利用可能な選択肢を提示する

## Google認証エラー時

認証エラーが発生した場合は、以下のコマンドで再認証を行う：

```bash
cd ~/Documents/Git/MCP-GoogleDrive && npm run auth
```
