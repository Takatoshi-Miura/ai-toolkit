# WORKFLOW-RECORD: 食事・歩数・睡眠記録フロー

ユーザーが「食事」シートに入力した日付・朝食・昼食・夕食をもとに、摂取カロリー・歩数・睡眠時間・たんぱく質・脂質・炭水化物の空欄を補完する。読み取りはGoogle Driveコネクタ、書き込みはGoogle Sheetsコネクタで行い、OAuthトークンを使うスクリプトは呼ばない。行の追記・食事内容の質問はしない。

表記（`<SKILL_DIR>`・`<WORK>`・コネクタのツール名の指し方）は[SKILL.md](SKILL.md)「実行環境の前提」に従う。

## Phase 0: Todo登録

TodoWriteツールが使える環境なら、以下を登録する（使えなければ省略してよい）。

```json
[
  {"content": "Phase 1: Sheetsコネクタの接続確認", "activeForm": "Sheetsコネクタの接続を確認中", "status": "pending"},
  {"content": "Phase 2: スプレッドシートのxlsxエクスポート", "activeForm": "スプレッドシートをエクスポート中", "status": "pending"},
  {"content": "Phase 3: 補完が必要な行の抽出", "activeForm": "補完が必要な行を抽出中", "status": "pending"},
  {"content": "Phase 4: 摂取カロリー・PFCの見積もり", "activeForm": "摂取カロリー・PFCを見積もり中", "status": "pending"},
  {"content": "Phase 5: 「食事」シートへ書き込み", "activeForm": "「食事」シートへ書き込み中", "status": "pending"},
  {"content": "Phase 6: 結果の報告", "activeForm": "結果を報告中", "status": "pending"}
]
```

## Phase 1: Sheetsコネクタの接続確認

作業ディレクトリを `mktemp -d` で作り、そのパスを `<WORK>` として以降で使う。

Google Sheetsコネクタの `get_values` を以下の引数で呼ぶ：

- `spreadsheetId`: CONFIG.mdの `meals.url` から抽出したファイルID
- `range`: `'<meals.sheet_name>'!A1:K1`

ツールが存在しない・エラーになる・ヘッダーがCONFIG.mdの「食事シートについて」に記載の列構成と一致しない場合は、**以降のPhaseを実行せず**、原因とGoogle Sheetsコネクタの再接続（またはシート構成の確認）を依頼して終了する。

**成功確認**: 11列のヘッダーが一致した → 次のPhaseへ

## Phase 2: スプレッドシートのxlsxエクスポート

Google Driveコネクタの `download_file_content` を以下の引数で呼ぶ：

