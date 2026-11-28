# health-advisor 設定

このファイルは人が直接編集する設定ファイル。リポジトリ上はテンプレートのため、`<...>` を自分の値に置き換えてから使う（`artifact.url` は初回のレポート公開後に決まる）。シート名・フォルダ・URLの変更はここで行う。スキルをClaude.aiにアップロードしている場合、変更後は再アップロードが必要（[SETUP.md](SETUP.md)）。

## リソース設定

```yaml
lifegraph:
  url: "https://docs.google.com/spreadsheets/d/<SPREADSHEET_ID>/edit"
  sheet_name: "Googleカレンダー集計"
meals:
  url: "https://docs.google.com/spreadsheets/d/<SPREADSHEET_ID>/edit"
  sheet_name: "食事"
drive:
  checkup_folder_id: "<CHECKUP_FOLDER_ID>"
artifact:
  url: "https://claude.ai/code/artifact/<ARTIFACT_ID>"
```

`meals`・`lifegraph` は同じスプレッドシート（`meals.url`）内のシート。

## 永続データの置き場所

実行ごとにファイルが消えるクラウド環境でも動くよう、スキル外に保存する。

| データ | 置き場所 | 書き込むフェーズ |
|------|------|------|
| 食事・歩数・睡眠・摂取カロリー・PFC | 「食事」シート | WORKFLOW-RECORD.md Phase 5 |
| 週次サマリー | 保存しない（「食事」シート・LifeGraphシートから毎回集計。公開した号の値はアーティファクトの `data/state.json` に残る） | — |
| 過去の号（レポート本文）・フィードバック履歴・ガイド更新候補 | アーティファクト「からだ週報」の `weeks/<日付>.html`・`data/state.json` | WORKFLOW-REPORT.md Phase 4・7・8 |
| 健康診断結果PDF | Driveフォルダ `drive.checkup_folder_id`（ファイル名 `健康診断_YYYYMMDD.pdf`、手動配置） | — |

## アーティファクトについて

`artifact.url` は週次レポートを公開するClaudeアーティファクト「からだ週報」のURL（WORKFLOW-REPORT.md Phase 1-4・7で使用）。複数ファイル構成で、`index.html`（最新号）・`weeks/<日付>.html`（各号）・`data/state.json`（号の一覧・フィードバック履歴・ガイド更新候補）からなる。`data/state.json` を消すと号の一覧・フィードバック・ガイド更新候補が失われるため、手で編集・削除しない。

## 列位置の補足

`scripts/read_sheets_export.py` はシートの1行目（ヘッダー行）を読み取り、列名をキーとする辞書を返す。列の追加・並べ替えがあってもこのファイルの修正は不要。シート名・URLが変わった場合のみ上記を修正する。

## 食事シートについて

`meals.sheet_name` は食事・歩数・睡眠を記録する「食事」シートの名前。列構成（日付|朝食|昼食|夕食|摂取カロリー|歩数|睡眠時間|たんぱく質|脂質|炭水化物|備考）はWORKFLOW-RECORD.md・WORKFLOW-REPORT.mdの記述と密結合しているため、列の追加・並べ替えを行う場合は両WORKFLOWファイル・SETUP.mdも合わせて確認すること（記録フローPhase 1はこの11列のヘッダーで接続確認する。`read_sheets_export.py` はヘッダー名「摂取カロリー」〜「炭水化物」の6列から書き込み範囲を求めるため、この6列はこの順で隣接させておく）。E列（摂取カロリー）とH〜J列（たんぱく質・脂質・炭水化物）は、朝食・昼食・夕食のテキストから`calc_nutrition.py`で見積もった値を `<値>kcal`・`<値>g` 形式で格納する（WORKFLOW-RECORD.md Phase 4参照）。
