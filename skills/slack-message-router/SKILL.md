---
name: slack-message-router
description: SlackメッセージをSocket Modeで監視し、キーワードに基づいて適切なClaude Codeスキルにルーティングする常駐リスナーの管理。起動・停止・ステータス確認・ルーティングルールの追加/更新/削除に対応。
allowed-tools: Bash, Read, TodoWrite
user-invocable: true
disable-model-invocation: true
---

# Slackメッセージルーター

SlackメッセージをSocket Modeで監視し、CONFIG.mdのルーティングルールに基づいてClaude Codeスキルを自動起動する常駐リスナーを管理する。

日本語で回答すること。

## 役割

Slackリスナープロセスの起動・停止・ステータス確認を行うスキル。リスナー自体はPythonプロセス（slack_listener.py）として常駐実行される。

## 手順

AskUserQuestionツールでユーザーに操作を確認する:

1. **起動**: リスナーを起動する
2. **停止**: 実行中のリスナーを停止する
3. **ステータス確認**: リスナーの実行状態を確認する
4. **ルール管理**: ルーティングルールの追加・更新・削除

起動失敗時は、エラー対応セクションを参照すること。

---

## 起動

```bash
cd ~/.claude/skills/slack-message-router && python3 scripts/slack_listener.py &
```

## 停止

```bash
pkill -f "slack_listener.py"
```

## ステータス確認

```bash
ps aux | grep -v grep | grep "slack_listener.py"
```

## ルール管理

[CONFIG.md](CONFIG.md) を読み取り、現在のルーティングルールをユーザーに提示する。

ユーザーの要望を自然言語で受け取り、意図を判断して対応する。
不明な点があれば質問して確認する。

**対応できる操作:**

- **追加**: 新しいルーティングルールをCONFIG.mdに追加。スキル名とキーワードをユーザーの要望から読み取り、不足情報は質問する。
- **更新**: 既存ルールの変更。ユーザーが指定したルールの該当項目をCONFIG.mdで編集する。
- **削除**: 既存ルールの削除。ユーザーに確認後、CONFIG.mdから該当行を削除する。

**ルール管理後の注意:**

CONFIG.mdはリスナー起動時に読み込まれるため、リスナーが実行中の場合は再起動が必要。
リスナーが実行中かを確認し、実行中であれば再起動を提案する。

---

## リファレンス

- **設定**: [CONFIG.md](CONFIG.md)
- **セットアップ**: [README.md](README.md)
- **エラー対応**: [ERROR-HANDLING.md](ERROR-HANDLING.md)
