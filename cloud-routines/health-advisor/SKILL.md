---
name: health-advisor
description: 「食事」シートの摂取カロリー・PFC・歩数・睡眠時間の空欄を補完し、健康診断結果PDFと栄養バランスガイド・運動量ガイド・睡眠ガイドを踏まえて健康レポート・アドバイスを作成する。ルーチン実行や「食事記録」「健康レポート」「健康診断」「食事バランス」などのキーワードで使用。
allowed-tools: Read, Write, Edit, Bash, AskUserQuestion, Agent, WebSearch, TodoWrite, Skill, Artifact, mcp__6be4de41-f7b5-4f2f-9ec2-faf294bb3fe1__download_file_content, mcp__6be4de41-f7b5-4f2f-9ec2-faf294bb3fe1__search_files, mcp__6be4de41-f7b5-4f2f-9ec2-faf294bb3fe1__read_file_content, mcp__e30046cb-8f74-410b-bbfa-1b4564720373__get_values, mcp__e30046cb-8f74-410b-bbfa-1b4564720373__update_values
user-invocable: true
disable-model-invocation: true
---

# health-advisor

健康管理に関する2つのワークフローを提供する。最初にどちらを行うかを判定し、対応するWORKFLOWファイルの手順に従うこと。

日本語で回答すること。

## Phase 0: Todo登録

TodoWriteツールが使える環境なら、以下を登録する（使えなければ省略してよい）。

```json
[
  {"content": "Phase 1: フロー判定", "activeForm": "フローを判定中", "status": "pending"},
  {"content": "選択したWORKFLOWファイルの手順を実行", "activeForm": "選択したワークフローを実行中", "status": "pending"}
]
```

## Phase 1: フロー判定

ユーザー発話・ルーチンのプロンプト文言から、以下のどちらを行うかを判定する。

| 判定 | 進む先 |
|------|--------|
| 食事・歩数・睡眠を記録したい（「食事記録して」「昨日の記録をつけて」等） | [WORKFLOW-RECORD.md](WORKFLOW-RECORD.md) |
| 健康レポート・アドバイスが欲しい（「健康レポート作成して」「アドバイスして」等） | [WORKFLOW-REPORT.md](WORKFLOW-REPORT.md) |

判定できない場合のみ、AskUserQuestionでどちらを行うか確認する。

判定後は、選ばれたWORKFLOWファイルのPhase構成に従って最後まで実行する。本ファイルのPhaseには戻らない。

## 実行環境の前提

ローカルのClaude Code・Claude.aiのクラウドルーチンのどちらでも動くように書いている。

- **スキルディレクトリ**: このSKILL.mdがあるディレクトリ。以下、手順中の `<SKILL_DIR>` はその絶対パスに置き換える（例: ローカルは `~/.claude/skills/health-advisor`、Claude.aiは `/mnt/skills/user/health-advisor` 等）
- **作業ディレクトリ**: 一時ファイル（エクスポート結果・JSON・HTML等）は最初に `mktemp -d` で作ったディレクトリ（以下 `<WORK>`）に置く。スキルディレクトリには書き込まない（アップロードしたスキルは書き換えられないため）
- **コネクタのツール名**: コネクタIDは環境ごとに異なる。手順中は「Google Driveコネクタの `download_file_content`」のように、コネクタ名とツール名で指す。該当するツールを名前の末尾で探して使う
- **永続データ**: 記録は「食事」シート、過去の号（レポート本文）・フィードバック履歴・ガイド更新候補はアーティファクト「からだ週報」の `weeks/`・`data/state.json`、健康診断PDFはDriveフォルダに置く。週次サマリーは保存せず毎回シートから集計する（[CONFIG.md](CONFIG.md)「永続データの置き場所」）

## 共通の設計方針

