# Pull Request 操作

GitHub CLI (`gh`) を使用した Pull Request 操作のリファレンスです。

## PR の作成

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

## PR の一覧表示

```bash
# オープン状態の PR 一覧
gh pr list --repo owner/repo

# 自分が作成した PR
gh pr list --repo owner/repo --author @me

# レビュー待ちの PR
gh pr list --repo owner/repo --search "review:required"
```

## PR の詳細表示

```bash
gh pr view 123 --repo owner/repo

# コメント含めて表示
gh pr view 123 --repo owner/repo --comments
```

## PR の diff 表示

```bash
gh pr diff 123 --repo owner/repo

# ファイル名のみ表示
gh pr diff 123 --repo owner/repo --name-only
```

## PR へのコメント追加

```bash
gh pr comment 123 --repo owner/repo --body "コメント内容"
```

## PR のマージ

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

## PR のクローズ

```bash
gh pr close 123 --repo owner/repo

# コメント付きでクローズ
gh pr close 123 --repo owner/repo --comment "対応不要になったためクローズ"
```

## PR のレビュー

```bash
# 承認
gh pr review 123 --repo owner/repo --approve

# 変更リクエスト
gh pr review 123 --repo owner/repo --request-changes --body "修正が必要です"

# コメントのみ
gh pr review 123 --repo owner/repo --comment --body "LGTMですが、1点確認させてください"
```
