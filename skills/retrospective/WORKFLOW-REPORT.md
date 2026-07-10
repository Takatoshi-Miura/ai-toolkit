# ワークフロー: レポート作成

週次または月次の振り返りレポートを作成する。各Phaseで対応するREFERENCEファイルを参照すること。

## Phase 0: 進捗管理の登録

**TodoWriteで以下を登録すること：**

```json
[
  { "content": "Phase 1: 期間選択", "status": "pending", "activeForm": "期間を選択中" },
  { "content": "Phase 2: 過去レポート・フィードバックログの読み込み", "status": "pending", "activeForm": "過去の蓄積を読み込み中" },
  { "content": "Phase 3: 出力ファイル作成", "status": "pending", "activeForm": "出力ファイルを作成中" },
  { "content": "Phase 4: データ取得", "status": "pending", "activeForm": "データを取得中" },
  { "content": "Phase 5: 分析とレポート作成", "status": "pending", "activeForm": "分析・レポートを作成中" },
  { "content": "Phase 6: 目標提案・総評", "status": "pending", "activeForm": "目標提案・総評を作成中" },
  { "content": "Phase 7: サブエージェントレビュー", "status": "pending", "activeForm": "サブエージェントレビューを実施中" },
  { "content": "Phase 8: ユーザー確認・修正", "status": "pending", "activeForm": "ユーザー確認・修正を反映中" },
  { "content": "Phase 9: 完了報告", "status": "pending", "activeForm": "完了報告中" }
]
```

## Phase 1: 期間選択・設定確認

**AskUserQuestionで以下を実行：**

```json
{
  "questions": [
    {
      "question": "振り返りの期間を選択してください。",
      "header": "期間",
      "multiSelect": false,
      "options": [
        { "label": "週次", "description": "LifeGraph + 日次記録を分析" },
        { "label": "月次", "description": "LifeGraph + 日次記録 + 金銭を分析" }
      ]
    }
  ]
}
```

| 選択肢 | 読み込むREFERENCE |
|--------|-----------------|
| 週次 | LIFEGRAPH / DAILY / SUMMARY |
| 月次 | LIFEGRAPH / DAILY / MONEY / SUMMARY |

**月タブ確認:** [CONFIG.md](CONFIG.md) の `month_tab` を読み取り、現在の値をAskUserQuestionで確認する。変更が必要な場合はCONFIG.mdを更新する。

## Phase 2: 過去レポート・フィードバックログの読み込み

同一種別（週次/月次）の過去レポートを [output/](output/) ディレクトリから**新しい順に最大3件**読み込む（ファイル名 `yyyyMMdd-{weekly|monthly}-retrospective.md` で判別）。

`output/feedback-log.md` が存在すれば読み込み、「## レポート」セクションの過去指摘を確認する（存在しない場合はこのPhaseをスキップし、Phase 8で初めて作成する）。

読み込んだ内容から、**今回のレポートで特に反映すべき過去の指摘・傾向**を把握しておく。Phase 5・Phase 7で活用する。

## Phase 3: 出力ファイル作成

`output/yyyyMMdd-{weekly|monthly}-retrospective.md` を作成（タイトルと目次のみ）。

## Phase 4: データ取得

→ **[REFERENCE-LIFEGRAPH.md](REFERENCE-LIFEGRAPH.md)** を参照してカレンダーイベント + スプレッドシート補完データを取得
→ **[REFERENCE-DAILY.md](REFERENCE-DAILY.md)** を参照して日次記録データを取得
→ **[REFERENCE-MONEY.md](REFERENCE-MONEY.md)** を参照して金銭データを取得（**月次のみ**）

## Phase 5: 分析とレポート作成

取得データをもとに分析しレポートに追記する。各観点のフォーマットは各REFERENCEファイルを参照。

| 観点 | 参照ファイル | 対象 |
|------|------------|------|
| LifeGraph分析 | [REFERENCE-LIFEGRAPH.md](REFERENCE-LIFEGRAPH.md) | 週次・月次 |
| 日次記録分析 | [REFERENCE-DAILY.md](REFERENCE-DAILY.md) | 週次・月次 |
| 金銭分析 | [REFERENCE-MONEY.md](REFERENCE-MONEY.md) | **月次のみ** |

Phase 2で把握した過去の指摘・傾向（例: 前回「〇〇の解釈が浅い」と指摘された等）を踏まえ、同じ問題を繰り返さないよう分析に反映する。

## Phase 6: 目標提案・総評

→ **[REFERENCE-SUMMARY.md](REFERENCE-SUMMARY.md)** を参照して目標提案と総評を追記。

## Phase 7: サブエージェントレビュー

**Agentツール（`general-purpose`）を起動し、以下の観点でレビューを依頼する：**

- 前回までのレポート・feedback-logで指摘された改善点が、今回のレポートに反映されているか
- データの解釈に誤り・矛盾がないか（元データの数値とレポート中の記述が整合しているか）
- 各REFERENCEファイルで定義された出力テンプレート（見出し・表構成）に沿っているか

エージェントには、作成したレポート本文と、Phase 2で読み込んだ過去レポート・feedback-logの該当箇所を渡す。レビュー結果を受けて、必要な修正をレポートに反映する。

## Phase 8: ユーザー確認・修正

レポート内容をユーザーに提示し、誤りや修正したい点がないか確認する。

- 指摘があれば、その内容をレポートに反映する
- 反映した指摘は `output/feedback-log.md` の「## レポート」セクションに、日付とともに追記する（次回のPhase 2で読み込まれる）
- 指摘がなければ `output/feedback-log.md` への追記は不要

## Phase 9: 完了報告

レポートファイルのパスを報告する。

## 注意事項

- **月次のみのPhaseを週次で実行しないこと**
- スクリプトがエラーを返した場合は [SETUP.md](SETUP.md) の認証手順を案内
