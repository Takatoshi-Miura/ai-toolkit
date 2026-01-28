---
name: generate-test-item-skill
description: 因子水準組み合わせに基づくテスト項目書を作成する。
allowed-tools: Bash, Read, Task, TodoWrite
user-invocable: true
disable-model-invocation: true
---

# テスト項目書作成スキル

因子水準組み合わせに基づくテスト項目書を自動作成する。

## 役割

モバイルアプリのテスト作成のエキスパートとして、与えられた手順に従ってテスト項目書を作成する。

## 重要：このスキルの使い方

**各フェーズを順番に実行すること。フェーズを飛ばしてはならない。**

**制約事項：**
- このスキルはPythonスクリプトのみを使用する（MCPツールは使用しない）
- 認証エラーが発生した場合は、[SETUP.md](SETUP.md) のセットアップワークフローを実行する

---

## Phase 0: Todo登録

**TodoWriteツールで以下を登録：**

```json
[
  {"content": "Phase 1: 情報収集", "activeForm": "情報を収集中", "status": "pending"},
  {"content": "Phase 2: 資料一括読取", "activeForm": "資料一括読取", "status": "pending"},
  {"content": "Phase 3: 仕様確認", "activeForm": "仕様を確認中", "status": "pending"},
  {"content": "Phase 4: 計画立案・承認", "activeForm": "計画を立案中", "status": "pending"},
  {"content": "Phase 5-1: 組み合わせパターン生成", "activeForm": "組み合わせパターンを生成中", "status": "pending"},
  {"content": "Phase 5-2: テスト項目書き込み", "activeForm": "テスト項目を書き込み中", "status": "pending"},
  {"content": "Phase 6: 完了確認・クリーンアップ", "activeForm": "完了確認・クリーンアップ中", "status": "pending"}
]
```

---

## Phase 1: 情報収集

### 1-1. 必要情報の一括収集

**AskUserQuestion ツール**で以下を一括収集：

```json
{
  "questions": [
    {
      "question": "テスト項目書のGoogleスプレッドシートURLを「その他」から入力してください",
      "header": "テスト項目書",
      "options": [
        {"label": "URLを入力する", "description": "「その他」を選択してURLを入力"},
        {"label": "後で指定する", "description": "一旦スキップして後で指定"}
      ],
      "multiSelect": false
    },
    {
      "question": "テストタイプを選択してください",
      "header": "テストタイプ",
      "options": [
        {"label": "単体テスト", "description": "画面・機能単位の振る舞い検証（最小単位、因子水準網羅、debugビルド）"},
        {"label": "プレ結合テスト", "description": "複数画面・外部連携のシナリオ検証（複数機能、互換性網羅、releaseビルド）"}
      ],
      "multiSelect": false
    },
    {
      "question": "参照する資料のURLがあれば「その他」から入力してください（PBI/Issue、概要設計書など）",
      "header": "参照資料",
      "options": [
        {"label": "なし", "description": "参照資料なしで進める"},
        {"label": "URLを入力", "description": "「その他」を選択してURLを入力"}
      ],
      "multiSelect": false
    },
    {
      "question": "テスト作成時の注意事項があれば「その他」から入力してください",
      "header": "注意事項",
      "options": [
        {"label": "特になし", "description": "注意事項なしで進める"},
        {"label": "入力する", "description": "「その他」を選択して入力"}
      ],
      "multiSelect": false
    }
  ]
}
```

**成功確認**: 必要な情報がすべて揃った → Phase 2へ

---

## Phase 2: 資料一括読取

### 2-1. batch 構成の作成

Phase 1 で収集した情報から、`--batch` の JSON 配列を構成する：

**必須項目:**
```json
{"id": "1fpcWeiNCIefrUXN9567iopHxPGpB4VUKQ5uxr9CznVo", "type": "docs", "label": "テストガイドライン"},
{"id": "<spreadsheet_id>", "type": "sheets", "parts": "因子・水準,原本", "label": "テスト項目書"}
```

