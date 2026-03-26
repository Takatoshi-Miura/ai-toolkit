# エラーハンドリング

## エラー対応表

| エラー | 原因 | 対応 |
|-------|------|------|
| `環境変数 SLACK_BOT_TOKEN が設定されていません` | Bot Tokenが未設定 | `export SLACK_BOT_TOKEN="xoxb-..."` を実行 |
| `環境変数 SLACK_APP_TOKEN が設定されていません` | App-Level Tokenが未設定 | `export SLACK_APP_TOKEN="xapp-..."` を実行 |
| `claude CLIが見つかりません` | claudeコマンドがPATHにない | Claude Codeのインストール確認、PATHの設定確認 |
| Socket Mode接続失敗 | App Tokenが無効、またはSocket Modeが無効 | Slack App管理画面でSocket Modeが有効か確認。App-Level Tokenの再生成 |
| チャンネルのメッセージが受信できない | BotがチャンネルにJoinしていない | 監視対象チャンネルにBotを招待 (`/invite @BotName`) |
| `not_in_channel`エラー | Botがチャンネルメンバーでない | 上記と同様、Botを招待 |
| スキル実行タイムアウト（30分） | claude CLIの実行が長時間 | 手動で対話版スキルを実行。タイムアウト値の調整が必要な場合はslack_listener.pyの`timeout`パラメータを変更 |
| 同時実行数上限到達 | 同時に複数のスキルが実行中 | 実行中のスキルが完了するまで待機。上限値はconfig_parser.pyの`max_concurrent`で変更可能（デフォルト: 3） |
| `slack_bolt`インポートエラー | 依存パッケージ未インストール | `pip3 install -r scripts/requirements.txt` を実行 |

## リカバリー手順

### リスナーが応答しない場合

1. プロセス確認: `ps aux | grep slack_listener.py`
2. プロセスが存在しない → 再起動: `python3 scripts/slack_listener.py`
3. プロセスが存在する → 停止してから再起動:
   ```bash
   pkill -f "slack_listener.py"
   python3 scripts/slack_listener.py
   ```

### スキル実行が失敗した場合

1. システム通知チャンネルのメッセージを確認
2. claude CLIのエラー内容に応じて対処:
   - 認証エラー → `claude` コマンドで再認証
   - スキルの実行エラー → 対象スキルのERROR-HANDLING.mdを参照
3. 必要に応じて手動で対話版スキルを実行