- `fileId`: Phase 1と同じファイルID
- `exportMimeType`: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`

結果はサイズ超過でファイルに保存され、保存先パスがツール結果に表示される。このパスをPhase 3で使う。

コネクタが使えない・結果がファイルに保存されなかった場合は処理を中止し、コネクタの再接続を依頼する。

**成功確認**: エクスポート結果の保存先パスを得た → 次のPhaseへ

## Phase 3: 補完が必要な行の抽出

対象日（日本時間の前日、`YYYY-MM-DD`）を以下で確定する（クラウド環境の時計はUTCのため、`date` コマンドで決めない）。

```bash
python3 -c "import datetime,zoneinfo;print((datetime.datetime.now(zoneinfo.ZoneInfo('Asia/Tokyo'))-datetime.timedelta(days=1)).date())"
```

続けて以下を実行する。

```bash
python3 <SKILL_DIR>/scripts/read_sheets_export.py --mode record --input <Phase 2の保存先パス> --date <前日の日付>
```

出力の使い方：

- `backfill`: 補完が必要な行。各行の `write_range` がPhase 5の書き込み範囲、`missing` が補完対象の列、`needs_estimate` がPhase 4で食事内容から見積もる列（摂取カロリー・たんぱく質・脂質・炭水化物のうち空欄のもの）
  - 摂取カロリー・歩数・睡眠時間: 空欄または `取得できませんでした` の行（対象日以前の全期間）
  - たんぱく質・脂質・炭水化物: 空欄の行（直近56日分のみ。摂取カロリーは入っていてPFCだけ空欄の過去分は、1回14行までに絞られる）
- `write_columns`: `write_range` の列順（摂取カロリー・歩数・睡眠時間・たんぱく質・脂質・炭水化物）
- `pfc_backfill_remaining`: 今回は見送ったPFCだけ空欄の行数（次回以降の実行で補完される）
- `target_status`: 前日の行の入力状況（`complete`=朝食・昼食・夕食すべて入力済み / `partial`=入力途中 / `missing`=行なし）。Phase 6の報告に使う

**成功確認**: `success: true` の出力を得た → 次のPhaseへ

## Phase 4: 摂取カロリー・PFCの見積もり

`backfill` のうち、`needs_estimate` が空でなく、かつ `meals_complete: true` の行だけを対象にする（`false` は入力途中のため書かない）。

朝食・昼食・夕食の内容から、Claudeが一般的な栄養成分表に基づき食品ごとのカロリー・PFC（たんぱく質/脂質/炭水化物）を見積もり、JSON形式（`[{"name": ..., "calorie": ..., "protein": ..., "fat": ..., "carb": ...}, ...]`）の一時ファイルを行ごとに `<WORK>` 配下に作成して、以下を実行する：

```bash
python3 <SKILL_DIR>/scripts/calc_nutrition.py --input <一時JSONファイルパス>
```

結果は `needs_estimate` に含まれる列だけに使う（すでに値がある列は書き換えない）。

- **摂取カロリー**: `totalCalorie` を四捨五入した整数を `<値>kcal` 形式（例: `1530kcal`）
- **たんぱく質・脂質・炭水化物**: `totalProteinG`・`totalFatG`・`totalCarbG` を小数1桁で `<値>g` 形式（例: `45.2g`）

「何も食べていない」等で食品がない場合は `0kcal`・`0.0g` とする。

**成功確認**: 対象行すべての見積もりができた → 次のPhaseへ

## Phase 5: 「食事」シートへ書き込み

`backfill` の各行について、`write_columns` の順に値を並べる。

- **摂取カロリー・たんぱく質・脂質・炭水化物**: Phase 4の値。対象外の列・行は `null`
- **歩数・睡眠時間**: `missing` に含まれ、`lifegraph` の値が `null` でなければその値。`null` なら、元が空欄の場合のみ `取得できませんでした`（元から `取得できませんでした` なら `null`）
- `missing` に含まれない列は `null`（`update_values` は `null` のセルを書き換えない）

すべて `null` の行は書かない。書く値がある行ごとに、**確認を取らず** Google Sheetsコネクタの `update_values` を以下の引数で呼ぶ：

- `spreadsheetId`: Phase 1と同じファイルID
- `range`: 行の `write_range`
- `values`: `[[<摂取カロリー>, <歩数>, <睡眠時間>, <たんぱく質>, <脂質>, <炭水化物>]]`

エラーになった行はエラー内容を記録して次の行へ進む（全体のフローは中断しない）。

**成功確認**: 書く値がある行をすべて処理した（書けなかった行はその旨を記録済み） → 次のPhaseへ

## Phase 6: 結果の報告

以下をチャットに表示する。

- 書き込んだ行ごとの日付と値（摂取カロリー・PFCは見積もりである旨を添える）
- 書けなかった行とエラー内容
- 入力途中のため摂取カロリー・PFCを書かなかった行
- `pfc_backfill_remaining` が1以上なら、PFCの過去分の補完が残り何行か
- `target_status` が `missing` なら「前日（<日付>）の食事が未入力」、`partial` なら「入力途中」である旨

**成功確認**: 報告を表示した → 完了
