# Alert Monitoring System

Gmail を定期監視し、条件に一致するメールを Slack に自動通知するシステム。

## アーキテクチャ

```
GitHub Actions (cron: 30分ごと)
  └─ main.py
       ├─ monitors.yaml を読み込み
       ├─ GmailMonitor: Gmail API でメール取得・フィルタ
       └─ SlackNotifier: Slack App (Bot Token) で通知
```

## セットアップ

### 1. Gmail API の有効化

1. [Google Cloud Console](https://console.cloud.google.com/) でプロジェクトを作成（または既存を使用）
2. 「APIとサービス」→「ライブラリ」→ **Gmail API** を有効化
3. 「APIとサービス」→「認証情報」→「認証情報を作成」→ **OAuthクライアントID**
   - アプリケーションの種類: **デスクトップアプリ**
   - 作成後、`credentials.json` をダウンロード

### 2. OAuth2 トークンの取得（初回のみ）

ローカルで以下を実行してブラウザ認証を行う:

```bash
cd scripts/alert-monitoring
pip install -r requirements.txt

python -c "
from google_auth_oauthlib.flow import InstalledAppFlow
flow = InstalledAppFlow.from_client_secrets_file(
    'credentials.json',
    scopes=['https://www.googleapis.com/auth/gmail.readonly']
)
creds = flow.run_local_server(port=0)
print('=== token.json の内容（以下を GMAIL_TOKEN に設定）===')
import json
print(json.dumps({
    'token': creds.token,
    'refresh_token': creds.refresh_token,
    'token_uri': creds.token_uri,
    'client_id': creds.client_id,
    'client_secret': creds.client_secret,
}))
"
```

### 3. GitHub Secrets の登録

リポジトリの Settings → Secrets and variables → Actions に以下を登録:

| Secret名 | 内容 |
|---|---|
| `GMAIL_CREDENTIALS` | `credentials.json` の全文（JSON文字列） |
| `GMAIL_TOKEN` | 上記スクリプトで出力された token JSON |
| `SLACK_BOT_TOKEN` | Slack App の Bot Token (`xoxb-...`) |

### 4. Slack App の設定

既存の Slack App（slack-message-router と共有）の Bot Token を使用。
必要なスコープ: `chat:write`

## 使い方

### ローカルテスト

```bash
cd scripts/alert-monitoring

# 環境変数を設定
export GMAIL_CREDENTIALS='{"installed":{...}}'
export GMAIL_TOKEN='{"token":"...","refresh_token":"..."}'
export SLACK_BOT_TOKEN='xoxb-...'

# dry-run（Slack送信せずstdoutに出力）
python main.py --dry-run

# 実行
python main.py
```

### 監視対象の追加

#### Gmail の場合（YAML追加のみ）

`type: gmail` の監視は `monitors.yaml` に設定を追加するだけで動作する:

```yaml
monitors:
  - name: new_alert          # 識別名
    type: gmail               # 監視タイプ（現在は gmail のみ）
    enabled: true             # 有効/無効
    from_address: ""          # 送信元フィルタ（空 = なし）
    subject_contains:         # 件名キーワード（OR条件）
      - "キーワード"
    body_contains: []         # 本文キーワード（OR条件、空 = なし）
    slack_channel: "#channel" # 通知先チャンネル
    note: "メモ"              # 説明（実行には影響しない）
```

#### Gmail 以外の場合（コード追加が必要）

Gmail 以外のソースを監視する場合は、以下の対応が必要:

1. `monitors/` に新しい monitor クラスを実装（例: `xxx_monitor.py`）
2. `main.py` に新しい `type` のルーティングを追加

## トークンの寿命

| トークン | 寿命 | 備考 |
|---|---|---|
| Access Token | 約1時間 | ライブラリが自動リフレッシュ |
| Refresh Token | 6ヶ月未使用で失効 | 30分cron実行なら実質無期限 |

Refresh Token が失効した場合は、セクション2の手順でトークンを再取得してください。

## トラブルシューティング

- **`GMAIL_CREDENTIALS と GMAIL_TOKEN を設定してください`**: 環境変数が未設定
- **`Slack通知失敗`**: Bot Token が無効、またはチャンネルにAppが追加されていない
- **重複通知が来る**: `processed_ids.json` のキャッシュが失われた（GitHub Actions Cacheの7日ルール）
