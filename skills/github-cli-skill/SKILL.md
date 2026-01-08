---
name: github-cli-skill
description: GitHub CLI (gh) を使った Issue/PR 操作のガイド。Issue 作成・更新・クローズ、PR 作成・取得・diff・コメントなど、gh コマンドの使い方を提供。
allowed-tools: Bash
---

# GitHub CLI スキル

GitHub CLI (`gh`) を使用して Issue や Pull Request を操作するためのガイドです。
MCP を使わず、`gh` コマンドで直接 GitHub API を操作します。

## 前提条件

- `gh` コマンドがインストール済み
- `gh auth login` で認証済み

認証状態の確認:
```bash
gh auth status
```

## Issue 操作

### Issue の作成

```bash
gh issue create --repo owner/repo --title "タイトル" --body "本文"
```

対話形式で作成する場合:
```bash
gh issue create --repo owner/repo
```

### Issue の一覧表示

```bash
# オープン状態の Issue 一覧
gh issue list --repo owner/repo

# 自分がアサインされた Issue
gh issue list --repo owner/repo --assignee @me

# ラベルでフィルタ
gh issue list --repo owner/repo --label "bug"

# 数を指定
gh issue list --repo owner/repo --limit 20
```

### Issue の詳細表示

```bash
gh issue view 123 --repo owner/repo

# コメント含めて表示
gh issue view 123 --repo owner/repo --comments
```

### Issue へのコメント追加

```bash
gh issue comment 123 --repo owner/repo --body "コメント内容"
```

### Issue のクローズ

```bash
gh issue close 123 --repo owner/repo

# 理由付きでクローズ
gh issue close 123 --repo owner/repo --comment "完了しました"
```

### Issue の更新

```bash
# タイトル変更
gh issue edit 123 --repo owner/repo --title "新しいタイトル"

# ラベル追加
gh issue edit 123 --repo owner/repo --add-label "bug,priority:high"

# アサイン
gh issue edit 123 --repo owner/repo --add-assignee @me
```

## Pull Request 操作

### PR の作成

```bash
# 基本的な作成
gh pr create --repo owner/repo --title "タイトル" --body "本文" --base main --head feature-branch

# ドラフトとして作成
gh pr create --repo owner/repo --title "タイトル" --body "本文" --base main --head feature-branch --draft

# 現在のブランチから作成（head 省略可）
gh pr create --title "タイトル" --body "本文" --base main
```

本文に複数行を含める場合（HEREDOC 使用）:
```bash
gh pr create --title "タイトル" --body "$(cat <<'EOF'
## 概要
変更内容の説明

## テスト方法
- [ ] 手動テスト完了
EOF
)" --base main
```

### PR の一覧表示

```bash
# オープン状態の PR 一覧
gh pr list --repo owner/repo

# 自分が作成した PR
gh pr list --repo owner/repo --author @me

# レビュー待ちの PR
gh pr list --repo owner/repo --search "review:required"
```

### PR の詳細表示

```bash
gh pr view 123 --repo owner/repo

# コメント含めて表示
gh pr view 123 --repo owner/repo --comments
```

### PR の diff 表示

```bash
gh pr diff 123 --repo owner/repo

# ファイル名のみ表示
gh pr diff 123 --repo owner/repo --name-only
```

### PR へのコメント追加

```bash
gh pr comment 123 --repo owner/repo --body "コメント内容"
```

### PR のマージ

```bash
# マージ（デフォルト: merge commit）
gh pr merge 123 --repo owner/repo

# Squash マージ
gh pr merge 123 --repo owner/repo --squash

# Rebase マージ
gh pr merge 123 --repo owner/repo --rebase

# マージ後にブランチ削除
gh pr merge 123 --repo owner/repo --delete-branch
```

### PR のクローズ

```bash
gh pr close 123 --repo owner/repo

# コメント付きでクローズ
gh pr close 123 --repo owner/repo --comment "対応不要になったためクローズ"
```

### PR のレビュー

```bash
# 承認
gh pr review 123 --repo owner/repo --approve

# 変更リクエスト
gh pr review 123 --repo owner/repo --request-changes --body "修正が必要です"

# コメントのみ
gh pr review 123 --repo owner/repo --comment --body "LGTMですが、1点確認させてください"
```

## リポジトリ情報の取得

現在のリポジトリの owner/repo を取得:
```bash
gh repo view --json owner,name --jq '"\(.owner.login)/\(.name)"'
```

または git remote から:
```bash
git remote get-url origin | sed -E 's/.*[:/]([^/]+)\/([^/.]+)(\.git)?$/\1\/\2/'
```

## JSON 出力

詳細な情報を JSON で取得する場合:

```bash
# Issue を JSON で取得
gh issue view 123 --repo owner/repo --json number,title,body,state,labels,assignees

# PR を JSON で取得
gh pr view 123 --repo owner/repo --json number,title,body,state,baseRefName,headRefName,mergeable

# Issue 一覧を JSON で取得
gh issue list --repo owner/repo --json number,title,state --limit 50
```

## 注意事項

- `--repo owner/repo` は省略可能（カレントディレクトリが git リポジトリの場合）
- 本文に日本語や特殊文字を含む場合は、HEREDOC や `"$(cat <<'EOF' ... EOF)"` を使用
- 認証エラーが出た場合は `gh auth login` で再認証