- **入力データの置き場所**: 食事・歩数・睡眠の記録は「食事」シートに集約し、日付・朝食・昼食・夕食はユーザーが入力する。健康診断結果PDFはDriveフォルダに手動で置く
- **書き込みは確認なしで実行**: 記録フローの「食事」シートへの補完、レポート作成フローのアーティファクトの更新（ガイド更新候補の追記を含む）は、ユーザーへの確認を挟まずそのまま行う（フィードバックの追記だけは確認を取る）
- **OAuthトークンを使う処理は呼ばない**: トークン失効でルーチンが止まらないようにするため。`google-drive-skill` のスクリプトやGoogle APIクライアントは使わない
- **読み取りはGoogle Driveコネクタを使う**: 両フローとも、スプレッドシートをコネクタでxlsxエクスポートし、`read_sheets_export.py` で必要な行を抽出する（「食事」・LifeGraphの両シートを1回のエクスポートで読む）
- **シートへの書き込みはGoogle Sheetsコネクタを使う**: Driveコネクタにはセル書き込み手段がないため、`update_values` で行う。接続確認は書き込み・見積もりより先に行う（[SETUP.md](SETUP.md)）
- **アーティファクト公開**: レポート作成フローでは、mdレポートを元にClaudeアーティファクト「からだ週報」を毎週同じURLで更新する（手順は[WORKFLOW-REPORT.md](WORKFLOW-REPORT.md) Phase 7）
- **レビュー**: レポート作成フローでは、成果物を提示する前に必ずレビューを行う。Agentツールがあればサブエージェント（`general-purpose`）に、なければ同じ観点で自己レビューする
- **医療的な断定を避ける**: レポート・アドバイスでは診断や処方に相当する断定表現を避け、「一般的な目安」「気になる場合は医療機関へ相談」等の表現に留める

## 使用スクリプト

いずれも標準ライブラリのみで動く（pipのインストール不要）。

| 操作 | スクリプト |
|------|-----------|
| （レポート作成フロー）xlsxエクスポートから直近7日分の記録と、今週・過去の週次サマリー（シートから集計）を抽出 | `python3 <SKILL_DIR>/scripts/read_sheets_export.py --input <エクスポート結果ファイル> --date YYYY-MM-DD` |
| （記録フロー）xlsxエクスポートから前日分の記録有無と、補完が必要な行（書き込み範囲付き）を抽出 | `python3 <SKILL_DIR>/scripts/read_sheets_export.py --mode record --input <エクスポート結果ファイル> --date YYYY-MM-DD` |
| 食事記録から栄養（カロリー・PFC）を計算 | `python3 <SKILL_DIR>/scripts/calc_nutrition.py --input <食品リストJSON>` |
| からだ週報の状態（号の一覧・フィードバック履歴・ガイド更新候補）の検証・追記 | `python3 <SKILL_DIR>/scripts/artifact_state.py load --input <state.json> --out <WORK>/state.json`（`add-feedback`・`add-candidate`・`resolve-candidate`・`init` もある） |
| レポートmd・週次サマリー・状態から、からだ週報のファイル一式（最新号・今週号・状態）を生成 | `python3 <SKILL_DIR>/scripts/build_artifact.py --date YYYY-MM-DD --report <md> --history <read_sheets_exportの出力JSON> --state <WORK>/state.json --out-dir <WORK>/artifact` |

## 参照ガイド（レポート作成時に使用）

- [references/nutrition-guide.md](references/nutrition-guide.md): 栄養バランスガイド
- [references/exercise-guide.md](references/exercise-guide.md): 運動量ガイド
- [references/sleep-guide.md](references/sleep-guide.md): 睡眠ガイド（ITエンジニア・PC作業が多い人向け）
- [references/report-format.md](references/report-format.md): レポートの構成と文章ルール

## ルーチン登録例

ルーチンを2つ登録し、どちらもGoogle Drive・Google Sheetsコネクタを有効にする。

- **記録用（毎朝実行推奨）**: 「health-advisorスキルで食事記録フローを実行して。無人実行」
- **レポート用（週1回程度を推奨）**: 「health-advisorスキルで健康レポート作成フローを実行して。無人実行」

## エラー対応

| エラー | 対応 |
|-------|------|
| CONFIG.mdが見つからない | スキルディレクトリにCONFIG.mdが存在するか確認する |
| Google Drive・Google Sheetsコネクタが使えない | 処理を中止し、コネクタの再接続を依頼する（OAuthスクリプトには切り替えない） |
| `read_sheets_export.py` でシートが見つからない（シート名変更等） | `availableSheets` に表示された正しいシート名をCONFIG.mdの各 `sheet_name` に反映するようユーザーに確認する |
| `read_sheets_export.py` の `warnings` が出た（今週のPFCが未補完等） | レポート作成は続行し、最終出力にwarningsの内容を明記する |
| からだ週報の `data/state.json` が読めない | WORKFLOW-REPORT.md Phase 1-4の代替手順に従う。状態が取れないままpublishしない（号の一覧・フィードバックが消えるため） |
| 該当日の行がLifeGraphシートに見つからない | 歩数・睡眠時間を「取得できませんでした」として記録を続行し、その旨を明記する（翌日以降の記録フローで再補完） |
| 健康診断フォルダにPDFが存在しない・読めない | 健康診断結果の分析はスキップし、食事・歩数・睡眠のみでレポートを作成する旨を明記する |
| 「食事」シートに直近の記録がない | ある範囲のデータのみでレポートを作成し、記録不足の旨を明記する |
