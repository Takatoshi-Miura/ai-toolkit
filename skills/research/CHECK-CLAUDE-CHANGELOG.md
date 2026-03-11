# Claude Code Changelog確認ワークフロー

Claude Codeのchangelogを取得し、前回確認日以降の新着情報を日本語で解説する。

日本語で回答すること。

## 状態ファイル

| 項目 | 値 |
|-----|-----|
| パス | `~/.claude/changelog-last-checked.txt` |
| 形式 | `YYYY-MM-DD`（1行のみ） |
| 用途 | 前回確認日の記録・更新 |

## TodoWrite チェックリスト

```json
[
  {"content": "Phase 1: 前回確認日の読み込み", "activeForm": "前回確認日を読み込み中", "status": "pending"},
  {"content": "Phase 2: Changelogページの取得", "activeForm": "Changelogページを取得中", "status": "pending"},
  {"content": "Phase 3: 新着情報の抽出と解説", "activeForm": "新着情報を抽出・解説中", "status": "pending"},
  {"content": "Phase 4: 確認日の更新", "activeForm": "確認日を更新中", "status": "pending"}
]
```

---

## Phase 1: 前回確認日の読み込み

**Phase 1開始時**: TodoWriteで「Phase 1」を `in_progress` に更新

### 1-1. 状態ファイルの確認

Bashツールで状態ファイルを読み込む：

```bash
cat ~/.claude/changelog-last-checked.txt 2>/dev/null
```

### 1-2. 前回確認日の決定

- ファイルが存在し `YYYY-MM-DD` 形式の日付が書かれていた場合 → その日付を「前回確認日」とする
- ファイルが存在しない、または空の場合 → 「初回実行」として全件を対象にする

**成功確認**: 前回確認日または「初回」が決定した → Phase 2へ

**Phase 1完了時**: TodoWriteで「Phase 1」を `completed` に更新

---

## Phase 2: Changelogページの取得

**Phase 2開始時**: TodoWriteで「Phase 2」を `in_progress` に更新

### 2-1. WebFetchでChangelogページを取得

```
URL: https://code.claude.com/docs/ja/changelog
```

WebFetchツールを使ってページ全体のコンテンツを取得する。

**成功確認**: Changelogページのコンテンツが取得できた → Phase 3へ

**Phase 2完了時**: TodoWriteで「Phase 2」を `completed` に更新

---

## Phase 3: 新着情報の抽出と解説

**Phase 3開始時**: TodoWriteで「Phase 3」を `in_progress` に更新

### 3-1. 対象エントリの抽出

取得したChangelogの内容から日付情報を持つエントリを識別する。

- **前回確認日がある場合**: 前回確認日より後（その日付は含まない）のエントリのみを抽出
- **初回実行の場合**: 全エントリを抽出

### 3-2. 新着情報の解説

**新着情報がある場合:**

```
## Claude Code Changelog 新着情報

前回確認日: YYYY-MM-DD（または「初回確認」）
確認日時: YYYY-MM-DD

### YYYY-MM-DD
#### [エントリタイトル]
- 変更内容の要点1
- 変更内容の要点2

...（新しい日付順に列挙）

---
合計 N 件の新着エントリがありました。
```

**新着情報がない場合:**

```
## Claude Code Changelog 確認結果

前回確認日: YYYY-MM-DD
確認日時: YYYY-MM-DD

前回確認日以降の新着情報はありませんでした。
```

**成功確認**: 新着情報の抽出・解説が完了した → Phase 4へ

**Phase 3完了時**: TodoWriteで「Phase 3」を `completed` に更新

---

## Phase 4: 確認日の更新

**Phase 4開始時**: TodoWriteで「Phase 4」を `in_progress` に更新

### 4-1. 今日の日付を取得して状態ファイルを更新

```bash
echo "$(date +%Y-%m-%d)" > ~/.claude/changelog-last-checked.txt
```

### 4-2. 書き込み確認

```bash
cat ~/.claude/changelog-last-checked.txt
```

表示された日付が今日の日付と一致していることを確認する。

**成功確認**: 状態ファイルが今日の日付で更新された → 完了

**Phase 4完了時**: TodoWriteで「Phase 4」を `completed` に更新

---

## エラー対応

| エラー | 対応 |
|-------|------|
| `cat` でファイルが見つからない | 初回実行として全件を対象にする（エラーではない） |
| WebFetchでページが取得できない | 英語版 `https://code.claude.com/docs/changelog` も試みる |
| `echo >` で書き込みエラー | `ls ~/.claude/` で `~/.claude/` ディレクトリの存在を確認 |
| 日付フォーマットが不正 | `date +%Y-%m-%d` の出力を再確認 |

**エラーフィードバックループ:**
1. エラーメッセージを確認
2. 上記の表に従って対応
3. 該当フェーズを再実行
4. 成功するまで繰り返す
