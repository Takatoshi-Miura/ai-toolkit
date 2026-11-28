# 健康管理アドバイザー（health-advisor）

## 1. 概要

- **何をするスキルか**: 「食事」シートの摂取カロリー・PFC・歩数・睡眠時間の空欄を補完し、健康診断結果PDFと栄養バランスガイド・運動量ガイド・睡眠ガイドを踏まえて健康レポート・アドバイスを作成する。
- **発動条件**:
  - 呼び出し時のフロー判定キーワード: 「食事記録」「健康レポート」「健康診断」「食事バランス」など
  - スラッシュ呼び出し: `/health-advisor` で可能
  - 自動発動: なし（`disable-model-invocation: true` のため、明示呼び出しのみ）
- **依存の有無**: 読み取りは両フローともGoogle Driveコネクタ（スプレッドシートのxlsxエクスポート・健康診断PDF）。「食事」シートへの書き込みはGoogle Sheetsコネクタ（`update_values`）、からだ週報（過去の号・フィードバック・ガイド更新候補）の読み書きはArtifactツール。OAuthトークンを使う処理は呼ばない
- **実行環境**: ローカルのClaude Code・Claude.aiのクラウドルーチンの両方で動く（永続データはスキル外のシート・Drive（健康診断PDFのみ）・アーティファクトに置く）
- **想定する利用シーン**: ユーザーが「食事」シートに日付・朝食・昼食・夕食を入力しておき、Claude.aiのクラウドルーチン（またはClaude Codeのルーチン）から1日1回程度呼び出して摂取カロリー・PFC・歩数・睡眠時間を補完するフローと、週1回程度呼び出し、直近1週間の記録と健康診断結果を踏まえた健康レポートを作成するフローの2つを使い分ける。

## 2. 事前準備（セットアップ）

Google DriveコネクタとGoogle Sheetsコネクタを接続しておく。確認手順は [SETUP.md](SETUP.md) を参照。

健康診断結果を分析に含める場合は、PDFファイルをDriveの健康診断フォルダ（CONFIG.mdの `drive.checkup_folder_id`）に配置しておく。Claude.aiで使う場合のアップロード手順も [SETUP.md](SETUP.md) を参照。

## 3. 使い方

- **呼び出し方法**: `/health-advisor` での明示呼び出し、または「health-advisorスキルで食事記録フローを実行して」「health-advisorスキルで健康レポート作成フローを実行して」のような依頼
- **入力例**:
  - 記録フロー: 「食事記録して」
  - レポートフロー: 「今週の健康レポートを作成して」
- **出力例**:
  - 記録フロー: 「食事」シート（Googleスプレッドシート、CONFIG.md参照）の摂取カロリー・歩数・睡眠時間・PFC（たんぱく質・脂質・炭水化物）の空欄が埋まり、補完結果と前日分の入力有無がチャットに表示される
  - レポートフロー: チャット表示＋ Claudeアーティファクト「からだ週報」（CONFIG.mdの`artifact.url`）が同じURLのまま更新される（最新号の `index.html` に加え、各号が `weeks/<日付>.html` として残り、過去の号へのリンクから閲覧できる）
- **手順**:
  1. SKILL.md でユーザー発話から「記録」か「レポート」かを判定
  2. 記録フロー（[WORKFLOW-RECORD.md](WORKFLOW-RECORD.md)）: Sheetsコネクタの接続確認（失敗したらここで停止） → Driveコネクタでスプレッドシートを読み取り → 空欄・「取得できませんでした」（摂取カロリー・歩数・睡眠時間・PFC）の行を抽出 → 摂取カロリー・PFCを見積もり（`calc_nutrition.py`） → Sheetsコネクタで書き込み（確認なし）
  3. レポートフロー（[WORKFLOW-REPORT.md](WORKFLOW-REPORT.md)）: 直近1週間の記録を読み込み、仮説生成・ガイド比較・Web調査・サブエージェントレビューを経てレポートを作成 → アーティファクト「からだ週報」を同じURLで更新（今週号を追加） → フィードバック収集（からだ週報の `data/state.json` に追記）
