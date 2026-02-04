---
name: git-pr-setup
description: Git準備（ブランチ作成、空コミット、PR作成）を自動化。「ブランチ作成」「PR準備」「Git準備」「開発開始」などで発動。Redmineチケット情報を元にブランチ・コミット・PR・Redmineコメントを一括作成。
allowed-tools: Bash, Read, TodoWrite, AskUserQuestion
user-invocable: true
---

# Git PR準備スキル

Redmineチケットを元に、ブランチ作成からPR作成までの一連のGitワークフローを自動実行する。

日本語で回答すること。

## 役割

Git準備の自動化エキスパートとして、以下を一括実行：
1. ブランチ作成
2. 空コミット作成
3. リモートへプッシュ
4. ドラフトPR作成
5. Redmineへのコメント追加（任意）

## 重要：このスキルの使い方

**各フェーズを順番に実行すること。フェーズを飛ばしてはならない。**

**制約事項：**
- このスキルはPythonスクリプトのみを使用する（MCPツールは使用しない）
- Redmineコメント追加には設定ファイルが必要（[SETUP.md](SETUP.md) 参照）
- 設定ファイルがない場合、Redmineコメントはスキップされる

---

## Phase 0: Todo登録

**TodoWriteツールで以下を登録：**

```json
[
  {"content": "Phase 1: 情報収集", "activeForm": "情報を収集中", "status": "pending"},
  {"content": "Phase 2: Git操作実行", "activeForm": "Git操作を実行中", "status": "pending"},
  {"content": "Phase 3: 完了報告", "activeForm": "完了報告を作成中", "status": "pending"}
]
```

各フェーズ開始時に`in_progress`、完了時に`completed`に更新する。

---

## Phase 1: 情報収集

### 1-1. 必要情報の一括収集（前半）

**AskUserQuestion ツール**で以下を一括収集：

```json
{
  "questions": [
    {
      "question": "RedmineチケットURLを「その他」から入力してください",
      "header": "チケットURL",
      "options": [
        {"label": "URLを入力する", "description": "「その他」を選択してURLを入力"}
      ],
      "multiSelect": false
    },
    {
      "question": "ブランチ名のprefixを選択または入力してください",
      "header": "ブランチprefix",
      "options": [
        {"label": "continuous_capture", "description": "連続撮影関連"},
        {"label": "feature", "description": "新機能"},
        {"label": "fix", "description": "バグ修正"},
        {"label": "hotfix", "description": "緊急修正"}
      ],
      "multiSelect": false
    },
    {
      "question": "コミットメッセージのprefixを選択または入力してください",
      "header": "コミットprefix",
      "options": [
        {"label": "撮影対応", "description": "撮影機能関連"},
        {"label": "機能追加", "description": "新機能追加"},
        {"label": "バグ修正", "description": "不具合修正"},
        {"label": "リファクタリング", "description": "コード改善"}
      ],
      "multiSelect": false
    },
    {
      "question": "実装内容を英語スネークケースで「その他」から入力してください（4-6単語程度）",
      "header": "実装説明",
      "options": [
        {"label": "入力例を見る", "description": "fix_close_button_position, add_payment_feature など"}
      ],
      "multiSelect": false
    }
  ]
}
```

### 1-2. 必要情報の一括収集（後半）

**AskUserQuestion ツール**で残りを収集：

```json
{
  "questions": [
    {
      "question": "PRテンプレートのパスを選択または入力してください",
      "header": "PRテンプレート",
      "options": [
        {"label": ".github/pull_request_template.md", "description": "標準テンプレート"},
        {"label": "テンプレートなし", "description": "テンプレートを使用しない"}
      ],
      "multiSelect": false
    },
    {
      "question": "PRのマージ先ブランチを選択または入力してください",
      "header": "マージ先",
      "options": [
        {"label": "main", "description": "メインブランチ"},
        {"label": "develop", "description": "開発ブランチ"},
        {"label": "feature_camera", "description": "カメラ機能ブランチ"}
      ],
      "multiSelect": false
    }
  ]
}
```

### 1-3. チケット情報の抽出

- RedmineチケットURLからチケット番号を抽出（例: `/issues/12345` → `12345`）
- Redmine APIでチケットタイトルを取得（設定済みの場合）

**成功確認**: すべての情報が揃った → Phase 2へ

---

## Phase 2: Git操作実行

**スクリプトベースディレクトリ**: `~/.claude/skills/git-pr-setup/scripts/`

### 2-1. ブランチ作成

```bash
python3 ~/.claude/skills/git-pr-setup/scripts/create_branch.py \
  "<prefix>" "<ticket_number>" "<implementation_description>"
```

**出力例**: `{"branch_name": "continuous_capture/12345/fix_close_button_position", "success": true}`

### 2-2. 空コミット作成

```bash
python3 ~/.claude/skills/git-pr-setup/scripts/create_empty_commit.py \
  "<commit_prefix>" "<ticket_title>" "<ticket_number>"
```

**出力例**: `{"commit_message": "撮影対応／閉じるボタンの位置を修正 refs #12345", "success": true}`

### 2-3. ブランチプッシュ

```bash
python3 ~/.claude/skills/git-pr-setup/scripts/push_branch.py "<branch_name>"
```

### 2-4. PR作成

```bash
python3 ~/.claude/skills/git-pr-setup/scripts/create_pr.py \
  "<template_path>" "<merge_target>" "<ticket_url>" "<pr_title>"
```

**出力例**: `{"pr_url": "https://github.com/owner/repo/pull/123", "success": true}`

### 2-5. Redmineコメント追加

```bash
python3 ~/.claude/skills/git-pr-setup/scripts/add_redmine_comment.py \
  "<ticket_number>" "<pr_url>"
```

**注意**: 設定ファイルがない場合はスキップされる（エラーにならない）

**成功確認**: すべてのスクリプトが成功（またはRedmineスキップ） → Phase 3へ

---

## Phase 3: 完了報告

### 3-1. 結果をまとめて報告

```markdown
## Git準備完了

### 作成内容
- **ブランチ名**: {branch_name}
- **コミットメッセージ**: {commit_message}
- **PR URL**: {pr_url}
- **Redmineコメント**: 追加済み / スキップ

### 次のステップ
実装を開始できます。
```

**成功確認**: 報告完了 → 終了

---

## 詳細リファレンス

- **セットアップ**: [SETUP.md](SETUP.md)

## エラー対応

| エラー | 対応 |
|-------|------|
| ブランチが既に存在する | 別の名前を指定するか、既存ブランチを削除 |
| リモートへのプッシュ失敗 | ネットワーク接続を確認、認証情報を確認 |
| gh コマンドが見つからない | `brew install gh` でインストール |
| gh 認証エラー | `gh auth login` で再認証 |
| Redmine設定ファイルなし | [SETUP.md](SETUP.md) を参照して設定（スキップ可） |

**エラーフィードバックループ**:
1. エラーメッセージを確認
2. 上記の表に従って対応
3. 該当ステップを再実行
4. 成功するまで繰り返す

## 出力形式

各スクリプトはJSON形式で結果を出力：

```json
{"success": true, "key": "value"}
```

エラー時：

```json
{"success": false, "error": "エラーメッセージ"}
```

## 注意事項

- 情報収集は2回のAskUserQuestionで完結させる（前半4問、後半2問）
- エラー発生時は該当ステップで停止し、ユーザーに報告
- Redmineコメント機能はオプション（設定なしでも動作する）
