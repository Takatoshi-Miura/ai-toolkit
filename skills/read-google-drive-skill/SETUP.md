# 初回セットアップ

このスキルを使用するための環境セットアップ手順。

## セットアップワークフロー

このチェックリストをコピーして進行状況を追跡：

```
セットアップ進捗：
- [ ] ステップ1：依存関係をインストール
- [ ] ステップ2：認証ファイルを配置
- [ ] ステップ3：動作確認
```

### ステップ1：依存関係をインストール

```bash
pip install google-api-python-client google-auth google-auth-oauthlib google-auth-httplib2
```

**検証**: エラーなく完了すればOK。`ModuleNotFoundError` が発生する場合は再実行。

### ステップ2：認証ファイルを配置

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

この方法で配置すると、セッションをまたいでも設定が維持される。

### ステップ3：動作確認

任意のGoogle DriveファイルIDで実行：

```bash
python3 scripts/read_drive_file.py <任意のfileId> sheets
```

**成功時**: JSON形式でファイル内容が出力される
**失敗時**: エラーメッセージを確認し、該当するトラブルシューティングを実行

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

### 認証情報ファイルが見つかりません

```
認証情報ファイルが見つかりません: /path/to/client_secret.json
```

**対応**:
1. Google Cloud ConsoleでOAuth 2.0クライアントIDを作成
2. 認証情報をダウンロード
3. ステップ2の配置手順を実行

### トークンファイルが見つかりません

```
トークンファイルが見つかりません: /path/to/token.json
```

**対応**:
1. 既存の `token.json` がある場合はコピー
2. ない場合は、Google OAuth認証フローを実行して生成

### トークンの有効期限切れ

**対応**: スクリプトが自動でリフレッシュを試みる。失敗する場合は `token.json` を再生成

### ModuleNotFoundError

```
ModuleNotFoundError: No module named 'google'
```

**対応**: ステップ1の依存関係インストールを再実行
