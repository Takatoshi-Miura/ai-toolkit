# WORKFLOW-REPORT: 健康レポート作成フロー

直近1週間の食事・歩数・睡眠記録と最新の健康診断結果を踏まえ、健康レポート・アドバイスを作成する。

表記（`<SKILL_DIR>`・`<WORK>`・コネクタのツール名の指し方）は[SKILL.md](SKILL.md)「実行環境の前提」に従う。

## Phase 0: Todo登録

TodoWriteツールが使える環境なら、以下を登録する（使えなければ省略してよい）。

```json
[
  {"content": "Phase 1: 入力データの読み込み（シート/からだ週報の状態/健康診断PDF/ガイド）", "activeForm": "入力データを読み込み中", "status": "pending"},
  {"content": "Phase 2: 栄養データの確認", "activeForm": "栄養データを確認中", "status": "pending"},
  {"content": "Phase 2.5: 仮説生成", "activeForm": "数値データから仮説を生成中", "status": "pending"},
  {"content": "Phase 3: レポート初稿作成", "activeForm": "レポート初稿を作成中", "status": "pending"},
  {"content": "Phase 4: 正確性チェック（Web調査）", "activeForm": "正確性をチェック中", "status": "pending"},
  {"content": "Phase 5: レビュー", "activeForm": "レビュー中", "status": "pending"},
  {"content": "Phase 6: 提示・保存", "activeForm": "レポートを提示・保存中", "status": "pending"},
  {"content": "Phase 7: アーティファクト更新", "activeForm": "アーティファクトを更新中", "status": "pending"},
  {"content": "Phase 8: フィードバック収集", "activeForm": "フィードバックを収集中", "status": "pending"}
]
```

## Phase 1: 入力データの読み込み

シートはGoogle Driveコネクタで読む（OAuthトークンを使うスクリプトは呼ばない）。

### 1-1. 作業ディレクトリとレポート作成日の確定

作業ディレクトリを `mktemp -d` で作り、`<WORK>` として以降で使う。レポート作成日（日本時間の今日）を以下で確定する（クラウド環境の時計はUTCのため、`date` コマンドで決めない）。

```bash
python3 -c "import datetime,zoneinfo;print(datetime.datetime.now(zoneinfo.ZoneInfo('Asia/Tokyo')).date())"
```

### 1-2. スプレッドシートのxlsxエクスポート

Google Driveコネクタの `download_file_content` を以下の引数で呼ぶ：

