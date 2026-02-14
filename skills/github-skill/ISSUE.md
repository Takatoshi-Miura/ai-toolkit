# Issue 操作

GitHub CLI (`gh`) を使用した Issue 操作のリファレンスです。

## Issue の作成

```bash
gh issue create --repo owner/repo --title "タイトル" --body "本文"
```

対話形式で作成する場合:
```bash
gh issue create --repo owner/repo
```

## Issue の一覧表示

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

## Issue の詳細表示

```bash
gh issue view 123 --repo owner/repo

# コメント含めて表示
gh issue view 123 --repo owner/repo --comments
```

## Issue へのコメント追加

```bash
gh issue comment 123 --repo owner/repo --body "コメント内容"
```

## Issue のクローズ

```bash
gh issue close 123 --repo owner/repo

# 理由付きでクローズ
gh issue close 123 --repo owner/repo --comment "完了しました"
```

## Issue の更新

```bash
# タイトル変更
gh issue edit 123 --repo owner/repo --title "新しいタイトル"

# ラベル追加
gh issue edit 123 --repo owner/repo --add-label "bug,priority:high"

# アサイン
gh issue edit 123 --repo owner/repo --add-assignee @me
```
