---
name: retrospective
description: 振り返りスペシャリストとして週次/月次のレトロスペクティブ、および週末の振り返り質問生成を実行。LifeGraph、日次記録、金銭データをスクリプトで取得・分析してレポートや質問を作成し、サブエージェントレビューとユーザーフィードバックの蓄積により回を重ねるごとに質を改善する。
allowed-tools: Bash, Read, Write, TodoWrite, AskUserQuestion, Agent
user-invocable: true
disable-model-invocation: true
---

# 振り返りスキル

振り返りに関する2つのワークフローを提供する。最初にどちらを行うかを選択し、対応するWORKFLOWファイルの手順に従うこと。

## Phase 0: ワークフロー選択

**AskUserQuestionで以下を実行：**

```json
{
  "questions": [
    {
      "question": "どちらのワークフローを実行しますか？",
      "header": "ワークフロー",
      "multiSelect": false,
      "options": [
        { "label": "レポート作成", "description": "週次/月次のレトロスペクティブレポートを作成する" },
        { "label": "週末振り返り質問生成", "description": "直近1週間の記録から、振り返りを深める質問を生成する" }
      ]
    }
  ]
}
```

| 選択肢 | 進む先 |
|--------|--------|
| レポート作成 | [WORKFLOW-REPORT.md](WORKFLOW-REPORT.md) |
| 週末振り返り質問生成 | [WORKFLOW-WEEKLY-QUESTIONS.md](WORKFLOW-WEEKLY-QUESTIONS.md) |

選択後は、選ばれたWORKFLOWファイルのPhase構成（TodoWrite登録含む）に従って最後まで実行する。本ファイルのPhaseには戻らない。

## 共通の設計方針

- **過去の蓄積を踏まえる**: 両ワークフローとも、`output/feedback-log.md`（ユーザー指摘の蓄積）と直近の過去成果物を読み込んでから作成に着手する。同じ指摘を繰り返さないようにするため。
- **サブエージェントレビュー**: 成果物の初稿ができた時点で、Agentツール（`general-purpose`）を起動しレビューを依頼する。レビュー観点は各WORKFLOWファイルに明記。
- **ユーザー確認とフィードバック蓄積**: レビュー反映後、必ずユーザーに内容を提示し誤り・修正指摘を確認する。指摘があれば成果物に反映したうえで `output/feedback-log.md` に追記し、次回以降に活かす。
- **出力先**: すべての成果物・ログは [output/](output/) 配下に保存する（`output/.gitignore` で誤コミットを防止済み）。

## 注意事項

- スクリプトがエラーを返した場合は [SETUP.md](SETUP.md) の認証手順を案内
- 月タブ名は `yyyyMM` 形式。現在値は [CONFIG.md](CONFIG.md) の `month_tab` を参照
- CONFIG.mdの値変更が必要な場合は、両WORKFLOWとも [CONFIG.md](CONFIG.md) を単一の情報源として参照・更新する