- `fileId`: CONFIG.mdの `meals.url` から抽出したファイルID
- `exportMimeType`: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`

結果はサイズ超過でファイルに保存され、保存先パスがツール結果に表示される。このパスを1-3で使う。

コネクタが使えない・結果がファイルに保存されなかった場合はレポート作成を中止し、コネクタの再接続を依頼する。

### 1-3. シートの抽出

```bash
python3 <SKILL_DIR>/scripts/read_sheets_export.py --input <1-2の保存先パス> --date <レポート作成日> > <WORK>/sheets.json
```

`<WORK>/sheets.json` を読む。レポート作成日の前日を起点に直近7日分が返る。

- `daily`: 日ごとの数値化済み `calorie_kcal`・`protein_g`・`fat_g`・`carb_g`・`protein_pct`・`fat_pct`・`carb_pct`・`steps`・`sleep_hours`。摂取カロリー・PFCは記録フロー（[WORKFLOW-RECORD.md](WORKFLOW-RECORD.md) Phase 4）で見積もり済みの「食事」シートの値。歩数・睡眠時間は「食事」シートの値を優先し、空欄・「取得できませんでした」の日はLifeGraphの値で補完済み（`*_source` に出どころ）。`null` は欠損
- `meals`: 「食事」シートの行（キーは `date`・朝食・昼食・夕食・摂取カロリー・歩数・睡眠時間・たんぱく質・脂質・炭水化物・備考）。朝食・昼食・夕食のいずれかが空欄の日は記録途中としてレポートにその旨を書く
- `lifegraph`: LifeGraph全項目（仕事・自己研鑽・運動・パートナー・リフレッシュ・歩数・睡眠等、キーはヘッダー名）。Phase 2.5の仮説生成に使う
- `current_summary`: 今週の週次サマリー（週平均。PFC比率は期間内のPFCの合計から算出）。`complete: false` なら欠けている指標がある
- `summaries`: シートから集計した過去の週の週次サマリー（Phase 7の週次推移で、公開済みの号がない週を埋めるのに使う）
- `warnings`: 続行可能な問題。最終出力に明記する
- 期間内でシートに存在しない日はスキップし、他の日のデータで続行する

### 1-4. からだ週報の状態の読み込み

公開中のアーティファクト「からだ週報」には、号の一覧・フィードバック履歴・ガイド更新候補が `data/state.json` として保存されている。

1. Artifactツールの `action: "read_file"` を、`url`: CONFIG.mdの `artifact.url`、`path`: `data/state.json` で呼ぶ。保存先パスがツール結果に表示される
2. 以下で検証し、作業ディレクトリに書き出す

   ```bash
   python3 <SKILL_DIR>/scripts/artifact_state.py load --input <1の保存先パス> --out <WORK>/state.json
   ```

- `read_file` が使えない場合: Artifactツールの `action: "read"` で同じURLを読み、HTML内の `<script type="application/json" id="health-advisor-state">` の中身（JSON）だけを `<WORK>/state_raw.json` に書き出して、2を `--input <WORK>/state_raw.json` で実行する
- Artifactツール自体がない環境の場合: `artifact_state.py init --out <WORK>/state.json` で空の状態を作り、Phase 7のpublishは行わない（公開中の号の一覧・フィードバックを空で上書きしないため）

`<WORK>/state.json` の `feedback` が過去のフィードバック（日付・指摘・反映）。次のレポートで同じ指摘を繰り返さないために使う。2の出力の `open_candidates` は未反映のガイド更新候補（Phase 4で同じ候補を重ねて追記しないために使う）。

### 1-5. 健康診断結果の読み込み

Google Driveコネクタの `search_files` を以下のクエリで呼ぶ：

- `query`: `parentId = '<CONFIG.mdの drive.checkup_folder_id>' and mimeType = 'application/pdf'`

結果に `nextPageToken` があれば `pageToken` に渡して残りも取得する。ファイル名（`健康診断_YYYYMMDD.pdf`）の日付で並べ、最新と1つ前の2件を、Google Driveコネクタの `read_file_content` で読む（前回比較に使う）。テキストが取れない場合は `download_file_content` で保存されたPDFをReadツールで読む。PDFがない・読めない場合は[SKILL.md](SKILL.md)のエラー対応に従いスキップする。

### 1-6. ガイドの読み込み

[references/nutrition-guide.md](references/nutrition-guide.md)・[references/exercise-guide.md](references/exercise-guide.md)・[references/sleep-guide.md](references/sleep-guide.md) を読む。

**成功確認**: 直近1週間の記録とガイド類が読み込めた（PDFなし・LifeGraph一部欠損の場合もその旨を記録して続行） → 次のPhaseへ

## Phase 2: 栄養データの確認

カロリー・PFCは、記録フローで見積もって「食事」シートに保存済みの値（Phase 1-3の `daily`・`current_summary`）をそのまま使う。食事内容から再計算はしない（二重計算による値のブレを避けるため）。

- PFCが空欄の日がある場合（記録フローの補完待ち）は、その日を除いた値であることをレポートに書く
- `current_summary.pfc_days` が0の場合は、PFCの評価をせず「PFCは記録フローの補完後に評価する」とだけ書く

**成功確認**: 日ごとの値と週平均を確認し、欠損日を把握した → 次のPhaseへ

## Phase 2.5: 仮説生成

**この時点ではまだ栄養・運動・睡眠ガイドの目安に沿った定型分析を始めない。** Phase 1で取得済みの数値データ（食事のカロリー・PFC、歩数、睡眠時間、LifeGraph全項目）だけを横断的に見て、指標同士の相関や違和感のある変化点に着目し、3〜5件の仮説を書き出す。

- 対象は直近1週間の数値データ全体（`feedback`・ガイド類・過去レポートはまだ見ない）
- ガイドの4項目（食事・運動・睡眠・健診）に沿った定型的な指摘ではなく、一見無関係に見える指標同士を掛け合わせた仮説を優先する（例: 「体重・歩数が横ばいの一方で睡眠時間が短い日が続いている週は、翌週の自己投資時間も落ちている」）
- 仮説は断定せず「〜という可能性がある」という推測の形で書き出す

**成功確認**: 数値データの横断から3〜5件の仮説を書き出した → 次のPhaseへ

## Phase 3: レポート初稿作成

[references/report-format.md](references/report-format.md) の構成と文章ルールに従って初稿を作成する。Phase 1-4の `feedback` の過去指摘も反映する。

**成功確認**: レポート初稿ができた → 次のPhaseへ

## Phase 4: 正確性チェック（Web調査）

初稿内で言及した栄養・運動・睡眠に関する数値・基準（例: 「1日8,000歩」「PFC比率○%」等）について、WebSearchで最新の公的情報と照らし合わせ、古い・不正確な記述がないか確認する。

- 誤り・古い情報が見つかった場合は初稿を修正する
- 参照ガイド（references/配下）が古くなっていると判明した場合は、ガイドを直接書き換えない（アップロードしたスキルは書き換えられないため）。「ガイド更新候補」として、からだ週報の状態に1件ずつ追記する（Phase 1-4の `open_candidates` にある候補は追記しない）。反映は在席時にローカルの正本で行う

  ```bash
  python3 <SKILL_DIR>/scripts/artifact_state.py add-candidate --input <WORK>/state.json \
    --date <レポート作成日> --target "<対象ファイル>「<該当箇所>」" --proposal "<修正案>" --source "<出典URL>" \
    --out <WORK>/state.json
  ```

  候補はPhase 7のpublishで、からだ週報の「ガイド更新候補」欄に表示される

**成功確認**: 記述内容の裏取りが完了し、必要な修正を反映した → 次のPhaseへ

## Phase 5: レビュー

Agentツールがあれば、`subagent_type: general-purpose` で起動し、以下を含む自己完結したプロンプトでレビューを依頼する（`run_in_background: false` で同期的に受け取る）。Agentツールがない環境では、同じ観点のチェックリストで自己レビューする（修正→再チェックは最大3回）。

- レビュー対象のレポート本文
- レビュー観点:
  - 栄養・運動・睡眠の計算値と評価の整合性（過不足の判定が参照ガイドの目安と矛盾していないか）
  - 医療的な断定表現になっていないか（「異常です」「病気です」等の診断的な言い切りがないか）
  - Phase 1-4の `feedback` の過去指摘が反映されているか
  - 記録が不足しているデータ（歩数取得失敗日等）について誤った断定をしていないか
  - 「気になる兆候」セクションがガイド比較の言い換えになっておらず、Phase 2.5の仮説がそのまま（推測である旨を明記して）反映されているか
  - [references/report-format.md](references/report-format.md) の構成・文章ルールに沿っているか（週平均の再掲・セクション間の重複・長い文がないか）

指摘があれば反映し、必要なら再度レビューする。

**成功確認**: レビューで重大な指摘がない、または指摘をすべて反映した → 次のPhaseへ

## Phase 6: 提示・保存

ユーザー確認を挟まずに実行する（無人実行時も同様）。

### 6-1. レポートの表示

レポートをチャット上に表示する。無人実行の場合は、レポート末尾に「ユーザー確認・フィードバック収集（Phase 8）は次回在席時に行う」旨を記載してから次へ進む。

### 6-2. レポートmdの書き出し

`<WORK>/<レポート作成日>_report.md` に書き出す（Phase 7の入力に使う）。レポートはPhase 7で、からだ週報の今週号（`weeks/<レポート作成日>.html`）として残る。

### 6-3. 週次サマリーの確認

今週の週次サマリーはPhase 1-3の `current_summary`（`<WORK>/sheets.json` 内）を使う。レポート本文で週平均に触れる場合はこの値と一致させる。シートへの保存はしない（週平均は「食事」シートからいつでも集計し直せ、公開した号の値は Phase 7 で `data/state.json` に残るため）。

**成功確認**: レポートmdを書き出し、週次サマリーとレポートの数値が一致していることを確認した → 次のPhaseへ

## Phase 7: アーティファクト更新

ユーザー確認を挟まずに実行する（無人実行時も同様）。

### 7-1. デザインガイドの読み込み

`artifact-design` スキルが使える環境なら読み込む（Artifactへのpublish前に必須）。見た目は `assets/artifact-template.html` で固定しているため、テンプレートは変更しない。

### 7-2. ファイル一式の生成

```bash
python3 <SKILL_DIR>/scripts/build_artifact.py --date <レポート作成日> \
  --report <WORK>/<レポート作成日>_report.md \
  --history <WORK>/sheets.json \
  --state <WORK>/state.json \
  --out-dir <WORK>/artifact
