# genshin-advisor（原神アドバイザースキル）

## 1. 概要

- **何をするスキルか**: 原神（Genshin Impact）のユーザーアカウントデータを公式HoYoLAB APIで取得し、ビルド・聖遺物・パーティ編成・深境螺旋・リアルタイム情報について日本語で分析・アドバイスする。データ取得は毎回APIから最新化し、提案前にサブエージェントによるレビュー（最大3回）を経てから回答する。
- **発動条件**:
  - 自動発動キーワード: 「原神」「genshin」「UID」「ビルド評価」「聖遺物スコア」「パーティ編成」「深境螺旋」等
  - スラッシュ呼び出し: `/genshin-advisor` で可能
  - 自動発動: あり（`/genshin build|party|abyss|status|help` や「雷電将軍のビルドを評価して」等の自然言語でも発動）
- **依存の有無**: Python 3.8以上（標準ライブラリのみ）、HoYoLAB公式APIへのネットワークアクセス、Agentツール（レビュー用サブエージェント）、WebSearch/WebFetch（最新環境情報の確認）
- **想定する利用シーン**: 原神の聖遺物・キャラビルドの評価を受けたい時、パーティ編成の提案が欲しい時、樹脂・派遣などのリアルタイム状況を確認したい時

## 2. 事前準備（セットアップ）

- `references/.genshin_config` に UID・`ltoken_v2`・`ltuid_v2` を設定しておくと、コマンド実行時に自動読み込みされる（未設定でも引数で都度指定可能）
- Cookie（`ltoken_v2` / `ltuid_v2`）の取得方法は `references/cookie-guide.md` を参照
- 原神アプリ内でプロフィールを「公開」設定にしておく必要がある

## 3. 使い方

- **呼び出し方法**: `/genshin build|party|abyss|status|help` での明示呼び出し、または「雷電将軍のビルドを評価して」のような自然言語での依頼
- **入力例**: `/genshin build 861748604`
- **出力例**: チャット上での回答に加え、`output/report_YYYYMMDD_HHMM.md` に分析レポートを保存
- **手順**:
  1. UID・Cookieの確認（`references/.genshin_config` から自動読込、なければ案内）
  2. `scripts/fetch.py` でHoYoLAB APIから最新データを取得し `data/latest.json` に上書き保存
  3. `references/analysis-guide.md` と `references/feedback.md`（過去のユーザー評価・好み）をもとに分析草案を作成。主力候補キャラについてはWebSearchで最新ビルド・環境ティアリストを確認し、固定基準との差異を反映
  4. Agentツールで独立したサブエージェントに草案をレビューさせる。サブエージェントもWebSearchで最新環境情報との矛盾を確認し、指摘があれば修正・再レビュー（最大3回）
  5. 確定内容を `output/report_YYYYMMDD_HHMM.md` に保存しつつユーザーへ回答
  6. ユーザーからの評価・好みの反応があれば、確認を取ってから `references/feedback.md` に追記
- **使う際のテクニック・コツ**: キャラクター・聖遺物データは公式HoYoLAB API（`allchars`）のみを使用し、Enka Network等の非公式APIは使わない方針。Web検索（WebSearch/WebFetch）はキャラ・聖遺物データそのものの取得には使わず、最新の環境ティアリスト・ビルド傾向など分析基準の補完のみに使用する

## 4. 保守・拡張ガイド

### ファイル構成

| ファイル/ディレクトリ | 役割 |
|---|---|
| SKILL.md | スキル定義（全体フロー） |
| WORKFLOW-ADVISE.md | データ取得〜サブエージェントレビュー〜レポート出力〜フィードバック記録の詳細手順 |
| references/commands.md | コマンド一覧 |
| references/analysis-guide.md | 聖遺物・パーティ編成の分析観点 |
| references/cookie-guide.md | HoYoLAB Cookie取得方法 |
| references/feedback.md | ユーザーフィードバック（評価コメント・プレイスタイルの好み）の蓄積先 |
| references/.genshin_config | UID・Cookieの設定ファイル |
| data/latest.json | `allchars`/`status`の最新取得結果（実行のたびに上書き） |
| data/.genshin_cache/ | 中国語→日本語 翻訳テーブルのキャッシュ（`translate.py`が自動生成） |
| output/ | 分析レポートの保存先（実行日時ごとに1ファイル） |
| scripts/fetch.py | HoYoLAB公式APIからのデータ取得スクリプト |
| scripts/translate.py | キャラ名・武器名・聖遺物セット名の中国語→日本語変換モジュール |

### 修正時の手順と注意点

- `description` を変更すると自動発動の挙動が変わるため、変更時はトリガーキーワードが自然に含まれているか確認する
- 分析観点・評価基準を変えたい場合は `references/analysis-guide.md` を編集する（SKILL.md本体は変更不要）
- サブエージェントレビューの観点を追加したい場合は `WORKFLOW-ADVISE.md` のステップ4を編集する

### 依存

- ツール: `Bash`, `Read`, `Write`, `Agent`, `WebSearch`, `WebFetch`
- 外部: HoYoLAB公式API（`bbs-api-os.hoyoverse.com`）、EnkaNetwork API-docs（翻訳テーブル生成元、`data/.genshin_cache/`に初回キャッシュ）

### 動作確認・テスト方法

```bash
cd ~/.claude/skills/genshin-advisor
python3 scripts/fetch.py all
```

正常時は `data/latest.json` に `allchars`/`status` キーで結果が保存され、`data/.genshin_cache/` に翻訳テーブルが生成される。`status`のみ必要な場合は `python3 scripts/fetch.py status` のように個別実行も可能。
