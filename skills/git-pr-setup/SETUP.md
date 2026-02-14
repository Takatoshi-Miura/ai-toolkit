# Git PR準備スキル - セットアップ

## 必要条件

- Git がインストールされていること
- GitHub CLI (`gh`) がインストールされ、認証済みであること
- Python 3.x がインストールされていること

---

## GitHub CLI セットアップ

### インストール

```bash
# macOS
brew install gh

# その他: https://cli.github.com/
```

### 認証

```bash
gh auth login
```

ブラウザで認証フローを完了してください。

### 認証確認

```bash
gh auth status
```

---

## Redmineコメント機能の設定（任意）

Redmineへのコメント追加機能を使用する場合、設定ファイルを作成してください。

**注意**: この設定がなくても、他の機能（ブランチ作成、PR作成等）は正常に動作します。

### 設定ファイルパス

```
~/.config/redmine-skill/config.json
```

### 設定ファイルの内容

```json
{
  "url": "https://redmine.example.com",
  "api_key": "your-api-key-here"
}
```

### セットアップ手順

1. **設定ディレクトリを作成**

```bash
mkdir -p ~/.config/redmine-skill
```

2. **設定ファイルを作成**

```bash
cat > ~/.config/redmine-skill/config.json << 'EOF'
{
  "url": "https://your-redmine-server.com",
  "api_key": "your-api-key"
}
EOF
```

3. **URLとAPIキーを編集**

```bash
# エディタで編集
nano ~/.config/redmine-skill/config.json
# または
code ~/.config/redmine-skill/config.json
```

### APIキーの取得方法

1. Redmineにログイン
2. 右上の「個人設定」をクリック
3. 「APIアクセスキー」セクションで「表示」をクリック
4. 表示されたキーをコピー

### 設定の確認

```bash
cat ~/.config/redmine-skill/config.json
```

---

## トラブルシューティング

| 問題 | 解決方法 |
|------|---------|
| `gh` コマンドが見つからない | `brew install gh` でインストール |
| GitHub認証エラー | `gh auth login` で再認証 |
| Redmineコメントがスキップされる | 設定ファイルが存在するか確認 |
| Redmine認証エラー | APIキーが正しいか確認、URLの末尾にスラッシュがないか確認 |
| `python3` が見つからない | `brew install python3` (macOS) |

---

## スクリプトの動作確認

各スクリプトは単体でテスト可能です：

```bash
# ブランチ作成テスト（実際にブランチが作成される）
python3 ~/.claude/skills/git-pr-setup/scripts/create_branch.py test 12345 test_branch

# Redmine設定確認
python3 -c "
import sys
sys.path.insert(0, '$HOME/.claude/skills/git-pr-setup/scripts')
from redmine_auth import is_configured, get_config
print('設定済み:', is_configured())
if is_configured():
    config = get_config()
    print('URL:', config.get('url'))
"
```
