---
name: retrospective-agent-team
description: エージェントチームを活用した振り返りスペシャリスト。LifeGraph・日次記録・金銭データを複数メンバーで並行分析し、クロスリファレンスによる深い洞察を含むレポートを作成。「チーム振り返り」「チームレトロ」「エージェントチーム振り返り」などの依頼で使用。
allowed-tools: Bash, AskUserQuestion, Write, Read
user-invocable: true
disable-model-invocation: true
---

# エージェントチーム振り返りスキル

エージェントチームを組成し、LifeGraph・日次記録・金銭データを並行分析してクロスリファレンスを含む深いレポートを作成します。

## 役割

振り返りのオーケストレーターとして、専門アナリストチームを編成・調整し、データソース横断の洞察を含む統合レポートを作成する。

## 重要：このスキルの使い方

**各フェーズを順番に実行すること。フェーズを飛ばしてはならない。**

**制約事項：**
- 既存の `retrospective` スキルのリソース（REFERENCE.md、SETUP.md、scripts/）をパスで参照する
- 既存ファイルは編集しない
- エージェントチーム機能を使用してメンバーをスポーンする

---

## 前提条件

### データソース
| データ | ファイルID | fileType | 用途 |
|--------|-----------|----------|------|
| LifeGraph | `1WF58VNM0lGfN-YKqR2ySXU_EKQQCpyrV4da8WiVtoBo` | sheets | 時間・パフォーマンス分析 |
| ノート | `1iVeZ1EB5dahEZukuQQB4gSa5jIw3By-Gz8JaAysiAoA` | docs | 日次記録・目標 |
| 金銭管理 | `1P519LiN0Tiu-NvWuYgek9jc4IfvXTzIukkVkuokAqY0` | sheets | 収支分析（月次のみ） |
| パーソナルコンテキスト | `1hDcVtQ5wEz2rPGRrJGK8CspnqSujheAjeZ1PPAj2u6E` | docs | 価値観・思考スタイル（全メンバー参照） |

### 共通リソースパス
- スクリプト: `~/.claude/skills/retrospective/scripts/read_drive_file.py`
- 分析リファレンス: `~/.claude/skills/retrospective/REFERENCE.md`
- セットアップ: `~/.claude/skills/retrospective/SETUP.md`
- チーム共通ガイド: [TEAM-GUIDE.md](TEAM-GUIDE.md)

### チーム構成
| メンバー | 役割 | スポーン条件 |
|---------|------|------------|
| LifeGraphアナリスト | 時間配分・パフォーマンス分析 | 常時 |
| 日次記録アナリスト | 4カテゴリ目標達成分析 | 常時 |
| 金銭アナリスト | 収支・予算・住宅ローン分析 | **月次のみ** |
| 統合コーチ | クロスリファレンス・目標提案・総評 | アナリスト完了後 |

---

## Phase 0: Todo登録

**TodoWriteツールで以下を登録：**

```json
[
  {"content": "Phase 1: 期間選択", "activeForm": "期間を選択中", "status": "pending"},
  {"content": "Phase 2: 出力ディレクトリ準備", "activeForm": "出力ディレクトリを準備中", "status": "pending"},
  {"content": "Phase 3: チーム組成・アナリストスポーン", "activeForm": "チームを組成してアナリストをスポーン中", "status": "pending"},
  {"content": "Phase 4: 統合コーチスポーン", "activeForm": "統合コーチをスポーンして統合中", "status": "pending"},
  {"content": "Phase 5: クリーンアップ・完了報告", "activeForm": "クリーンアップして完了報告中", "status": "pending"}
]
```

---

## Phase 1: 期間選択

AskUserQuestionツールで期間を質問：

| 選択肢 | 内容 | メンバー数 |
|--------|------|-----------|
| 週次 | LifeGraph + 日次記録 → 統合 | 3名 |
| 月次 | LifeGraph + 金銭 + 日次記録 → 統合 | 4名 |

**確定する変数：**
- `PERIOD_TYPE`: `weekly` or `monthly`
- `CURRENT_MONTH`: 今月の `yyyyMM` 形式（例: 202602）
- `DATE_PREFIX`: 今日の `yyyyMMdd` 形式（例: 20260208）
- `OUTPUT_DIR`: `~/Downloads/{DATE_PREFIX}-{PERIOD_TYPE}-retrospective/`

