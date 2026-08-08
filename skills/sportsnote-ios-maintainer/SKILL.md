---
name: sportsnote-ios-maintainer
description: SportsNote iOS（/Users/it6210/Documents/Git/SportsNote_iOS）の開発・保守を無人実行するオーケストレーター。コード調査によるdoc/仕様書更新（ナレッジ蓄積）、不具合調査・ユーザー要望・リファクタリング候補・ドキュメント不足・テスト不足の観点からのissue起票（issue作成）、issueの選択から実装・クロスレビュー・PR作成まで（実装）の3フローを提供する。ローカルルーチンからの「ナレッジ蓄積フロー」「issue作成フロー」「実装フロー」の呼び出しで使用。
allowed-tools: Read, Write, Edit, Bash, Agent, TodoWrite, Glob, Grep
user-invocable: true
disable-model-invocation: true
---

# sportsnote-ios-maintainer

SportsNote iOSの開発・保守に関する3つのフローを提供する。最初にどのフローを行うかを判定し、対応するWORKFLOWファイルの手順に従うこと。

日本語で回答すること。

## Phase 0: Todo登録

**TodoWriteツールで以下を登録：**

```json
[
  {"content": "Phase 1: フロー判定", "activeForm": "フローを判定中", "status": "pending"},
  {"content": "選択したWORKFLOWファイルの手順を実行", "activeForm": "選択したワークフローを実行中", "status": "pending"}
]
```

## Phase 1: フロー判定

呼び出し文言から、以下のどれを行うかを判定する。

| 判定 | 進む先 |
|------|--------|
| コード調査・doc更新・ナレッジ蓄積をしたい（「ナレッジ蓄積」「doc更新」「仕様整理」等） | [WORKFLOW-KNOWLEDGE.md](WORKFLOW-KNOWLEDGE.md) |
| issueを作成したい（「issue作成」「issue起票」「issue棚卸し」等） | [WORKFLOW-ISSUE.md](WORKFLOW-ISSUE.md) |
| issueを実装したい（「実装フロー」「issue実装」「issueを片付けて」等） | [WORKFLOW-IMPLEMENT.md](WORKFLOW-IMPLEMENT.md) |

本スキルは無人実行が前提のため、AskUserQuestionでの確認は行わない。判定できない場合は、KNOWLEDGE → ISSUE → IMPLEMENT の順に実行可能性を状態から判定し、最初に該当したものを実行する（例: `references/knowledge-map.md`が古ければKNOWLEDGE、`input/requests.md`に未処理項目があればISSUE、openなissueがあればIMPLEMENT）。

判定後は、選ばれたWORKFLOWファイルのPhase構成（TodoWrite登録含む）に従って最後まで実行する。本ファイルのPhaseには戻らない。

## 共通の設計方針

- **無人実行前提**: AskUserQuestionは使用しない。各WORKFLOWの成果物（doc更新・issue作成・PR作成）はユーザー承認を待たずに確定する
- **単一情報源**: `references/review-insights.md`（レビュー観点ナレッジ）と `input/feedback.md`（ユーザーフィードバック）は全フロー共通で参照・蓄積する
- **独立性**: 3フローはローカルルーチンから個別に呼ばれるため、各WORKFLOWは他フローが未実行でも単独で完走できる
- **他スキルとの関係**: `~/.claude/skills/coding/WORKFLOW-SPORTSNOTE.md`（ユーザー対話型・単発実装依頼用）とは完全に独立している。ファイルの参照・importは行わない

## 対象リポジトリ

- **プロジェクトパス**: `/Users/it6210/Documents/Git/SportsNote_iOS`
- **プロジェクト規約**: `/Users/it6210/Documents/Git/SportsNote_iOS/CLAUDE.md`
- **仕様書ディレクトリ**: `/Users/it6210/Documents/Git/SportsNote_iOS/doc/spec/`
- **GitHubリポジトリ**: `Takatoshi-Miura/SportsNote_iOS`（`gh` CLIでログイン済み前提）

## エラー対応

| エラー | 対応 |
|-------|------|
| `gh auth status` が失敗する | [README.md](README.md) の事前準備を確認しユーザーに認証を依頼する旨をhistory.mdに記録して終了 |
| SportsNote_iOSリポジトリが存在しない | パスを確認し、history.mdに記録して終了 |
| サブエージェント失敗 | エラーメッセージを分析し再試行（最大3回） |
| 各WORKFLOW固有のエラー | 各WORKFLOWファイルのエラー対応表を参照 |
