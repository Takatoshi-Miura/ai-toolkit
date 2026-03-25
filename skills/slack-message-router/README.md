# slack-message-router

SlackメッセージをSocket Modeで監視し、CONFIG.mdのルーティングルールに基づいてClaude Codeスキルを自動起動する常駐リスナー。

## アーキテクチャ

```
Slack ワークスペース ◄──WebSocket── カスタム Slack App (Socket Mode)
                                         │ イベント配信
                                         ▼
                                   slack_listener.py (ローカルPC)
                                   CONFIG.md のルールで解析・ルーティング
                                         │ subprocess
                                         ▼
                                   claude -p '{...}' (スキル実行)
```

## 前提条件

- Python 3.9+
- Claude Code CLI (`claude`) がインストール・認証済み
- ルーティング先のスキルがセットアップ済み（例: release-workflow-slack）

## セットアップ

### 1. Slack App作成

[Slack API](https://api.slack.com/apps) で新しいAppを作成する。

#### Socket Mode有効化

1. 左メニュー「Socket Mode」→ 有効にする
2. App-Level Tokenを生成（スコープ: `connections:write`）
3. 生成されたトークン（`xapp-`で始まる）を控える

#### Bot Token Scopes設定

左メニュー「OAuth & Permissions」→ 「Bot Token Scopes」に以下を追加:

| スコープ | 用途 |
|---------|------|
| `chat:write` | メッセージ送信（スレッド返信） |
| `channels:history` | パブリックチャンネルのメッセージ受信 |
| `groups:history` | プライベートチャンネルのメッセージ受信 |

#### Event Subscriptions設定

左メニュー「Event Subscriptions」→ 有効にする → 「Subscribe to bot events」に以下を追加:

| イベント | 用途 |
|---------|------|
| `message.channels` | パブリックチャンネルのメッセージ |
| `message.groups` | プライベートチャンネルのメッセージ |

#### Appインストール

左メニュー「Install App」→ ワークスペースにインストール → Bot Token（`xoxb-`で始まる）を控える

### 2. Python依存パッケージインストール

```bash
pip3 install -r ~/.claude/skills/slack-message-router/scripts/requirements.txt
```

### 3. 環境変数設定

```bash
export SLACK_BOT_TOKEN="xoxb-..."
export SLACK_APP_TOKEN="xapp-..."
```

`.zshrc` や `.bash_profile` に追記して永続化することを推奨。

### 4. CONFIG.md編集

[CONFIG.md](CONFIG.md) を編集して以下を設定:

- **監視対象チャンネル**: 監視するSlackチャンネルのIDを追加
- **許可ユーザー**: 必要に応じてユーザーIDを制限
- **通知設定**: 運用通知・エラー通知の送信先チャンネルIDを設定
- **ルーティングルール**: 必要に応じてルールを追加・変更

### 5. Botをチャンネルに招待

監視対象チャンネルでBotを招待:
```
/invite @{Bot名}
```

## 起動・停止

### 起動

```bash
cd ~/.claude/skills/slack-message-router
python3 scripts/slack_listener.py
```

バックグラウンド実行:
```bash
cd ~/.claude/skills/slack-message-router
nohup python3 scripts/slack_listener.py > /tmp/slack-listener.log 2>&1 &
```

### 停止

- フォアグラウンド: `Ctrl+C`
- バックグラウンド: `pkill -f "slack_listener.py"`

### ステータス確認

```bash
ps aux | grep -v grep | grep "slack_listener.py"
```

## ルーティングルールの追加方法

新しいスキルをSlackから起動したい場合、CONFIG.mdの編集のみで対応可能:

1. **ルーティングルール**テーブルに新しい行を追加
2. 必要に応じて**パラメータ抽出パターン**テーブルに正規表現を追加
3. リスナーを再起動（CONFIG.mdは起動時に読み込まれるため）

## トラブルシューティング

| 症状 | 確認事項 |
|------|---------|
| リスナーが起動しない | 環境変数（SLACK_BOT_TOKEN, SLACK_APP_TOKEN）が設定されているか確認 |
| メッセージに反応しない | Botがチャンネルに招待されているか確認。CONFIG.mdの監視対象チャンネルIDが正しいか確認 |
| `claude`コマンドが見つからない | `which claude` でパスを確認。PATHに含まれているか確認 |
| Socket Mode接続エラー | Slack App管理画面でSocket Modeが有効か確認。App-Level Tokenが有効か確認 |

詳細は [ERROR-HANDLING.md](ERROR-HANDLING.md) を参照。