**参照資料の追加（Phase 1 で指定された Google Drive URL がある場合）:**

| URL パターン | type | 追加例 |
|-------------|------|--------|
| `docs.google.com/document/d/<id>` | docs | `{"id": "<id>", "type": "docs", "label": "設計書"}` |
| `docs.google.com/spreadsheets/d/<id>` | sheets | `{"id": "<id>", "type": "sheets", "label": "仕様書"}` |
| `docs.google.com/presentation/d/<id>` | presentations | `{"id": "<id>", "type": "presentations", "label": "資料"}` |

> **💡 Tip**: label は識別しやすい名前を付ける

### 2-2. 全資料の一括読取

```bash
python3 ~/.claude/skills/generate-test-item-skill/scripts/read_drive_file.py --batch '[
  {"id": "1fpcWeiNCIefrUXN9567iopHxPGpB4VUKQ5uxr9CznVo", "type": "docs", "label": "テストガイドライン"},
  {"id": "<spreadsheet_id>", "type": "sheets", "parts": "因子・水準,原本", "label": "テスト項目書"},
  ... Phase 1 で指定された Google Drive 資料を追加 ...
]'
```

> **💡 Note**: 結果は `/tmp/drive_batch_result.json` に自動保存される。

### 2-3. 結果ファイルの読み込み

**Read ツール**で結果ファイルを読み込む：

```
/tmp/drive_batch_result.json
```

> **💡 Note**: ファイル出力により大きなデータも一括で読み込める。

### 2-4. GitHub Issue の読取（該当する場合）

Phase 1 で GitHub Issue URL が指定された場合のみ：

```
mcp-gh-issue-mini MCPツール（例外的に使用）
```

### 2-5. 読取結果の確認

**レスポンス構造:**
```json
{
  "success": true,
  "files": {
    "テストガイドライン": {"content": [...], "structure": {...}},
    "テスト項目書": {"content": {"因子・水準": {...}, "原本": {...}}, "structure": {...}},
    "設計書": {"content": [...], "structure": {...}}
  },
  "summary": {"total": 3, "success": 3, "failed": 0}
}
```

**確認ポイント:**
- **テストガイドライン**: 「■単体テスト」「■プレ結合テスト」セクションから目的・スコープ・観点を把握
- **テスト項目書**: 因子水準表の数と構成、原本シートの列構成と **sheetId（Phase 5で使用）**
- **参照資料**: 機能仕様、画面遷移、期待動作などを把握

**「原本」シートが存在しない場合：**

> ⚠️ テスト項目書に「原本」シートが見つかりません。
>
> 「原本」シートはテスト項目のテンプレートとして使用します。
> 以下の手順で追加してください：
>
> 1. スプレッドシートを開く
> 2. 新しいシートを作成し、名前を「原本」に設定
> 3. テスト項目の列構成（№、因子水準列、前提条件、操作手順、期待結果など）を設定
> 4. 追加が完了したらお知らせください

ユーザーから追加完了の報告を受けたら、再度読み取って続行する。

**成功確認**: 全ての資料が読み取れた → Phase 3へ

---

## Phase 3: 仕様確認

### 3-1. 不明点の質問

操作手順・期待結果・仕様等の不明点について整理してユーザーに質問する。
不明点がなくなるまで繰り返し実施。

**成功確認**: 不明点が解消された → Phase 4へ

---

## Phase 4: 計画立案・承認

### 4-1. Planサブエージェントでテスト作成計画を立案

**⚠️ 重要な制約事項：**
- **ペアワイズ法・直交表・PICT等による組み合わせ削減は禁止**
- 因子・水準の全組み合わせ（フルカバレッジ）を生成すること
- 項目数が多くなっても削減提案はしないこと

以下の情報をサブエージェントに渡す：
- テストタイプ（単体テスト/プレ結合テスト）
- テストガイドラインから把握した観点
- 因子・水準シートの構成
- PBI/Issue や概要設計書から得た仕様情報
- ユーザーとの質疑応答で確認した内容
- **上記の制約事項（ペアワイズ法禁止、全組み合わせ必須）**

