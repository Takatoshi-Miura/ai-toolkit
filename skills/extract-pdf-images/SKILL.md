---
name: extract-pdf-images
description: PDFファイルから画像を抽出して~/Downloads/に保存する。pdfimagesコマンドを使用し、抽出後に各画像のサイズ（幅x高さ）も取得して報告。単一PDF・複数PDF一括変換に対応。「PDF画像抽出」「PDFから画像を取り出す」「PDF内の画像を保存」「画像を抜き出して」「PDFの図を抽出」「埋め込み画像を取得」「PDFから画像」などの依頼で使用。
allowed-tools: Bash
user-invocable: true
---

# PDF画像抽出スキル

PDFファイルから埋め込み画像を抽出し、`~/Downloads/` に保存する。
抽出後、各画像のサイズ（幅x高さ）も取得して報告する。

## 発動条件

このスキルは以下の状況で自動的に適用されます：

- PDFファイルから画像を抽出したいという依頼があった時
- 「PDF画像抽出」「PDFから画像を取り出す」「PDF内の画像を保存」などのキーワード
- 「埋め込み画像」「図を抽出」「画像を抜き出して」などの表現
- 複数PDFの一括処理を依頼された時

## 対応パターン

| パターン | 入力例 | 動作 |
|---------|--------|------|
| 単一PDF | `/path/to/file.pdf` | 1ファイルから画像抽出 |
| 複数PDF | `/path/to/*.pdf` または複数パス指定 | 一括で全PDFから画像抽出 |
| ディレクトリ | `/path/to/pdfs/` | ディレクトリ内の全PDFを処理 |

## 手順

### 1. pdfimagesの確認・自動インストール

```bash
which pdfimages || brew install poppler
```

未インストールの場合は自動でインストールする。

### 2. PDFパスの解析

ユーザーから受け取ったパスを解析：

- **単一ファイル**: そのまま処理
- **ワイルドカード**（`*.pdf`）: 展開してループ処理
- **ディレクトリ**: 配下の全PDFを取得してループ処理

### 3. 画像抽出の実行

**単一PDFの場合:**
```bash
pdfimages -j "<PDFパス>" ~/Downloads/<ファイル名>-
```

**複数PDFの場合:**
```bash
for pdf in /path/to/*.pdf; do
  name=$(basename "${pdf%.pdf}")
  pdfimages -j "$pdf" ~/Downloads/"$name"-
done
```

**ディレクトリ指定の場合:**
```bash
for pdf in /path/to/directory/*.pdf; do
  name=$(basename "${pdf%.pdf}")
  pdfimages -j "$pdf" ~/Downloads/"$name"-
done
```

### 4. 画像サイズの取得

macOSの`sips`コマンドで各画像のサイズを取得：

```bash
for img in ~/Downloads/<prefix>-*; do
  w=$(sips -g pixelWidth "$img" 2>/dev/null | awk '/pixelWidth/{print $2}')
  h=$(sips -g pixelHeight "$img" 2>/dev/null | awk '/pixelHeight/{print $2}')
  echo "$(basename "$img"): ${w}x${h}"
done
```

### 5. 結果を報告

処理結果をまとめて報告する。

## 出力形式

```markdown
## 画像抽出完了

### 処理結果
- **処理PDF数**: X件
- **抽出画像数**: Y件
- **出力先**: ~/Downloads/

### 抽出されたファイル

#### document1.pdf
| ファイル名 | サイズ |
|-----------|--------|
| document1-000.jpg | 1920x1080 |
| document1-001.jpg | 800x600 |

#### document2.pdf
| ファイル名 | サイズ |
|-----------|--------|
| document2-000.png | 3840x2160 |
```

## pdfimagesオプション

| オプション | 説明 |
|-----------|------|
| `-j` | JPEG画像をJPEGファイルとして保存（推奨） |
| `-png` | デフォルト出力形式をPNGに変更 |
| `-all` | 全形式を元の形式で保存 |
| `-p` | ファイル名にページ番号を含める |
| `-f <n>` | 開始ページ指定 |
| `-l <n>` | 終了ページ指定 |
| `-list` | 抽出せず画像一覧を表示 |

## 注意事項

- pdfimagesはpoppler-utilsパッケージに含まれる
- 出力ファイル名は `<PDFベース名>-NNN.<ext>` 形式
- 画像がない場合は0件として報告
- 出力先は固定で `~/Downloads/`
- 日本語で回答すること
