---
name: redmine-skill
description: Redmineチケットの読み取り・操作をPythonスクリプトで実行。チケット詳細の取得に対応。Redmine URL（/issues/を含むURL）が含まれ「チケット見て」「Redmine読んで」「チケット確認して」「チケットの内容を教えて」「PBIを確認」などの依頼で自動発動。
allowed-tools: Bash
---

# Redmine操作スキル

RedmineチケットのURLからチケット詳細を取得し、操作するスキル。Pythonスクリプトで実行する。

日本語で回答すること。

## 制約事項

- このスキルはPythonスクリプト（`scripts/` 配下）のみを使用する
- Redmine関連のMCPツールは使用しない
- 認証エラーが発生した場合は、必ず [SETUP.md](SETUP.md) のセットアップワークフローを実行する

---

## 共通: URLからチケットIDを抽出

全ワークフロー共通のステップ。ユーザーのメッセージからRedmine URLを抽出し、チケットIDを取得する。

| URLパターン | 抽出例 |
|------------|--------|
| `https://redmine.example.com/issues/12345` | `12345` |
| `https://redmine.example.com/issues/12345#note-5` | `12345` |

URLが提供されていない場合は、AskUserQuestionツールでチケットURLまたはIDを質問する。

---

## ワークフロー選択

状況に応じて適切なワークフローを参照する：

| やりたいこと | 参照先 |
|-------------|--------|
| 初めて使用する / 認証エラーが発生した | [SETUP.md](SETUP.md) |
| チケット情報を読み取りたい | [READING.md](READING.md) |

---

## エラー対応

| エラー | 対応 |
|-------|------|
| python3: command not found | `brew install python3` (macOS) |
| 認証エラー / 設定ファイルなし | [SETUP.md](SETUP.md) を参照して設定 |
| HTTP 403: Forbidden | APIキーの権限を確認 |
| HTTP 404: Not Found | チケットIDが正しいか確認 |

## 注意事項

- URLからチケットIDを抽出する（例: `/issues/123` から `123`）
- 履歴（journals）が長い場合は、最新の数件のみ表示
- 日本語で回答すること
