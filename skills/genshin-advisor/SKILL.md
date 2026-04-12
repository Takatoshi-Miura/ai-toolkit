---
name: genshin-advisor
description: 原神（Genshin Impact）のゲームデータをAPIで取得してClaudeが分析・アドバイスするスキル

# 原神アドバイザースキル（Claude Code版）

ユーザーの原神アカウントデータを**公式HoYoLAB API**で取得し、ビルド・聖遺物・パーティ編成・深境螺旋・リアルタイム情報などについて日本語でアドバイスを提供する。

**このスキルはClaude Code環境専用**。外部APIへのネットワークアクセスが必要なため、スクリプトを実行して取得する。

キャラクター情報・聖遺物情報は**必ず公式HoYoLAB APIのみ使用**する（Enka Network等の非公式APIは使用しない）。

---

## コマンド一覧

| コマンド | 説明 |
|---|---|
| `/genshin build [UID]` | 全所持キャラの聖遺物スコア一覧＋ビルド評価・改善アドバイス |
| `/genshin party [UID]` | 全所持キャラからパーティ編成を提案 |
| `/genshin abyss [UID]` | 全所持キャラから深境螺旋向けの編成を提案 |
| `/genshin status [UID]` | 樹脂・派遣などリアルタイムステータス（要Cookie） |
| `/genshin help` | コマンド一覧を表示 |

UIDが省略された場合は、会話履歴から取得するか、ユーザーに聞く。

---

## ステップ1: UIDとCookieの確認

UID（9桁の数字）と HoYoLAB Cookie（`ltoken_v2` / `ltuid_v2`）が必要。

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

## ステップ2: スクリプトでデータ取得

このスキルディレクトリにある `scripts/fetch.py` を使ってデータを取得する。

### build / party / abyss コマンド（公式API・全キャラ取得）

キャラクター情報・聖遺物情報は必ず `allchars` コマンドを使用する：

```bash
python3 scripts/fetch.py allchars <UID> --ltoken <ltoken_v2> --ltuid <ltuid_v2>
```

`allchars` は HoYoLAB 公式APIで全所持キャラクター（武器・聖遺物・スキルレベル含む）を取得する。

### status コマンド（リアルタイム情報）

```bash
python3 scripts/fetch.py status <UID> --ltoken <ltoken_v2> --ltuid <ltuid_v2>
```

### スクリプトの出力

`fetch.py` はJSON形式で結果を標準出力に返す。Claudeはこれを受け取って分析・アドバイスを生成する。

---

## ステップ3: 分析とアドバイス生成

スクリプトの出力JSONをもとに以下の観点で分析する。詳細は `references/analysis-guide.md` を参照。

### 聖遺物スコア計算式

サブオプションのみを対象に計算：

| サブオプション | 係数 |
|---|---|
| 会心率 | × 2.0 |
| 会心ダメージ | × 1.0 |
| 攻撃力% | × 1.0 |
| 元素熟知 | ÷ 4.0 |
| 元素チャージ効率 | × 0.65 |
| HP% | × 0.5 |
| 防御% | × 0.4 |

評価基準: **SS**≥220 / **S**≥180 / **A**≥140 / **B**≥100 / **C**≥60 / **D**<60

### 出力フォーマット

```
## [キャラ名] のビルド評価

**スコア**: XX.X点（評価: S）

**聖遺物5枚合計**
| 部位 | スコア | メイン | 注目サブ |
|---|---|---|---|
| 花 | XX.X | HP | 会心率X%, 会心ダメX% |
...

**✅ 良い点**
- ...

**⚠️ 改善点**
- ...

**💡 おすすめの方向性**
- ...
```

---

## 注意事項

1. 回答は常に**日本語**で行う
2. キャラクター・聖遺物データは**公式HoYoLAB API（allchars）のみ**使用する
3. Enka Network等の非公式APIは使用しない
4. Cookieはセッション内でのみ使用し、ファイルに保存しない
5. スクリプトが初回実行時にキャラ名変換データをローカルキャッシュする（`.genshin_cache/` ディレクトリ）