**成功確認**: 期間が選択された → Phase 2へ

---

## Phase 2: 出力ディレクトリ準備

```bash
mkdir -p ~/Downloads/{DATE_PREFIX}-{PERIOD_TYPE}-retrospective/
```

**成功確認**: ディレクトリが作成された → Phase 3へ

---

## Phase 3: チーム組成・アナリストスポーン

### 3-1. メンバー指示書の読み取り

以下のファイルをReadツールで読み取る：
- [agents/lifegraph-analyst.md](agents/lifegraph-analyst.md)
- [agents/daily-notes-analyst.md](agents/daily-notes-analyst.md)
- [agents/money-analyst.md](agents/money-analyst.md)（月次のみ）

### 3-2. 動的パラメータの埋め込み

各指示書内のプレースホルダーを実際の値に置換：
- `{PERIOD_TYPE}` → 実際の期間タイプ
- `{CURRENT_MONTH}` → 実際のyyyyMM
- `{OUTPUT_DIR}` → 実際の出力ディレクトリパス
- `{DATE_PREFIX}` → 実際のyyyyMMdd

### 3-3. エージェントチーム作成・アナリストスポーン

自然言語でエージェントチームを作成し、アナリストメンバーをスポーンする。

**スポーンプロンプト構成（各アナリスト共通）：**
```
あなたは{メンバー名}です。

{指示書の内容（動的パラメータ埋め込み済み）}

共通ガイド:
{TEAM-GUIDE.mdの内容}
```

**週次の場合**: LifeGraphアナリスト + 日次記録アナリストの2名を並行スポーン
**月次の場合**: 上記2名 + 金銭アナリストの3名を並行スポーン

**成功確認**: アナリストがスポーンされ、作業を開始した → Phase 4へ（完了待ち）

---

## Phase 4: 統合コーチスポーン

### 4-1. アナリスト完了待ち

各アナリストからの完了メッセージを受信する。
全アナリストが完了するまで待機する。

**完了判定**: 以下のファイルが存在すること
- `{OUTPUT_DIR}/lifegraph-analysis.md`
- `{OUTPUT_DIR}/daily-notes-analysis.md`
- `{OUTPUT_DIR}/money-analysis.md`（月次のみ）

### 4-2. 統合コーチのスポーン

[agents/integration-coach.md](agents/integration-coach.md) を読み取り、動的パラメータを埋め込んでスポーン。

統合コーチに追加で伝える情報：
- 分析ファイルの一覧（存在するファイルパス）
- 期間タイプに応じた出力フォーマット（週次/月次）

### 4-3. 統合コーチ完了待ち

統合コーチの完了メッセージを受信し、最終レポートの存在を確認。

**成功確認**: `{OUTPUT_DIR}/{DATE_PREFIX}-{PERIOD_TYPE}-retrospective.md` が存在する → Phase 5へ

---

## Phase 5: クリーンアップ・完了報告

### 5-1. チームシャットダウン

全メンバーにシャットダウンを要求し、チームをクリーンアップする。

### 5-2. 完了報告

ユーザーに以下を報告：
- 最終レポートのパス: `{OUTPUT_DIR}/{DATE_PREFIX}-{PERIOD_TYPE}-retrospective.md`
- 中間ファイルのパス（参考用）:
  - `{OUTPUT_DIR}/lifegraph-analysis.md`
  - `{OUTPUT_DIR}/daily-notes-analysis.md`
  - `{OUTPUT_DIR}/money-analysis.md`（月次のみ）

---

## エラー対応

| エラー | 対応 |
|-------|------|
| 認証エラー（Google Drive） | アナリストがリーダーに報告。[SETUP.md](~/.claude/skills/retrospective/SETUP.md) の手順を案内 |
| スクリプト実行エラー | リトライ1回。失敗時はリーダーにメッセージで報告 |
| メンバーがアイドル化 | リーダーがメッセージ送信でウェイクアップ |
| 統合コーチが分析ファイルを読めない | 該当アナリストの完了状態を再確認 |

## 注意事項

- エージェントチームはトークン消費が大きい。軽い振り返りには既存の `/retrospective` を推奨
- 中間ファイルは削除せず `{OUTPUT_DIR}/` に保存される
- 各メンバーは CLAUDE.md とスキルを自動ロードするため、プロジェクトコンテキストにアクセス可能
