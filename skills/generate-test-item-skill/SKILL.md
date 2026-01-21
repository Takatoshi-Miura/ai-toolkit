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

## 使用方法

このスキルは手動で呼び出して使用します：

```
/generate-test-item-skill
```

## 重要：このスキルの使い方

**必ず以下のチェックリストをコピーして、各フェーズを順番に実行すること。**
フェーズを飛ばしたり、チェックリストなしで進めてはならない。

**制約事項：**
- このスキルはPythonスクリプトのみを使用する（MCPツールは使用しない）
- 認証エラーが発生した場合は、[SETUP.md](SETUP.md) のセットアップワークフローを実行する
- 各フェーズ完了時にTodoWriteで進捗を更新すること

## ワークフロー概要

**【必須】このチェックリストをコピーして進行状況を追跡（省略不可）：**

```
テスト項目書作成進捗：
- [ ] Phase 1: 情報収集
- [ ] Phase 2: スプレッドシート準備
- [ ] Phase 3: 仕様確認
- [ ] Phase 4: 計画立案・承認
- [ ] Phase 5: テスト項目生成（並列）
- [ ] Phase 6: 完了確認
```

---

## Phase 1: 情報収集

**チェックリスト更新**: `- [x] Phase 1: 情報収集`

### 1-1. 必要情報の確認

以下の情報が提供されていなければユーザーに質問：

| 項目 | 必須 | 説明 |
|------|------|------|
| テスト項目書URL | ✅ | Googleスプレッドシートのリンク |
| テストタイプ | ✅ | 「単体テスト」または「プレ結合テスト」 |
| PBI/Issue URL | - | 対象チケットのリンク |
| 概要設計書URL | - | 概要設計書のリンク |
| その他注意事項 | - | テスト作成時の注意点 |

### テストタイプの判断基準

| テストタイプ | 目的 | スコープ |
|-------------|------|----------|
| 単体テスト | 画面・機能単位の振る舞い検証 | 最小の画面・機能単位、因子水準網羅、debugビルド |
| プレ結合テスト | 複数画面・外部連携のシナリオ検証 | 複数画面・機能、互換性網羅、releaseビルド |

### 1-2. テストガイドラインの読取

ユーザーから必要情報を取得後、テストガイドラインを読み取る：

```bash
python3 ~/.claude/skills/generate-test-item-skill/scripts/read_drive_file.py 1fpcWeiNCIefrUXN9567iopHxPGpB4VUKQ5uxr9CznVo docs
```

「■単体テスト」と「■プレ結合テスト」のセクションから、それぞれの目的・スコープ・観点の違いを把握する。

**成功確認**: 必要な情報がすべて揃った → Phase 2へ

---

## Phase 2: スプレッドシート準備

**チェックリスト更新**: `- [x] Phase 2: スプレッドシート準備`

### 2-1. シート構造の読取（許可不要）

```bash
# シート一覧取得
python3 ~/.claude/skills/generate-test-item-skill/scripts/read_drive_file.py <spreadsheet_id> sheets
```

### 2-2. 「原本」シートの存在確認

シート一覧に「原本」シートが存在するか確認する。

**「原本」シートが存在しない場合:**

> ⚠️ テスト項目書に「原本」シートが見つかりません。
>
> 「原本」シートはテスト項目のテンプレートとして使用します。
> 以下の手順で追加してください：
>
> 1. スプレッドシートを開く
> 2. 新しいシートを作成し、名前を「原本」に設定
> 3. テスト項目の列構成（№、因子水準列、前提条件、操作手順、期待結果など）を設定
> 4. 追加が完了したらお知らせください
>
> 追加完了後、続きの処理を実行します。

**ユーザーから追加完了の報告を受けたら**、再度シート構造を読み取って続行する。

### 2-3. 因子水準シートの読取

```bash
python3 ~/.claude/skills/generate-test-item-skill/scripts/read_drive_file.py <spreadsheet_id> sheets '因子・水準'
```

因子水準表の数と各表のタイトルを特定する。

### 2-4. 原本シートの構造把握

