# PDF画像抽出 ワークフロー

PDFファイルから埋め込み画像を抽出し、`~/Downloads/` に保存する詳細手順。
抽出後、各画像のサイズ（幅x高さ）も取得して報告する。

## 対応パターン

| パターン | 入力例 | 動作 |
|---------|--------|------|
| 単一PDF | `/path/to/file.pdf` | 1ファイルから画像抽出 |
| 複数PDF | `/path/to/*.pdf` または複数パス指定 | 一括で全PDFから画像抽出 |
| ディレクトリ | `/path/to/pdfs/` | ディレクトリ内の全PDFを処理 |

---

## TodoWriteチェックリスト

このワークフロー開始時に以下をTodoWriteで登録すること:

```json
[
  {"content": "Phase 1: pdfimagesの確認・インストール", "activeForm": "pdfimagesを確認中", "status": "pending"},
  {"content": "Phase 2: PDFパスの解析", "activeForm": "PDFパスを解析中", "status": "pending"},
  {"content": "Phase 3: 画像抽出の実行", "activeForm": "画像を抽出中", "status": "pending"},
  {"content": "Phase 4: 画像サイズの取得", "activeForm": "画像サイズを取得中", "status": "pending"},
  {"content": "Phase 5: 結果の報告", "activeForm": "結果を報告中", "status": "pending"}
]
```

---

## Phase 1: pdfimagesの確認・自動インストール

### 1-1. pdfimagesの存在確認

```bash
which pdfimages || brew install poppler
```

未インストールの場合は自動でインストールする。

**成功確認**: `pdfimages` コマンドが使用可能になった → Phase 2へ

---

## Phase 2: PDFパスの解析

### 2-1. ユーザーから受け取ったパスを解析

- **単一ファイル** (`.pdf` で終わる): そのまま処理リストに追加
- **ワイルドカード** (`*.pdf` を含む): シェルで展開してループ処理
- **ディレクトリ**: 配下の全 `.pdf` ファイルを取得してループ処理

```bash
# ディレクトリの場合
find /path/to/directory -name "*.pdf" -maxdepth 1
```

**成功確認**: 処理対象のPDFファイル一覧が確定した → Phase 3へ

---

## Phase 3: 画像抽出の実行

### 3-1. 画像を抽出

**単一PDFの場合:**

```bash
pdfimages -j "<PDFパス>" ~/Downloads/<ファイル名>-
```

**複数PDF・ディレクトリの場合:**

```bash
for pdf in /path/to/*.pdf; do
  name=$(basename "${pdf%.pdf}")
  pdfimages -j "$pdf" ~/Downloads/"$name"-
done
```

**成功確認**: 抽出コマンドが完了した（エラーなし） → Phase 4へ

---

## Phase 4: 画像サイズの取得

### 4-1. sipsコマンドで各画像サイズを取得

```bash
for img in ~/Downloads/<prefix>-*; do
  w=$(sips -g pixelWidth "$img" 2>/dev/null | awk '/pixelWidth/{print $2}')
  h=$(sips -g pixelHeight "$img" 2>/dev/null | awk '/pixelHeight/{print $2}')
  echo "$(basename "$img"): ${w}x${h}"
done
```

**成功確認**: 全画像のサイズ情報が取得できた → Phase 5へ

---

## Phase 5: 結果の報告

処理結果をMarkdownテーブル形式でまとめて報告する。

### 出力形式

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

画像がない場合は「0件（埋め込み画像なし）」と報告する。

**成功確認**: 結果サマリーを表示した → 完了

---

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
- 出力先は固定で `~/Downloads/`
