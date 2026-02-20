---
name: homebrew
description: Homebrewパッケージの一括更新（brew update/upgrade/cleanup + Brewfile生成）、パッケージの追加インストール（brew search/install）、パッケージの削除（brew uninstall/autoremove）、App StoreアプリのHomebrew移行（mas + brew cask）、Mac移行（旧Mac環境エクスポート・新Macセットアップ）を実行する。「brew」「Homebrew」「パッケージ更新」「パッケージ追加」「パッケージ削除」「Brewfile」「brew update」「brew upgrade」「brew install」「brew uninstall」「cask」「App Store移行」「mas」「Homebrewに移行」「Mac移行」「Mac環境構築」「セットアップ」「エクスポート」などのキーワードで自動発動。
allowed-tools: Bash, AskUserQuestion, TodoWrite
user-invocable: true
---

# Homebrew管理スキル

Homebrewパッケージの更新・追加・削除・App Store移行・Mac移行を統括するスキルです。

日本語で回答すること。

## 前提条件

- `brew` コマンドがインストール済み
- macOS環境

確認方法:
```bash
brew --version
```

## ワークフロー概要

**TodoWriteで進捗管理すること:**

```
Homebrew管理進捗:
- [ ] Phase 0: 操作タイプの選択
- [ ] Phase 1-N: (選択されたワークフローに応じて動的に設定)
```

---

## Phase 0: 操作タイプの選択

### 0-1. ユーザーに操作タイプを質問

AskUserQuestionツールで以下の選択肢を提示:

| # | 操作タイプ | 説明 |
|---|-----------|------|
| 1 | 更新 | brew update/upgrade + 不要ファイル削除 + Brewfile生成 |
| 2 | 削除 | インストール済みパッケージの削除 |
| 3 | 追加 | 新しいパッケージの検索・インストール |
| 4 | 移行 | App StoreアプリをHomebrew cask版に移行 |
| 5 | Mac移行 | 旧Macのエクスポート / 新Macのセットアップ |

**注意**: ユーザーの最初の発言から操作タイプが明確に判断できる場合（例: 「brewを更新して」「wgetをインストールして」「nodeを削除して」「App StoreからHomebrewに移行したい」「新Macをセットアップしたい」）は、質問をスキップして該当ワークフローに直接分岐してよい。

### 0-2. 選択に応じて分岐

ユーザーの選択に基づいて、該当するワークフローファイルを参照し実行する:

- **更新を選択** → [WORKFLOW-UPDATE.md](WORKFLOW-UPDATE.md) を参照して実行
- **削除を選択** → [WORKFLOW-DELETE.md](WORKFLOW-DELETE.md) を参照して実行
- **追加を選択** → [WORKFLOW-ADD.md](WORKFLOW-ADD.md) を参照して実行
- **移行を選択** → [WORKFLOW-MIGRATE.md](WORKFLOW-MIGRATE.md) を参照して実行
- **Mac移行を選択** → [WORKFLOW-MAC-MIGRATION.md](WORKFLOW-MAC-MIGRATION.md) を参照して実行

**重要**: 選択されたワークフローに記載されているTodoWriteチェックリストを使用して、Phase 0以降の進捗を管理すること。

---

## 注意事項

- brew コマンドの実行前に、エラーが発生した場合はエラー対応表を参照する
- 削除操作では依存関係を必ず確認してから実行する
- 更新操作の Brewfile 出力先は `~/Brewfile`

## エラー対応（共通）

| エラー | 対応 |
|-------|------|
| `brew: command not found` | Homebrewのインストールを案内: `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"` |
| `Permission denied` | `/opt/homebrew` の所有権を確認: `sudo chown -R $(whoami) /opt/homebrew` |
| ネットワークエラー | ネットワーク接続状況の確認を案内 |

## 発動キーワード

このスキルは以下のキーワードを含む依頼で自動的に発動します:

- **更新関連**: 「brew update」「brew upgrade」「Homebrew更新」「パッケージ更新」「brewアップデート」
- **追加関連**: 「brew install」「パッケージ追加」「インストールしたい」「brewで入れたい」
- **削除関連**: 「brew uninstall」「パッケージ削除」「アンインストール」「brewで消したい」
- **移行関連**: 「App Store移行」「Homebrewに移行」「mas」「caskに移行」「App Storeから移行」
- **Mac移行関連**: 「Mac移行」「Mac環境構築」「新Macセットアップ」「エクスポート」「環境移行」「setup.sh」「export.sh」
- **一般**: 「brew」「Homebrew」「Brewfile」「cask」