```bash
python3 ~/.claude/skills/generate-test-item-skill/scripts/read_drive_file.py <spreadsheet_id> sheets '原本'
```

各列に記載する項目を把握する。原本シートのIDも確認しておく（Phase 5で使用）。

**成功確認**: シート構造と原本シートIDが把握できた → Phase 3へ

---

## Phase 3: 仕様確認

**チェックリスト更新**: `- [x] Phase 3: 仕様確認`

### 3-1. 参考情報の読取

**PBI/Issue（GitHub）の場合:**

```bash
# mcp-gh-issue-miniを使用（MCPツールのみ例外的に使用）
```

または read-redmine-skill が自動発動。

**概要設計書（Google Docs）の場合:**

```bash
python3 ~/.claude/skills/generate-test-item-skill/scripts/read_drive_file.py <doc_id> docs
```

### 3-2. 不明点の質問

操作手順や期待結果、仕様等の不明点について整理してユーザーに質問する。
不明点がなくなるまで繰り返し実施。

**成功確認**: 不明点が解消された → Phase 4へ

---

## Phase 4: 計画立案・承認

**チェックリスト更新**: `- [x] Phase 4: 計画立案・承認`

### 4-1. テスト作成計画の立案

Taskツールを使用してPlanサブエージェントを起動し、テスト作成計画を立案させる。

以下の情報をサブエージェントに渡す：
- テストタイプ（単体テスト/プレ結合テスト）
- テストガイドラインから把握した観点
- 因子・水準シートの構成
- PBI/Issue や概要設計書から得た仕様情報
- ユーザーとの質疑応答で確認した内容

### 4-2. ユーザー承認

計画案をユーザーに提示し、承認を要求する。

**成功確認**: ユーザーから承認を得た → Phase 5へ

---

## Phase 5: テスト項目生成（並列）

**チェックリスト更新**: `- [x] Phase 5: テスト項目生成（並列）`

### 5-1. 組み合わせパターンの生成

```bash
python3 ~/.claude/skills/generate-test-item-skill/scripts/generate_combinations.py '<factors_json>'
```

### 5-2. サブエージェントの並列起動

因子水準表の数だけ **test-item-writer** サブエージェントを並列起動。
各サブエージェントが「原本」シートを複製し、テスト項目を記載する。

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

  注意事項:
  - 最初に原本シートを複製してシート名を設定すること
  - A列の№は追加不要（既存の番号を使用）
  - 因子水準の組み合わせ順序はエージェントのプロンプトに従う
```

**成功確認**: すべてのサブエージェントが完了した → Phase 6へ

---

## Phase 6: 完了確認

**チェックリスト更新**: `- [x] Phase 6: 完了確認`

以下の情報を報告：
- 処理対象シート数
- 生成したテスト項目の総数
- 発生した警告やエラー

---

## 詳細リファレンス

- **詳細ワークフロー**: [WORKFLOW.md](WORKFLOW.md)
- **セットアップ・トラブルシューティング**: [SETUP.md](SETUP.md)

## 使用スクリプト

| 操作 | スクリプト |
|------|-----------|
| 読み取り | `~/.claude/skills/generate-test-item-skill/scripts/read_drive_file.py` |
| 値挿入 | `~/.claude/skills/generate-test-item-skill/scripts/insert_value.py` |
| シートコピー | `~/.claude/skills/generate-test-item-skill/scripts/copy_element.py` |
| セル結合（一括） | `~/.claude/skills/generate-test-item-skill/scripts/merge_cells_batch.py` |
| 組み合わせ生成 | `~/.claude/skills/generate-test-item-skill/scripts/generate_combinations.py` |

## エラー対応

| エラー | 対応 |
|-------|------|
| 認証エラー / トークンエラー | [SETUP.md](SETUP.md) のセットアップワークフローを実行 |
| ModuleNotFoundError | `pip install google-auth google-auth-oauthlib google-api-python-client` を実行 |
| シート名が見つからない | エラーメッセージの `availableSheets` から正しい名前を使用 |

**エラーフィードバックループ**:
1. エラーメッセージを確認
2. 上記の表に従って対応
3. 該当フェーズを再実行
4. 成功するまで繰り返す
