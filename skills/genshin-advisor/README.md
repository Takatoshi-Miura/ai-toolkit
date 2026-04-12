# genshin-advisor スキル

Claude Code 向けの原神アドバイザースキルです。

## インストール

このディレクトリを Claude Code のスキルディレクトリに配置してください：

```
~/.claude/skills/genshin-advisor/
```

または、プロジェクトのスキルディレクトリ：

```
.claude/skills/genshin-advisor/
```

## ディレクトリ構成

```
genshin-advisor/
├── SKILL.md                      # スキル定義（Claude が読む）
├── README.md                     # このファイル
├── scripts/
│   └── fetch.py                  # データ取得スクリプト（Python標準ライブラリのみ）
└── references/
    ├── analysis-guide.md         # 分析・アドバイスの指針
    └── cookie-guide.md           # HoYoLAB Cookie 取得方法
```

## 必要環境

- Python 3.8 以上（標準ライブラリのみ使用、追加インストール不要）
- インターネット接続（Enka.Network API へのアクセス）

## 使い方

Claude Code で以下のように話しかけるだけ：

```
/genshin build 861748604
/genshin party 861748604
/genshin status 861748604
```

または自然言語でも動きます：

```
原神のUID 861748604 の聖遺物スコアを見せて
雷電将軍のビルドを評価して
```

## キャッシュ

初回実行時、カレントディレクトリに `.genshin_cache/` を作成してキャラ名変換データをキャッシュします。2回目以降の起動が高速になります。

## 注意

- 非公式APIのため、変更・停止の可能性があります
- プロフィールをゲーム内で「公開」設定にする必要があります
