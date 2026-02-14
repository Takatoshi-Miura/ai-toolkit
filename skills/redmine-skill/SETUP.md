# Redmineスキル - セットアップ

## 前提条件

- Python 3.x がインストールされていること

---

## 設定ファイルパス

```
~/.config/redmine-skill/config.json
```

## 設定ファイルの内容

```json
{
  "url": "https://redmine.example.com",
  "api_key": "your-api-key-here"
}
```

## 認証の共有について

このスキルは `git-pr-setup` スキルと同じ設定ファイルパスを使用します。
既に `git-pr-setup` でRedmine設定済みの場合、追加の設定は不要です。

---

## セットアップ手順

### 1. 設定ディレクトリを作成

```bash
mkdir -p ~/.config/redmine-skill
```

### 2. 設定ファイルを作成

```bash
cat > ~/.config/redmine-skill/config.json << 'EOF'
{
  "url": "https://your-redmine-server.com",
  "api_key": "your-api-key"
}
EOF
```

### 3. URLとAPIキーを編集

```bash
nano ~/.config/redmine-skill/config.json
```

## APIキーの取得方法

1. Redmineにログイン
2. 右上の「個人設定」をクリック
3. 「APIアクセスキー」セクションで「表示」をクリック
4. 表示されたキーをコピー

---

## セットアップ確認

```bash
python3 ~/.claude/skills/redmine-skill/scripts/redmine_auth.py
```

成功時の出力例:
```json
{"configured": true, "config_path": "/Users/xxx/.config/redmine-skill/config.json", "url": "https://redmine.example.com", "api_key_set": true}
```

---

## トラブルシューティング

| 問題 | 解決方法 |
|------|---------|
| `python3` が見つからない | `brew install python3` (macOS) |
| `configured: false` と表示される | 設定ファイルが存在するか、`url` と `api_key` が設定されているか確認 |
| Redmine認証エラー (HTTP 403) | APIキーが正しいか確認 |
| 接続エラー | `url` が正しいか確認、末尾にスラッシュがないか確認 |