- **使う際のテクニック・コツ**:
  - ルーチン登録は2つに分け、プロンプトにどちらのフローかを明記する（記録用は毎朝、レポート用は週1回程度）
  - 食事は「食事」シートに日付・朝食・昼食・夕食の3つを入力しておく。1つでも空欄の行は入力途中とみなし、摂取カロリー・PFCを書かない
  - レポートへの感想・指摘を伝えると、からだ週報の「これまでのフィードバック」に蓄積され、次回以降のレポートに反映される

## 4. 保守・拡張ガイド

### ファイル構成

| ファイル | 役割 |
|---------|------|
| SKILL.md | 概要・フロー判定・共通方針 |
| WORKFLOW-RECORD.md | 食事・歩数・睡眠の記録フロー詳細 |
| WORKFLOW-REPORT.md | レポート作成フロー詳細 |
| SETUP.md | 必要なコネクタと接続確認手順 |
| CONFIG.md | スプレッドシートURL・各シート名・DriveフォルダID・アーティファクトURL設定 |
| references/nutrition-guide.md | 食事バランスガイド（厚労省・農水省の情報を要約） |
| references/exercise-guide.md | 運動量ガイド（厚労省の身体活動・運動ガイド2023を要約） |
| references/sleep-guide.md | 睡眠ガイド（ITエンジニア・PC作業が多い人向け） |
| references/report-format.md | レポートの構成（見出し順）と文章ルール（簡潔・重複なし・週平均を再掲しない） |
| scripts/read_sheets_export.py | Driveコネクタでxlsxエクスポートしたスプレッドシートから「食事」シート・LifeGraphシートの行をヘッダー名キーで抽出（xlsx解析は標準ライブラリのみ）。既定はレポート対象期間（直近7日）と日別数値（`daily`）に加え、今週・過去12週の週次サマリー（`current_summary`・`summaries`。シートから毎回集計）、`--mode record` は記録フロー用に前日分の記録有無と、補完が必要な行をSheetsコネクタ用の書き込み範囲（`write_range`、E〜J列）付きで返す（PFCの過去分は直近56日・1回14行まで） |
| scripts/calc_nutrition.py | 食事記録からカロリー・PFCバランスを計算 |
| scripts/build_artifact.py | レポートmd・週次サマリー（`read_sheets_export.py` の出力）・からだ週報の状態から、`index.html`（最新号）・`weeks/<日付>.html`（今週号）・`data/state.json` を `--out-dir` に生成。過去の号の値は状態のものを優先する。判定基準（目安値）はスクリプト冒頭の定数 |
| scripts/artifact_state.py | からだ週報の `data/state.json`（号の一覧・フィードバック履歴・ガイド更新候補）の検証（`load`）・初期化（`init`）・フィードバック追記（`add-feedback`）・ガイド更新候補の追記（`add-candidate`）と反映済み化（`resolve-candidate`） |
| assets/artifact-template.html | アーティファクトの固定テンプレート（今週の4指標・週次推移・レポート本文・過去の号・フィードバック） |
| scripts/config_parser.py | CONFIG.mdの読み込み（標準ライブラリのみ） |
| scripts/package_skill.sh | Claude.aiアップロード用zipの作成（frontmatterをClaude.ai向けに調整） |
| 「食事」シート（Googleスプレッドシート） | 食事・歩数・睡眠・摂取カロリー・PFCの記録（日付・食事・備考はユーザーが入力、摂取カロリー・歩数・睡眠時間・PFCは自動補完。列構成はCONFIG.mdの「食事シートについて」参照） |
| アーティファクト「からだ週報」 | 過去の号（`weeks/`）と号の一覧・フィードバック履歴・ガイド更新候補（`data/state.json`）の保存先。`data/state.json` は手で編集・削除しない |
| Driveの健康診断フォルダ（CONFIG.mdの `drive.checkup_folder_id`） | 健康診断結果PDF（手動配置） |

### 修正時の手順と注意点

