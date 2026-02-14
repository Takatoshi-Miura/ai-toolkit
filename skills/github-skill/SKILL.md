---
name: github-skill
description: GitHub CLI (gh) とGit操作を統合したスキル。Issue 作成・更新・クローズ、PR 作成・取得・diff・コメント・マージ・レビュー、強制プッシュなど、GitHub/Git操作全般を提供。「Issue」「PR」「プルリクエスト」「GitHub」「gh」「強制プッシュ」「force push」「git push」などのキーワードで自動発動。
allowed-tools: Bash
---

# GitHub スキル

GitHub CLI (`gh`) とGit操作を統合したスキルです。
MCP を使わず、`gh` コマンドやGitコマンドで直接操作します。

日本語で回答すること。

## 前提条件

- `gh` コマンドがインストール済み
- `gh auth login` で認証済み

認証状態の確認:
```bash
gh auth status
```

## ワークフロー選択

| やりたいこと | 参照先 |
|---|---|
| Issue を操作したい（作成・一覧・詳細・コメント・クローズ・更新） | [ISSUE.md](ISSUE.md) |
| PR を操作したい（作成・一覧・詳細・diff・コメント・マージ・クローズ・レビュー） | [PULL-REQUEST.md](PULL-REQUEST.md) |
| 強制プッシュしたい（スカッシュやリベース後のリモート上書き） | [GIT-PUSH.md](GIT-PUSH.md) |
| リポジトリ情報取得・JSON出力・共通Tips | [REFERENCE.md](REFERENCE.md) |

## 注意事項

- `--repo owner/repo` は省略可能（カレントディレクトリが git リポジトリの場合）
- 本文に日本語や特殊文字を含む場合は、HEREDOC や `"$(cat <<'EOF' ... EOF)"` を使用
- 認証エラーが出た場合は `gh auth login` で再認証
