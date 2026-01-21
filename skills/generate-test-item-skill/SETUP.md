# テスト項目書作成スキル - セットアップ

## 前提条件

このスキルはGoogle Drive APIを使用するPythonスクリプトを含んでいます。

## セットアップ確認

認証が正しく設定されているか確認：

```bash
# 読み取りテスト
python3 ~/.claude/skills/generate-test-item-skill/scripts/read_drive_file.py 1fpcWeiNCIefrUXN9567iopHxPGpB4VUKQ5uxr9CznVo docs
```

**成功時**: ファイル内容がJSON形式で出力される

**エラー時**: 以下のセットアップを実行

---

## 認証設定（エラー時のみ）

### 認証ファイルの配置先

```
~/.config/google-drive-skills/
├── client_secret.json   # Google Cloud Console から取得
└── token.json           # 初回認証時に自動生成
```

### client_secret.json の取得方法

1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. プロジェクトを作成または選択
3. 「APIとサービス」→「認証情報」を開く
4. 「認証情報を作成」→「OAuth クライアント ID」
5. アプリケーションの種類: 「デスクトップアプリ」
6. JSONをダウンロードして `~/.config/google-drive-skills/client_secret.json` に配置

### 必要なAPIの有効化

Google Cloud Consoleで以下のAPIを有効化：
- Google Sheets API
- Google Docs API
- Google Slides API
- Google Drive API

### トークン期限切れ時の対処

```bash
# 古いトークンを削除
rm ~/.config/google-drive-skills/token.json

# 再認証（ブラウザが開く）
python3 ~/.claude/skills/generate-test-item-skill/scripts/read_drive_file.py <任意のfileId> docs
```

---

## 依存パッケージ

```bash
pip install google-auth google-auth-oauthlib google-api-python-client
```

---

## トラブルシューティング

| エラー | 対応 |
|-------|------|
| `ModuleNotFoundError` | 上記の `pip install` を実行 |
| `Token has been expired` | token.json を削除して再認証 |
| `invalid_grant` | token.json を削除して再認証 |
| `Access denied` | Google Cloud Console でスコープを確認 |