- `description` を変更すると自動発動の挙動が変わる（現状 `disable-model-invocation: true` のため自動発動はしない）
- OAuthトークンを使うスクリプト（`google-drive-skill` 等）を呼ぶ処理を追加しない。読み取りはDriveコネクタ、書き込みはSheetsコネクタに寄せる
- コネクタを再接続してツール名（`mcp__<コネクタID>__...`）が変わった場合は、SKILL.mdの `allowed-tools`を修正する（WORKFLOW本文はコネクタ名＋ツール名で書いているため修正不要）
- スキルファイルを変更したら `bash scripts/package_skill.sh` でzipを作り直し、Claude.aiに再アップロードする（ローカルが正本）
- Phase 4で見つかった「ガイド更新候補」（からだ週報の「ガイド更新候補」欄）は、在席時にローカルの `references/` へ反映して再アップロードする。反映後は `artifact_state.py resolve-candidate` で反映済みにし、からだ週報を再publishすると欄から消える
- LifeGraphシートの列構成（列の追加・並べ替え）が変わっても、`read_sheets_export.py` はヘッダー行から自動マッピングするため修正不要。シートのURL・シート名自体が変わった場合のみ `CONFIG.md` を修正する
- 「食事」シートのE列（摂取カロリー）・H〜J列（PFC）は記録フロー（WORKFLOW-RECORD.md Phase 4）で一度だけ見積もって書き込み、レポートフロー（WORKFLOW-REPORT.md Phase 2）はその値を再利用する設計。列構成自体を変更する場合は`CONFIG.md`・WORKFLOW-RECORD.md・WORKFLOW-REPORT.md・SETUP.mdを揃えて修正する（記録フローPhase 1は11列のヘッダー `A1:K1` で接続確認するため。`read_sheets_export.py` はヘッダー名「摂取カロリー」〜「炭水化物」の6列から書き込み範囲を求め、この6列が隣接している前提。列名を変えた場合は `read_sheets_export.py` の `build_daily`・`FILL_COLUMNS`・`PFC_COLUMNS` も修正する）
- 栄養・運動・睡眠の基準値が更新された場合は `references/` 配下の該当mdを修正する（Web調査で最新情報を確認してから更新）。アーティファクトの判定にも使うため、`scripts/build_artifact.py` 冒頭の定数も合わせて修正する
- アーティファクトの見た目を変える場合は `assets/artifact-template.html` を修正する（差し込み位置は `<!--@...-->` のプレースホルダ）。過去の号のページ（`weeks/`）は公開時のまま残るため、見た目の変更は今後の号から反映される
- WORKFLOW追加・Phase変更時は、TodoWriteの登録内容とPhase番号の対応がずれないよう注意する

### 依存

- ツール: Read, Write, Edit, Bash, AskUserQuestion, Agent, WebSearch, TodoWrite, Skill（`artifact-design`の読み込み）, Artifact, Google Driveコネクタの `download_file_content`・`search_files`・`read_file_content`, Google Sheetsコネクタの `get_values`・`update_values`
- Pythonパッケージ: なし（標準ライブラリのみ。`markdown` があれば `build_artifact.py` が使い、なければ内蔵の簡易変換を使う）
- 外部: なし（コネクタのみ、[SETUP.md](SETUP.md)）

### 動作確認・テスト方法

1. `python3 ~/.claude/skills/health-advisor/scripts/calc_nutrition.py --input <食品リストJSON>` でカロリー・PFC計算が動くか確認
2. Sheetsコネクタの `get_values` で `'食事'!A1:K1` が読めるか確認（[SETUP.md](SETUP.md)）
3. Driveコネクタの `download_file_content` でスプレッドシートをxlsxエクスポートし、`python3 ~/.claude/skills/health-advisor/scripts/read_sheets_export.py --mode record --input <保存先パス> --date <前日>` で `backfill`（各行の `write_range` を含む）・`target_status` が返るか確認
4. 同じ保存先パスで `python3 ~/.claude/skills/health-advisor/scripts/read_sheets_export.py --input <保存先パス> --date <レポート日>` を実行し、`meals`・`lifegraph` に直近7日分が入るか確認
5. 4の出力を保存したJSONを `--history` に渡し、`python3 ~/.claude/skills/health-advisor/scripts/artifact_state.py init --out <WORK>/state.json` の後、`python3 ~/.claude/skills/health-advisor/scripts/build_artifact.py --date <レポート日> --report <md> --history <4の出力> --state <WORK>/state.json --out-dir <WORK>/artifact` で `index.html`・`weeks/`・`data/state.json` が生成されるか確認
6. `/health-advisor` で記録フロー・レポートフローそれぞれを実際に実行し、「食事」シート・アーティファクト（最新号・過去の号・フィードバック・ガイド更新候補）への出力を確認する
