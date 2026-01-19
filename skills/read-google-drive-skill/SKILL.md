---
name: read-google-drive-skill
description: Read Google Drive files. When a specific part name is mentioned (in quotes, brackets, or as a distinct phrase like "read 〇〇"), check structure first to find matching sheet/tab/page, then read that part. Otherwise read the entire file.
allowed-tools: Bash
---

# Google Drive ファイル読み取りスキル

Google Driveのスプレッドシート、ドキュメント、スライドをPythonスクリプトで高速に読み取ります。

## 環境変数設定

このスキルは以下の環境変数で認証ファイルの場所を指定します：

| 環境変数 | 説明 | デフォルト値 |
|---------|------|-------------|
| `GOOGLE_DRIVE_CONFIG_DIR` | 認証ファイルのディレクトリ | `~/.config/read-google-drive/` |
| `GOOGLE_CREDENTIALS_PATH` | client_secret.jsonのパス | `${CONFIG_DIR}/client_secret.json` |
| `GOOGLE_TOKEN_PATH` | token.jsonのパス | `${CONFIG_DIR}/token.json` |

**優先順位:**
1. `GOOGLE_CREDENTIALS_PATH` / `GOOGLE_TOKEN_PATH`（個別指定）
2. `GOOGLE_DRIVE_CONFIG_DIR` 内のファイル
3. `~/.config/read-google-drive/` 内のファイル（デフォルト）

## CLIスクリプトの使用

### 基本コマンド

```bash
python scripts/read_drive_file.py <fileId> <fileType> [partName]
```

### パラメータ

| パラメータ | 必須 | 説明 |
|----------|------|------|
| `fileId` | ✅ | Google DriveのファイルID |
| `fileType` | ✅ | `docs` / `sheets` / `presentations` |
| `partName` | ❌ | 読み取る部分名（シート名、タブ名、ページ番号） |

### ファイルIDの抽出

URLからファイルIDを抽出する：
- スプレッドシート: `https://docs.google.com/spreadsheets/d/{fileId}/edit`
- ドキュメント: `https://docs.google.com/document/d/{fileId}/edit`
- スライド: `https://docs.google.com/presentation/d/{fileId}/edit`

## 使用例

### 全体読み取り

```bash
# スプレッドシート全体
python scripts/read_drive_file.py 1abc...xyz sheets

# ドキュメント全体
python scripts/read_drive_file.py 1abc...xyz docs

# スライド全体
python scripts/read_drive_file.py 1abc...xyz presentations
```

### 部分読み取り

```bash
# 特定シートを読み取り（シート名指定）
python scripts/read_drive_file.py 1abc...xyz sheets "売上"

# 特定タブを読み取り（タブ名指定）
python scripts/read_drive_file.py 1abc...xyz docs "概要"

# 特定ページを読み取り（ページ番号指定）
python scripts/read_drive_file.py 1abc...xyz presentations 3
```

### 環境変数を指定して実行

```bash
GOOGLE_CREDENTIALS_PATH=/path/to/client_secret.json \
GOOGLE_TOKEN_PATH=/path/to/token.json \
python scripts/read_drive_file.py 1abc...xyz docs
```

## 部分指定の判断ルール

ユーザーが以下のような形式で特定の名前を指定した場合は、**partName引数を追加**する：

- 「〇〇を読んで」（〇〇がファイル全体を指していない場合）
- 「"〇〇"を読んで」（引用符で囲まれている）
- 「『〇〇』を読んで」（カギカッコで囲まれている）
- 「〇〇シートを読んで」
- 「〇〇タブを読んで」
- 「〇ページ目を読んで」

**例：**
- ❌「このドキュメントを読んで」→ partName省略（全体読み取り）
- ✅「売上を読んで」→ partName="売上"
- ✅「3ページ目を見せて」→ partName="3"

## 出力形式

スクリプトはJSON形式で結果を出力します：

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

## エラー時

部分名が見つからない場合、利用可能な選択肢が提示されます：

```json
{
  "error": "シート \"売り上げ\" が見つかりません",
  "availableSheets": ["売上", "経費", "在庫"]
}
```

## セットアップ手順

### 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 初回セットアップ（配布版）

1. Google Cloud Consoleでプロジェクトを作成し、OAuth認証情報を取得
2. 認証ファイルを配置：
   ```bash
   mkdir -p ~/.config/read-google-drive
   cp /path/to/client_secret.json ~/.config/read-google-drive/
   ```
3. 初回認証でtoken.jsonを生成（別途認証フローが必要）

### 既存の認証を利用する場合

環境変数で既存の認証ファイルを指定：
```bash
export GOOGLE_CREDENTIALS_PATH=/path/to/existing/client_secret.json
export GOOGLE_TOKEN_PATH=/path/to/existing/token.json
```
