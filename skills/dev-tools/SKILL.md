---
name: dev-tools
description: AndroidデバイスへのAPKインストール、PDFからの画像抽出など開発・作業効率化ツール群。ユーザーが明示的に呼び出して使用するユーティリティスキル。APKインストールは接続端末の確認・選択・インストール実行まで対応。PDF画像抽出は単一PDF・複数PDF一括処理・ディレクトリ指定に対応し抽出後に画像サイズも報告。
allowed-tools: Bash, AskUserQuestion, TodoWrite
user-invocable: true
disable-model-invocation: true
---

# 開発ツール（Dev Tools）

開発・作業効率化のためのユーティリティツール群。
新しいツールを追加する際はこのスキルにワークフローを追加していく。

日本語で回答すること。

## 利用可能なツール

| # | ツール | 説明 |
|---|--------|------|
| 1 | APKインストール | Android端末へのAPKファイルのインストール |
| 2 | PDF画像抽出 | PDFファイルから埋め込み画像を抽出して保存 |

---

## Phase 0: ツールの選択

### 0-1. ユーザーにツールを質問

AskUserQuestionツールで以下の選択肢を提示:

```
どのツールを使用しますか？
1. APKインストール - Android端末にAPKをインストール
2. PDF画像抽出 - PDFから画像を抽出して~/Downloads/に保存
```

**注意**: ユーザーの発言から操作が明確に判断できる場合（例: 「APKインストールして」「PDFから画像を抜き出して」）は、質問をスキップして直接分岐してよい。

### 0-2. 選択に応じて分岐

ユーザーの選択に基づいて、該当するワークフローファイルを参照し実行する:

- **APKインストールを選択** → [WORKFLOW-INSTALL-APK.md](WORKFLOW-INSTALL-APK.md) を参照して実行
- **PDF画像抽出を選択** → [WORKFLOW-EXTRACT-PDF-IMAGES.md](WORKFLOW-EXTRACT-PDF-IMAGES.md) を参照して実行

**重要**: 選択されたワークフローに記載されているTodoWriteチェックリストを使用して、Phase 1以降の進捗を管理すること。

---

## エラー対応（共通）

| エラー | 対応 |
|-------|------|
| コマンドが見つからない | 該当ワークフローの前提条件セクションを確認してインストール手順に従う |
| 権限エラー | `sudo` の使用またはファイル・デバイスの権限を確認する |
| ネットワークエラー | ネットワーク接続状況を確認してから再試行する |

## 詳細ワークフロー

- **APKインストール**: [WORKFLOW-INSTALL-APK.md](WORKFLOW-INSTALL-APK.md)
- **PDF画像抽出**: [WORKFLOW-EXTRACT-PDF-IMAGES.md](WORKFLOW-EXTRACT-PDF-IMAGES.md)