### 4-2. サンプルテスト項目の作成

計画に基づいて、**各因子水準表から1〜2件のサンプルテスト項目**を作成する。

**サンプルフォーマット：**

```
【サンプルテスト項目】<因子水準表タイトル>

■ サンプル1: <因子の組み合わせ概要>

前提条件:
- <前提条件1>
- <前提条件2>

操作手順:
- <操作1>
- <操作2>
- <操作3>

期待結果:
- <期待結果>
```

### 4-3. ユーザー承認

計画案とサンプルテスト項目をユーザーに提示し、承認を要求する。
フィードバックがあれば、サンプルを修正して再提示する。

**成功確認**: ユーザーから承認を得た → Phase 5へ

---

## Phase 5: テスト項目生成

### 5-1. 組み合わせパターンの生成

```bash
python3 ~/.claude/skills/generate-test-item-skill/scripts/generate_combinations.py '<factors_json>'
```

**factors_json の形式：**

```json
{
  "因子A": ["A1", "A2", "A3"],
  "因子B": ["B1", "B2"],
  "ワンパス": ["D1", "D2", "D3"],
  "期待値": ["E1", "E2"]
}
```

> **💡 Note**: 因子名に「ワンパス」「期待値」「OS」を含む場合は特別扱いされる（スクリプト内で自動分類）

### 5-2. サブエージェントの並列起動

因子水準表の数だけ **test-item-writer** サブエージェントを並列起動。

**⚠️ 重要**: 1つのレスポンス内で複数のTaskツールを同時に呼び出すこと（`run_in_background`は使用しない）。

**Taskツール呼び出しパラメータ：**

```
subagent_type: test-item-writer
prompt: |
  以下のパラメータでテスト項目書を作成してください：

  - spreadsheet_id: <対象スプレッドシートID>
  - source_sheet_id: <原本シートのID>
  - sheet_name: <因子水準表のタイトル（複製後のシート名）>
  - factors_data: <該当する因子・水準データ>
  - test_requirements: <対応する参考情報とテスト仕様>
  - test_type: <テストタイプ（「単体テスト」または「プレ結合テスト」）>
  - test_guidelines: <テストタイプに応じた観点・方針>
  - sample_items: <Phase 4-2で承認されたサンプルテスト項目>

  注意事項:
  - 最初に原本シートを複製してシート名を設定すること
  - A列の№は追加不要（既存の番号を使用）
  - サンプルテスト項目の記述スタイルに従って作成すること
  - 操作手順は番号付きではなく箇条書き（・）で記載すること
```

**成功確認**: すべてのサブエージェントが完了した → Phase 6へ

---

## Phase 6: 完了確認・クリーンアップ

### 6-1. 結果報告

以下の情報を報告：
- 処理対象シート数
- 生成したテスト項目の総数
- 発生した警告やエラー

### 6-2. 一時ファイルの削除

```bash
rm -f /tmp/test_items*.json /tmp/drive_batch_result.json
```

**成功確認**: 一時ファイルが削除された → 完了

---

## 使用スクリプト

| 操作 | スクリプト |
|------|-----------|
| 読み取り | `read_drive_file.py` |
| 組み合わせ生成 | `generate_combinations.py` |
| テスト項目書き込み | `write_test_items.py` |

スクリプトパス: `~/.claude/skills/generate-test-item-skill/scripts/`

---

## エラー対応

| エラー | 対応 |
|-------|------|
| 認証エラー / トークンエラー | [SETUP.md](SETUP.md) のセットアップワークフローを実行 |
| ModuleNotFoundError | `pip install google-auth google-auth-oauthlib google-api-python-client` を実行 |
| シート名が見つからない | エラーメッセージの `availableSheets` から正しい名前を使用 |

**エラーフィードバックループ**: エラー確認 → 対応 → 該当フェーズ再実行 → 成功まで繰り返す
