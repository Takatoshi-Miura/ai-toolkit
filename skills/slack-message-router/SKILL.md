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

---

## リファレンス

- **設定**: [CONFIG.md](CONFIG.md)
- **セットアップ**: [README.md](README.md)
- **エラー対応**: [ERROR-HANDLING.md](ERROR-HANDLING.md)
