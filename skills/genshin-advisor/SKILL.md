---
name: genshin-advisor
description: 原神（Genshin Impact）のUID・ビルド・聖遺物スコア・パーティ編成・深境螺旋・リアルタイムステータスなどのゲームデータをHoYoLAB APIで取得し、Claudeが分析・アドバイスするスキル
allowed-tools: Bash, Read, Write, Agent, WebSearch, WebFetch
user-invocable: true
---

# 原神アドバイザースキル

ユーザーの原神アカウントデータを**公式HoYoLAB API**で取得し、ビルド・聖遺物・パーティ編成・深境螺旋・リアルタイム情報などについて**常に日本語**でアドバイスを提供する。

キャラクター情報・聖遺物情報は**必ず公式HoYoLAB APIのみ使用**する（Enka Network等の非公式APIは使用しない）。

---

## コマンド一覧

`/genshin build|party|abyss|status|help [UID]` に対応する。詳細は `references/commands.md` を参照。

---

## ステップ1: UIDとCookieの確認

UID（9桁の数字）と HoYoLAB Cookie（`ltoken_v2` / `ltuid_v2`）が必要。

**設定ファイル自動参照**: `references/.genshin_config` が存在する場合、UID・Cookie は自動で読み込まれる（このディレクトリは非公開のプライベート環境のため実値保存で問題ない）。引数省略可。

**Cookieがない場合**: 取得方法をユーザーに案内する（→ `references/cookie-guide.md` を参照）。

先頭数字でサーバーを判定：

| 先頭 | サーバーID |
|---|---|
| 1〜4 | `cn_gf01` |
| 5 | `cn_qd01` |
| 6 | `os_usa` |
| 7 | `os_euro` |
| 8 | `os_asia` |
| 9 | `os_cht` |

---

## ステップ2: データ取得（毎回最新化）

`fetch.py all` で全所持キャラ・聖遺物データとリアルタイムステータスを1回の呼び出しでまとめて取得する。キャッシュは使い回さず毎回APIから取得し、`data/latest.json` に上書き保存する。

```bash
python3 scripts/fetch.py all
```

`references/.genshin_config` からUID・Cookieを自動読み込みする（引数で明示上書きも可能）。`allchars`・`status`が個別に必要な場合はそれぞれ単体コマンドとしても実行できる。

あわせて `references/feedback.md` を読み、過去の評価傾向・プレイスタイルの好みを把握しておく（ステップ3の分析・レポート作成に活かす）。

初回実行時は `scripts/translate.py` がキャラ名変換データを `data/.genshin_cache/` にローカルキャッシュする。

---

## ステップ3: 分析・アドバイス草案作成

`data/latest.json` と `references/analysis-guide.md`・`references/feedback.md` をもとに草案を作る。詳細は `WORKFLOW-ADVISE.md` を参照。

---

## ステップ4: サブエージェントレビュー

Agentツールで独立したサブエージェントに草案をレビューさせ、指摘があれば修正して再レビュー（最大3回）。レビュー観点は `WORKFLOW-ADVISE.md` を参照。

---

## ステップ5: レポート出力

確定内容を `output/report_YYYYMMDD_HHMM.md` に保存しつつユーザーに回答する。

---

## ステップ6: フィードバック記録

ユーザーの評価・好みの反応があれば、確認を取ってから `references/feedback.md` に追記する。フォーマットは `WORKFLOW-ADVISE.md` を参照。
