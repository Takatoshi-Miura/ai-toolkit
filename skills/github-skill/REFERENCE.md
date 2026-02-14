# 共通リファレンス

GitHub CLI (`gh`) 操作で共通して使える便利なコマンドや設定です。

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
