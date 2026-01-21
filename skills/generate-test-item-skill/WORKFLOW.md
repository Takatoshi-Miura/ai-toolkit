# テスト項目書作成 - 詳細ワークフロー

このドキュメントはSKILL.mdの各フェーズをより詳細に説明します。

## 前提条件

- 認証ファイル（`~/.config/google-drive-skills/`）が配置済み

---

## Phase 1: 情報収集（詳細）

### Step 1-1: テストガイドラインの読取

テストガイドライン（Google Docs）を読み取り、テストタイプごとの観点を把握する。

```bash
python3 ~/.claude/skills/generate-test-item-skill/scripts/read_drive_file.py 1fpcWeiNCIefrUXN9567iopHxPGpB4VUKQ5uxr9CznVo docs
```

**把握すべき内容：**
- 「■単体テスト」の目的・スコープ・観点
- 「■プレ結合テスト」の目的・スコープ・観点
- それぞれの違い

### Step 1-2: 必要情報の収集

ユーザーから以下の情報を収集：

#### 必須情報

| 項目 | 説明 | 例 |
|------|------|-----|
| テスト項目書URL | Googleスプレッドシートのリンク | `https://docs.google.com/spreadsheets/d/xxx/edit` |
| テストタイプ | 「単体テスト」または「プレ結合テスト」 | 単体テスト |

#### 任意情報

| 項目 | 説明 | 例 |
|------|------|-----|
| PBI/Issue URL | 対象チケットのリンク | GitHub Issue、Redmine URL |
| 概要設計書URL | 概要設計書のリンク | Google Docs URL |
| その他注意事項 | テスト作成時の注意点 | 「○○機能は除外」等 |

**質問例：**

> テスト項目書を作成するために、以下の情報を教えてください：
>
> 1. テスト項目書のスプレッドシートURL（必須）
> 2. テストタイプ（必須）：「単体テスト」または「プレ結合テスト」
> 3. PBI/IssueのURL（あれば）
> 4. 概要設計書のURL（あれば）
> 5. その他、テスト作成時の注意事項（あれば）

---

## Phase 2: スプレッドシート準備（詳細）

### Step 2-1: スプレッドシートIDの抽出

URLパターンから `{spreadsheet_id}` を抽出：

```
https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit#gid=0
```

### Step 2-2: シート構造の読取（許可不要）

```bash
python3 ~/.claude/skills/generate-test-item-skill/scripts/read_drive_file.py <spreadsheet_id> sheets
```

**確認ポイント：**
- 「因子・水準」シートの存在
- 「原本」シートの存在
- 既存シートの一覧

### Step 2-3: 「原本」シートの存在確認

シート一覧に「原本」シートが存在するか確認する。

**「原本」シートが存在しない場合：**

> ⚠️ テスト項目書に「原本」シートが見つかりません。
>
> 「原本」シートはテスト項目のテンプレートとして使用します。
> 以下の手順で追加してください：
>
> 1. スプレッドシートを開く
> 2. 新しいシートを作成し、名前を「原本」に設定
> 3. テスト項目の列構成を設定（下記参照）
> 4. 追加が完了したらお知らせください
>
> **推奨する列構成：**
>
> | 列 | 内容 |
> |----|------|
> | A | № |
> | B〜F | 因子水準（因子の数に応じて調整） |
> | G | 前提条件 |
> | H | 操作手順 |
> | I | 期待結果 |
> | J | 結果 |
> | K | 備考 |
>
> 追加完了後、続きの処理を実行します。

**ユーザーから追加完了の報告を受けたら**、Step 2-2 に戻って再度シート構造を読み取り、「原本」シートの存在を確認してから続行する。

### Step 2-4: 因子水準シートの読取

```bash
python3 ~/.claude/skills/generate-test-item-skill/scripts/read_drive_file.py <spreadsheet_id> sheets '因子・水準'
```

**取得する情報：**
- 因子水準表の数
- 各表のタイトル（シート名として使用）
- 各因子の名前と水準

### Step 2-5: 原本シートの列構成把握

```bash
python3 ~/.claude/skills/generate-test-item-skill/scripts/read_drive_file.py <spreadsheet_id> sheets '原本'
```

**把握する列構成（例）：**

| 列 | 内容 |
|----|------|
| A | № |
| B〜F | 因子水準 |
| G | 前提条件 |
| H | 操作手順 |
| I | 期待結果 |
| J | 結果 |
| K | 備考 |

**注意**: 原本シートのIDを確認しておくこと（Phase 5でサブエージェントに渡す）。

---

## Phase 3: 仕様確認（詳細）

### Step 3-1: PBI/Issueの読取

**GitHub Issueの場合：**

mcp-gh-issue-mini MCPツールを使用（例外的にMCP許可）。

**Redmine Issueの場合：**

read-redmine-skill が自動発動される。

### Step 3-2: 概要設計書の読取

```bash
# Google Docs IDを抽出
# https://docs.google.com/document/d/{doc_id}/edit

python3 ~/.claude/skills/generate-test-item-skill/scripts/read_drive_file.py <doc_id> docs
```

**ファイルが大きい場合：**

```bash
# タブIDを指定して部分読取
python3 ~/.claude/skills/generate-test-item-skill/scripts/read_drive_file.py <doc_id> docs --tab-id <tabId>
```

### Step 3-3: 不明点の整理と質問

読み取った情報を基に、以下の観点で不明点を整理：

