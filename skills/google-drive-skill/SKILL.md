---
name: google-drive-skill
description: Google Driveファイル（スプレッドシート、ドキュメント、スライド）の読み取りと書き込みをPythonスクリプトで実行。読み取り、値挿入、シート/スライド作成、要素コピー、セル結合に対応。URLやファイルIDが指定された時、「ドライブ読んで」「スプレッドシート見せて」「ドキュメント確認」「〇〇シートを読んで」「このファイルの内容」「ドライブに書いて」「スプレッドシートに追加」「シート作成」「セル結合」「スライド追加」などの依頼で使用。
allowed-tools: Bash
user-invocable: true
---

# Google Drive ファイル操作スキル

Google Driveのスプレッドシート、ドキュメント、スライドをPythonスクリプトで読み書きする。

日本語で回答すること。

## 制約事項

- このスキルはPythonスクリプト（`scripts/` 配下）のみを使用する
- Google Drive関連のMCPツールは使用しない
- 認証エラーが発生した場合は、必ず [SETUP.md](SETUP.md) のセットアップワークフローを実行する

## 共通：URLからファイルIDとタイプを抽出

全ワークフロー共通のステップ。URLパターンから `{fileId}` を抽出し、ファイルタイプを特定：

| URL | fileType |
|-----|----------|
| `docs.google.com/spreadsheets/d/{fileId}/edit` | `sheets` |
| `docs.google.com/document/d/{fileId}/edit` | `docs` |
| `docs.google.com/presentation/d/{fileId}/edit` | `presentations` |

## ワークフロー選択

状況に応じて適切なワークフローを参照する：

| やりたいこと | 参照先 |
|-------------|--------|
| 初めて使用する / 認証エラーが発生した | [SETUP.md](SETUP.md) |
| ファイルを読み取りたい | [READING.md](READING.md) |
| 値/テキストを挿入したい | [WRITING.md](WRITING.md) の「値挿入ワークフロー」 |
| 新規シート/スライドを作成したい | [WRITING.md](WRITING.md) の「新規作成ワークフロー」 |
| シート/スライドをコピーしたい | [WRITING.md](WRITING.md) の「コピーワークフロー」 |
| セルを結合したい | [WRITING.md](WRITING.md) の「セル結合ワークフロー」 |
| 複数セルを一括結合したい | [WRITING.md](WRITING.md) の「セル一括結合ワークフロー」 |
