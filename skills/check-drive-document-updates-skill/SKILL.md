---
name: check-drive-document-updates-skill
description: Google Driveのファイル変更有無を日付指定で確認する。ファイルの更新確認、変更チェック、ドライブファイル監視などの依頼時に使用。「ファイル更新確認」「変更あったか」「ドライブ確認」「更新チェック」「テンプレート更新」「ドキュメント変更」などのキーワードで発動。
allowed-tools: Bash, Read, TodoWrite, AskUserQuestion
user-invocable: true
disable-model-invocation: false
---

# Google Driveファイル更新確認スキル

指定日以降にGoogle Driveのファイルが更新されたかを確認し、結果を分かりやすく報告する。

## 役割

ファイル更新確認のアシスタントとして、監視対象ファイルの変更有無を確認し、結果を表形式で報告する。

## 重要：このスキルの使い方

**各フェーズを順番に実行すること。フェーズを飛ばしてはならない。**

**制約事項：**
- このスキルはPythonスクリプトのみを使用する（MCPツールは使用しない）
- 認証エラーが発生した場合は、[SETUP.md](SETUP.md) のセットアップワークフローを実行する
- 監視対象ファイルは [TARGET_FILES.md](TARGET_FILES.md) で管理する

---

## Phase 0: Todo登録

**TodoWriteツールで以下を登録：**

```json
[
  {"content": "Phase 1: 日付情報の取得", "activeForm": "日付情報を取得中", "status": "pending"},
  {"content": "Phase 2: ファイルの変更確認", "activeForm": "ファイルの変更を確認中", "status": "pending"},
  {"content": "Phase 3: 結果の集約と表示", "activeForm": "結果を集約中", "status": "pending"}
]
```

各フェーズ開始時に`in_progress`、完了時に`completed`に更新する。

---

## Phase 1: 日付情報の取得

### 1-1. 確認基準日の入力

**AskUserQuestionツールを使用して、基準日を入力してもらう：**

```json
{
  "questions": [
    {
      "question": "確認基準日を選択または「その他」から入力してください（YYYY-MM-DD形式）",
      "header": "基準日",
      "options": [
        {"label": "1週間前", "description": "1週間前の日付を基準にする"},
        {"label": "1ヶ月前", "description": "1ヶ月前の日付を基準にする"},
        {"label": "3ヶ月前", "description": "3ヶ月前の日付を基準にする"}
      ],
      "multiSelect": false
    }
  ]
}
```

### 1-2. 日付の決定

- 選択肢が選ばれた場合：現在日付から計算して基準日を決定
- 「その他」で入力された場合：入力された日付をそのまま使用

**成功確認**: 基準日が決定した → Phase 2へ

---

## Phase 2: ファイルの変更確認

### 2-1. 更新確認スクリプトの実行

```bash
python3 ~/.claude/skills/check-drive-document-updates-skill/scripts/check_file_modified.py <YYYY-MM-DD>
```

※ `<YYYY-MM-DD>` にはPhase 1で決定した基準日を入れる

### 2-2. 結果の取得

スクリプトはJSON形式で以下の情報を出力する：

```json
{
  "sinceDate": "2025-01-01",
  "totalFiles": 4,
  "modifiedCount": 1,
  "results": [
    {
      "url": "...",
      "fileId": "...",
      "name": "ファイル名",
      "modified": true,
      "modifiedTime": "2025-01-15 14:30",
      "lastModifyingUser": "user@example.com",
      "error": null
    }
  ]
}
```

**成功確認**: JSON結果が取得できた → Phase 3へ

---

## Phase 3: 結果の集約と表示

### 3-1. 結果を以下の形式で出力

```markdown
## 確認結果

**確認基準日**: YYYY-MM-DD

| ファイル名 | 変更有無 | 最終更新日時 | 最終更新者 |
|-----------|---------|-------------|-----------|
| (ファイル名) | ○/× | YYYY-MM-DD HH:MM | 更新者メール |
| ... | ... | ... | ... |

### 凡例
- ○: 指定日以降に更新あり
- ×: 指定日以降に更新なし
```

### 3-2. サマリーの表示

```markdown
### サマリー
N件中M件に変更がありました。
```

- 変更があったファイルがある場合は、内容確認を推奨するメッセージを表示

**成功確認**: 結果が表形式で出力された → 完了

---

## 詳細リファレンス

- **セットアップ・トラブルシューティング**: [SETUP.md](SETUP.md)
- **監視対象ファイル**: [TARGET_FILES.md](TARGET_FILES.md)

## 使用スクリプト

| 操作 | スクリプト |
|------|-----------|
| 更新確認 | `~/.claude/skills/check-drive-document-updates-skill/scripts/check_file_modified.py` |

## エラー対応

| エラー | 対応 |
|-------|------|
| 認証エラー / トークンエラー | [SETUP.md](SETUP.md) のセットアップワークフローを実行 |
| ModuleNotFoundError | `pip install google-auth google-auth-oauthlib google-api-python-client` を実行 |
| TARGET_FILES.mdが見つからない | スキルディレクトリにTARGET_FILES.mdを作成 |
| URLからファイルIDを抽出できない | URLの形式を確認（`/d/xxxxxxx/` を含む形式であること） |

**エラーフィードバックループ**:
1. エラーメッセージを確認
2. 上記の表に従って対応
3. 該当フェーズを再実行
4. 成功するまで繰り返す

## 備考

- ツールから最終更新者情報が取得できない場合は「-」と表示する
- エラーが発生した場合は、エラー内容をユーザーに報告し、対処方法を案内する