- **操作手順**: 具体的なユーザー操作が不明確な箇所
- **期待結果**: 検証すべき動作が不明確な箇所
- **前提条件**: テスト実行に必要な事前条件が不明確な箇所
- **境界条件**: 値の範囲や上限/下限が不明確な箇所

**質問のフォーマット例：**

> 以下の点について確認させてください：
>
> 1. [操作手順] ○○画面で△△を行う際の具体的な手順は？
> 2. [期待結果] □□機能の正常動作とは具体的にどのような状態ですか？
> 3. [前提条件] このテストを実行するために必要なデータや設定はありますか？

---

## Phase 4: 計画立案・承認（詳細）

### Step 4-1: Planサブエージェントの起動

Taskツールで Plan サブエージェントを起動：

```
subagent_type: Plan
prompt: |
  テスト項目書の作成計画を立案してください。

  ## 入力情報
  - テストタイプ: <単体テスト/プレ結合テスト>
  - テストガイドラインの観点: <Phase 1で把握した観点>
  - 因子・水準シートの構成: <Phase 2で把握した構成>
  - 仕様情報: <Phase 3で把握した仕様>
  - 質疑応答の内容: <Phase 3でのユーザー回答>

  ## 出力してほしい内容
  1. 各シートで作成するテスト項目の方針
  2. 重点的にテストすべき観点
  3. 注意すべき境界条件やエッジケース
  4. テスト作成の優先順位（あれば）
```

### Step 4-2: 計画の承認依頼

サブエージェントから返された計画案をユーザーに提示：

> テスト作成計画が作成されました。以下の内容で進めてよろしいですか？
>
> [計画内容]
>
> 修正が必要な場合はお知らせください。

---

## Phase 5: テスト項目生成（詳細）

### Step 5-1: 組み合わせパターンの生成

専用スクリプトで因子水準の組み合わせを生成：

```bash
python3 ~/.claude/skills/generate-test-item-skill/scripts/generate_combinations.py '<factors_json>'
```

**factors_json の形式：**

```json
{
  "factors": [
    {"name": "因子A", "levels": ["A1", "A2", "A3"]},
    {"name": "因子B", "levels": ["B1", "B2"]},
    {"name": "ワンパス", "levels": ["D1", "D2", "D3"]},
    {"name": "期待値", "levels": ["E1", "E2"]}
  ]
}
```

**出力例：**

```json
{
  "success": true,
  "combinations": [
    ["A1", "B1"],
    ["A1", "B2"],
    ["A2", "B1"],
    ["A2", "B2"],
    ["A3", "B1"],
    ["A3", "B2"]
  ],
  "onepassCases": [
    {"factor": "ワンパス", "level": "D1"},
    {"factor": "ワンパス", "level": "D2"},
    {"factor": "ワンパス", "level": "D3"}
  ],
  "totalCount": 9
}
```

### Step 5-2: サブエージェントの並列起動

因子水準表の数だけ test-item-writer サブエージェントを並列起動。
各サブエージェントが「原本」シートを複製し、テスト項目を記載する。

```
# シート1用
Task(
  subagent_type: "test-item-writer",
  prompt: |
    以下のパラメータでテスト項目書を作成してください：

    - spreadsheet_id: <スプレッドシートID>
    - source_sheet_id: <原本シートのID>
    - sheet_name: <因子水準表のタイトル（複製後のシート名）>
    - factors_data: <該当する因子・水準データ（JSON）>
    - test_requirements: <テスト仕様・要求事項>
    - test_type: <単体テスト/プレ結合テスト>
    - test_guidelines: <テストガイドラインの観点>

    注意事項:
    - 最初に原本シートを複製してシート名を設定すること
    - A列の№は追加不要（既存の番号を使用）
    - 因子水準の組み合わせ順序は定義順を厳守
)

# シート2用
Task(
  subagent_type: "test-item-writer",
  ...
)

# 以降、シートの数だけ並列起動
```

### Step 5-3: サブエージェント完了待機

すべてのサブエージェントのタスク完了を待機。

---

## Phase 6: 完了確認（詳細）

### Step 6-1: 結果の集計

各サブエージェントからの報告を集計：

- 処理対象シート名
- 生成した因子数
- 生成した組み合わせ数
- 作成したテスト項目数
- 発生した警告やエラー

### Step 6-2: 完了報告

ユーザーに最終報告：

> テスト項目書の作成が完了しました。
>
> ## 結果サマリ
> - 処理対象シート数: X シート
> - 生成したテスト項目の総数: Y 件
>
> ## シート別詳細
> | シート名 | 因子数 | 組み合わせ数 | テスト項目数 |
> |---------|--------|-------------|-------------|
> | シート1 | 3 | 12 | 12 |
> | シート2 | 4 | 24 | 24 |
> | ... | ... | ... | ... |
>
> ## 警告・エラー
> - （あれば記載）

---

## トラブルシューティング

### 認証エラーが発生した場合

```
Error: Token has been expired or revoked
```

→ [SETUP.md](SETUP.md) のセットアップワークフローを実行

### シート名が見つからない場合

```json
{
  "success": false,
  "error": "Sheet not found",
  "availableSheets": ["シート1", "シート2", "因子・水準", "原本"]
}
```

→ `availableSheets` から正しいシート名を確認して再実行

### 組み合わせ数が300を超える場合

```json
{
  "success": true,
  "warning": "Combination count (456) exceeds limit (300). Truncated.",
  "totalCount": 300
}
```

→ 上限300件まで生成。必要に応じて因子の絞り込みを検討