```

`<WORK>/artifact/` に以下が生成される。`success: false` の場合はエラー内容に従い、mdを修正して再実行する。

- `index.html`: 最新号のページ（今週の4指標・既定8週分の推移・レポート本文・過去のレポート一覧・フィードバック履歴）
- `weeks/<レポート作成日>.html`: 今週号の単独ページ（過去の号として残る）
- `data/state.json`: 号の一覧（今週号を追加済み）とフィードバック履歴

週次推移は、公開済みの号の値を優先し、号のない週をシートの集計値で埋める。

### 7-3. publish

Artifactツールで以下を指定してpublishする。

- `file_path`: `<WORK>/artifact/index.html`（絶対パス）
- `url`: CONFIG.mdの `artifact.url`
- `root`: `<WORK>/artifact`
- `files`: `{"weeks/<レポート作成日>.html": "weeks/<レポート作成日>.html", "data/state.json": "data/state.json"}`
- `label`: `"<レポート作成日>号"`

過去の号のページ（`weeks/` 配下の他のファイル）は `files` に含めなくてもサーバー側に残る。

- 他所で更新済みのため拒否された場合: Phase 1-4からやり直して最新の状態を読み、Phase 4で追記したガイド更新候補を追記し直してから、7-2から再実行する（`force` は使わない）
- Artifactツールがない・publishできない環境の場合: 失敗扱いにせず、からだ週報を更新できなかった旨と、Phase 4のガイド更新候補（あれば）を最終出力に示して次へ進む（レポート本文はPhase 6-1でチャットに表示済み）

**成功確認**: アーティファクトのpublishが成功してURLを提示した、またはpublishできなかった旨を最終出力に示した → 次のPhaseへ

## Phase 8: フィードバック収集

無人実行の場合はこのPhaseをスキップし、最終出力で「フィードバック収集は次回在席時に行う」と伝える。

### 8-1. 感想・指摘のヒアリング

ユーザーにレポート内容への感想・修正指摘を尋ねる。

### 8-2. レポートへの反映

指摘があれば、`<WORK>/<レポート作成日>_report.md` に反映する。

### 8-3. フィードバックの記録とアーティファクトの更新

記録内容（日付・指摘・反映）を提示して確認を取ってから、Phase 7で生成した状態に追記する。

```bash
python3 <SKILL_DIR>/scripts/artifact_state.py add-feedback --input <WORK>/artifact/data/state.json \
  --date <レポート作成日> --issue "<ユーザーからの指摘内容>" --applied "<レポートにどう反映したか>" \
  --out <WORK>/state.json
```

続けて、Phase 7-2（`--state <WORK>/state.json`）・7-3を再実行する。今週号は置き換えられ、フィードバック履歴に追記される。

**成功確認**: フィードバックの有無を確認した（あれば反映・記録済み） → 完了
