---
name: read-google-drive-skill
description: Google Driveファイル（スプレッドシート、ドキュメント、スライド）を読み取る。URLやファイルIDが指定された時、「ドライブ読んで」「スプレッドシート見せて」「ドキュメント確認」「〇〇シートを読んで」「このファイルの内容」などの依頼で使用。
allowed-tools: Bash
user-invocable: true
---

# Google Drive ファイル読み取りスキル

Google Driveのスプレッドシート、ドキュメント、スライドをPythonスクリプトで読み取る。

## 重要：このスキルの使い方

**必ず以下のチェックリストをコピーして、各ステップを順番に実行すること。**
ステップを飛ばしたり、チェックリストなしで進めてはならない。

**制約事項：**
- このスキルはPythonスクリプト（`scripts/read_drive_file.py`）のみを使用する
- Google Drive関連のMCPツールは使用しない
- 認証エラーが発生した場合は、必ず [SETUP.md](SETUP.md) のセットアップワークフローを実行する

## ワークフロー選択

まず状況を判断する：

- **初めて使用する / 認証エラーが発生した？** → [SETUP.md](SETUP.md) を参照
- **ファイルを読み取りたい？** → 以下の「読み取りワークフロー」へ

## 読み取りワークフロー

**【必須】** このチェックリストをコピーして進行状況を追跡（省略不可）：

```
読み取り進捗：
- [ ] ステップ1：URLからファイルIDとタイプを抽出
- [ ] ステップ2：部分指定の有無を判断
- [ ] ステップ3：スクリプトを実行
- [ ] ステップ4：結果を確認（エラー時は対応）
```

### ステップ1：URLからファイルIDとタイプを抽出

URLパターンから `{fileId}` を抽出し、ファイルタイプを特定：

| URL | fileType |
|-----|----------|
| `docs.google.com/spreadsheets/d/{fileId}/edit` | `sheets` |
| `docs.google.com/document/d/{fileId}/edit` | `docs` |
| `docs.google.com/presentation/d/{fileId}/edit` | `presentations` |

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

**詳細な使用例・出力形式**: [READING.md](READING.md) を参照
