---
name: retrospective
description: 振り返りスペシャリストとして週次/月次のレトロスペクティブを実行。LifeGraph、日次記録、金銭データをスクリプトで取得・分析してレポートを作成。
allowed-tools: Bash, Read, Write, TodoWrite, AskUserQuestion
user-invocable: true
disable-model-invocation: true
---

# 振り返りスキル

週次または月次の振り返りを実行するスキル。各Phaseで対応するREFERENCEファイルを参照すること。

## 実行手順

### Phase 0: 進捗管理の登録

**最初にTodoWriteで以下を登録すること：**

```json
[
  { "content": "Phase 1: 期間選択", "status": "pending", "activeForm": "期間を選択中" },
  { "content": "Phase 2: 出力ファイル作成", "status": "pending", "activeForm": "出力ファイルを作成中" },
  { "content": "Phase 3: データ取得", "status": "pending", "activeForm": "データを取得中" },
  { "content": "Phase 3.5: Insights取得（月次のみ）", "status": "pending", "activeForm": "Insightsを取得中" },
  { "content": "Phase 4: 分析とレポート作成", "status": "pending", "activeForm": "分析・レポートを作成中" },
  { "content": "Phase 5: 目標提案・総評", "status": "pending", "activeForm": "目標提案・総評を作成中" },
  { "content": "Phase 6: 完了報告", "status": "pending", "activeForm": "完了報告中" }
]
```

### Phase 1: 期間選択

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

### Phase 2: 出力ファイル作成

`~/Downloads/yyyyMMdd-{weekly|monthly}-retrospective.md` を作成（タイトルと目次のみ）。

### Phase 3: データ取得

→ **[REFERENCE-LIFEGRAPH.md](REFERENCE-LIFEGRAPH.md)** を参照してLifeGraphデータを取得
→ **[REFERENCE-DAILY.md](REFERENCE-DAILY.md)** を参照して日次記録データを取得
→ **[REFERENCE-MONEY.md](REFERENCE-MONEY.md)** を参照して金銭データを取得（**月次のみ**）

### Phase 3.5: Insights取得（月次のみ）

`/insights` コマンドを実行して過去の会話から得られた洞察を取得する。取得結果はPhase 4の分析材料として活用。

### Phase 4: 分析とレポート作成

取得データをもとに分析しレポートに追記する。各観点のフォーマットは各REFERENCEファイルを参照。

| 観点 | 参照ファイル | 対象 |
|------|------------|------|
| LifeGraph分析 | [REFERENCE-LIFEGRAPH.md](REFERENCE-LIFEGRAPH.md) | 週次・月次 |
| 日次記録分析 | [REFERENCE-DAILY.md](REFERENCE-DAILY.md) | 週次・月次 |
| 金銭分析 | [REFERENCE-MONEY.md](REFERENCE-MONEY.md) | **月次のみ** |

### Phase 5: 目標提案・総評

→ **[REFERENCE-SUMMARY.md](REFERENCE-SUMMARY.md)** を参照して目標提案と総評を追記。

### Phase 6: 完了報告

レポートファイルのパスを報告する。

## 注意事項

- スクリプトがエラーを返した場合は [SETUP.md](SETUP.md) の認証手順を案内
- 今月のタブ名は `yyyyMM` 形式（例: 202601）
- **月次のみのPhaseを週次で実行しないこと**
