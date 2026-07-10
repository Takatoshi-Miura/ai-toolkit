# 振り返りスキル（retrospective）

## 1. 概要

- **何をするスキルか**: 週次/月次のレトロスペクティブレポート作成、または週末の振り返り質問生成を行う。LifeGraph・日次記録・金銭データをスクリプトで取得・分析し、サブエージェントレビューとユーザーフィードバックの蓄積により回を重ねるごとに質を改善する。
- **発動条件**:
  - 自動発動キーワード: なし（明示呼び出しのみ）
  - スラッシュ呼び出し: `/retrospective` で可能
  - 自動発動: なし（`disable-model-invocation: true`）
- **依存の有無**: Google Drive API・Google Calendar API を使うPythonスクリプト（`scripts/`配下）。詳細は [SETUP.md](SETUP.md)。
- **想定する利用シーン**: 週末や月末に、直近の活動記録・金銭データをもとに振り返りレポートを作成したいとき。または週末に、来週の方針・アクション検討につながる振り返り質問を作りたいとき。

## 2. 事前準備（セットアップ）

Google Sheets/Docs/Drive/Calendar APIの認証が必要。初回実行時にスクリプトが認証エラーを返した場合、[SETUP.md](SETUP.md)の手順に従って `client_secret.json` を配置し認証を行う。詳細な取得方法・トラブルシューティングも同ファイルに記載。

## 3. 使い方

- **呼び出し方法**: `/retrospective` で明示的に呼び出す
- **入力例**: `/retrospective`（呼び出し後、AskUserQuestionで「レポート作成」か「週末振り返り質問生成」かを選択）
- **出力例**:
  - レポート作成: `output/yyyyMMdd-weekly-retrospective.md` または `output/yyyyMMdd-monthly-retrospective.md`
  - 週末振り返り質問生成: `output/yyyyMMdd-weekly-questions.md`（回答はこのファイルに直接書き込む想定）
- **手順**:
  1. SKILL.md Phase 0でワークフローを選択
  2. **レポート作成**: [WORKFLOW-REPORT.md](WORKFLOW-REPORT.md) に従い、期間選択 → 過去レポート/feedback-log読み込み → データ取得 → 分析・レポート作成 → 目標提案・総評 → サブエージェントレビュー → ユーザー確認・修正 → 完了報告
  3. **週末振り返り質問生成**: [WORKFLOW-WEEKLY-QUESTIONS.md](WORKFLOW-WEEKLY-QUESTIONS.md) に従い、feedback-log読み込み → データ取得 → 質問生成 → サブエージェントレビュー → ユーザー確認・修正 → 出力ファイル保存 → 完了報告
- **使う際のテクニック・コツ**:
  - 過去レポートはレポート作成時に最新3件まで自動参照される
  - ユーザーが指摘した誤りは `output/feedback-log.md` に蓄積され、次回実行時に自動で読み込まれる
  - `output/` はスキルディレクトリ内の `.gitignore` で除外設定済みのため、Git管理下に置いても個人の振り返り内容は誤コミットされない

## 4. 保守・拡張ガイド

### ファイル構成

| ファイル | 役割 |
|---------|------|
| SKILL.md | ワークフロー選択の共通エントリーポイント（Phase 0のみ） |
| WORKFLOW-REPORT.md | 週次/月次レポート作成の全Phase手順 |
| WORKFLOW-WEEKLY-QUESTIONS.md | 週末振り返り質問生成の全Phase手順 |
| REFERENCE-LIFEGRAPH.md | LifeGraph（カレンダー+スプレッドシート）データ取得・分析観点 |
| REFERENCE-DAILY.md | 日次記録データ取得・分析観点 |
| REFERENCE-MONEY.md | 金銭データ取得・分析観点（月次のみ） |
| REFERENCE-SUMMARY.md | 目標提案・総評の作成観点 |
| CONFIG.md | リソースURL・シート名・タグマッピング等の設定値（単一の情報源） |
| SETUP.md | Google API認証のセットアップ手順 |
| scripts/ | Google Drive/Calendar からデータを取得するPythonスクリプト群 |
| output/ | レポート・質問・feedback-log.mdの出力先（`.gitignore`で除外設定済み） |

### 修正時の手順と注意点

- `description` を変更すると自動発動の挙動が変わる（現状は`disable-model-invocation: true`のため無関係だが、将来変更する場合は要注意）
- WORKFLOWファイルにPhaseを追加する場合、SKILL.md Phase 0のTodoWrite登録例には手を加える必要はない（各WORKFLOWファイルが自分のTodoWriteをPhase 0で登録するため）
- レビュー観点を変更する場合は、WORKFLOW-REPORT.md Phase 7 / WORKFLOW-WEEKLY-QUESTIONS.md Phase 4を編集する
- CONFIG.mdの値はスクリプト・REFERENCEファイル側で直書きせず、CONFIG.mdを単一の情報源として参照する

### 依存

- ツール: Bash, Read, Write, TodoWrite, AskUserQuestion, Agent
- MCP / 外部: Google Sheets API, Google Docs API, Google Drive API, Google Calendar API（scripts/配下のPythonスクリプト経由）
- サブエージェント: `general-purpose`（Agentツールで起動、レビュー用途）

### 動作確認・テスト方法

1. `/retrospective` を実行し、Phase 0のAskUserQuestionで「レポート作成」または「週末振り返り質問生成」を選択できるか確認
2. レポート作成: 期間選択後、`output/` にファイルが作成され、Phase 7でAgentツールが起動しレビューコメントが返るか確認
3. 週末振り返り質問生成: 5つの質問が生成され、サブエージェントレビュー後にユーザー確認が行われるか確認
4. ユーザー指摘を入力した場合、`output/feedback-log.md` に追記されるか確認
5. 認証エラー時は [SETUP.md](SETUP.md) の手順で解消できるか確認
