# 初回セットアップ

このスキルを使用するための環境セットアップ手順。

## 認証の共有について

このスキルは `read-google-drive-skill` と認証設定を共有する。
既に `read-google-drive-skill` をセットアップ済みの場合、追加の認証設定は不要。

**共有される認証ファイル**:
- `~/.config/google-drive-skills/client_secret.json`
- `~/.config/google-drive-skills/token.json`

## セットアップワークフロー

このチェックリストをコピーして進行状況を追跡：

```
セットアップ進捗：
- [ ] ステップ1：依存関係をインストール
- [ ] ステップ2：認証ファイルを配置（未設定の場合）
- [ ] ステップ3：書き込み権限を確認
- [ ] ステップ4：動作確認
```

### ステップ1：依存関係をインストール

```bash
pip install google-api-python-client google-auth google-auth-oauthlib google-auth-httplib2
```

**検証**: エラーなく完了すればOK。`ModuleNotFoundError` が発生する場合は再実行。

### ステップ2：認証ファイルを配置（未設定の場合）

`read-google-drive-skill` を既にセットアップ済みならこのステップはスキップ。

以下の2つのファイルが必要：

| ファイル | 説明 |
|---------|------|
| `client_secret.json` | Google Cloud ConsoleのOAuth 2.0クライアントID |
| `token.json` | 認証済みアクセストークン |

**配置先ディレクトリ**: `~/.config/google-drive-skills/`

```bash
mkdir -p ~/.config/google-drive-skills
cp /path/to/client_secret.json ~/.config/google-drive-skills/
cp /path/to/token.json ~/.config/google-drive-skills/
```

### ステップ3：書き込み権限を確認

書き込み操作には適切なOAuthスコープが必要。以下のスコープが `token.json` に含まれていることを確認：

| 操作 | 必要なスコープ |
|------|---------------|
| スプレッドシート書き込み | `https://www.googleapis.com/auth/spreadsheets` |
| ドキュメント書き込み | `https://www.googleapis.com/auth/documents` |
| スライド書き込み | `https://www.googleapis.com/auth/presentations` |

**注意**: 読み取り専用スコープ（`.readonly` サフィックス付き）では書き込み操作は失敗する。

スコープが不足している場合は `token.json` を削除し、適切なスコープで再認証を実行。

### ステップ4：動作確認

任意のスプレッドシートで書き込みテストを実行：

```bash
# テスト用の値を挿入
python3 scripts/insert_value.py <テスト用fileId> sheets "Sheet1!A1" '[["テスト"]]'
```

**成功時**: `"success": true` を含むJSONが出力される
**失敗時**: エラーメッセージを確認し、トラブルシューティングを参照

## トラブルシューティング

### python3: command not found

```
python3: command not found
```

**対応**（OS別）:

| OS | インストール方法 |
|----|-----------------|
| macOS | `brew install python3` または [python.org](https://www.python.org/downloads/) からダウンロード |
| Ubuntu/Debian | `sudo apt install python3` |
| Windows | [python.org](https://www.python.org/downloads/) からダウンロード（「Add to PATH」にチェック） |

**検証**: `python3 --version` でバージョンが表示されればOK

### 認証に失敗しました

```json
{
  "success": false,
  "error": "認証に失敗しました"
}
```

**対応**:
1. `~/.config/google-drive-skills/` ディレクトリに認証ファイルがあるか確認
2. `client_secret.json` と `token.json` の両方が存在するか確認
3. ファイルの読み取り権限があるか確認

### 権限エラー（書き込み不可）

```json
{
  "success": false,
  "error": "The caller does not have permission"
}
```

**対応**:
1. 対象ファイルへの編集権限があるか確認
2. OAuth スコープが書き込み可能か確認（`.readonly` スコープでないこと）
3. 必要に応じて `token.json` を再生成

### トークンの有効期限切れ

**対応**: スクリプトが自動でリフレッシュを試みる。失敗する場合は `token.json` を削除して再認証。

### ModuleNotFoundError

```
ModuleNotFoundError: No module named 'google'
```

**対応**: ステップ1の依存関係インストールを再実行

### シートが見つかりません

```json
{
  "success": false,
  "error": "シート \"Unknown\" が見つかりません",
  "availableSheets": ["Sheet1", "売上"]
}
```

**対応**: `availableSheets` に表示されている正しいシート名を使用

## 認証ファイルの再生成

書き込み権限を含む新しいトークンを生成する場合：

1. `~/.config/google-drive-skills/token.json` を削除
2. 以下のスコープを含むOAuth認証フローを実行：
   ```
   https://www.googleapis.com/auth/spreadsheets
   https://www.googleapis.com/auth/documents
   https://www.googleapis.com/auth/presentations
   https://www.googleapis.com/auth/drive.readonly
   ```
3. 生成された `token.json` を配置

**参考**: Google Cloud Consoleで作成するOAuthクライアントには「デスクトップアプリ」タイプを選択。
