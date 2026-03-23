---
name: retrospective
description: 振り返りスペシャリストとして週次のレトロスペクティブを実行。LifeGraph・日次記録データをコネクタで取得・分析してレポートを作成。
---

# 振り返りスキル（Claude Web版）

週次の振り返りを実行するスキル。各Phaseで対応するREFERENCEファイルを参照すること。

**注意**: このスキルは週次振り返り専用です。月次振り返り（金銭分析を含む）はClaude Code版を使用してください。

## 実行手順

### Phase 1: データ取得

以下のデータを各REFERENCEファイルの手順に従って取得する。

| データ | 参照ファイル | 取得方法 |
|--------|------------|----------|
| LifeGraph | [REFERENCE-LIFEGRAPH.md](REFERENCE-LIFEGRAPH.md) | Googleカレンダーコネクタ |
| 日次記録 | [REFERENCE-DAILY.md](REFERENCE-DAILY.md) | Google Driveコネクタ |
| パーソナルコンテキスト | [REFERENCE-SUMMARY.md](REFERENCE-SUMMARY.md) | Google Driveコネクタ |

### Phase 2: 分析とレポート作成

取得データをもとに分析し、会話内でMarkdownレポートを出力する。各観点のフォーマットは各REFERENCEファイルを参照。

| 観点 | 参照ファイル |
|------|------------|
| LifeGraph分析 | [REFERENCE-LIFEGRAPH.md](REFERENCE-LIFEGRAPH.md) |
| 日次記録分析 | [REFERENCE-DAILY.md](REFERENCE-DAILY.md) |

### Phase 3: 目標提案・総評

[REFERENCE-SUMMARY.md](REFERENCE-SUMMARY.md) を参照して目標提案と総評を出力。

## 注意事項

- 今月のタブ名は `yyyyMM` 形式（例: 202601）
- 金銭分析はClaude Webではスプレッドシート読み取り不可のため除外
