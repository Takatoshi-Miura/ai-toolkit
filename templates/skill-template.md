# Skillのテンプレート

以下のテンプレートを使用してSKILL.mdファイルを生成してください。
`{変数名}` の部分を適切な値に置き換えてください。

## テンプレート

```markdown
---
name: {skill_name}
description: {description}
allowed-tools: {allowed_tools}
user-invocable: {user_invocable}
disable-model-invocation: {disable_model_invocation}
---

# {skill_title}

{overview}

## 役割

{role_description}

## 重要：このスキルの使い方

**各フェーズを順番に実行すること。フェーズを飛ばしてはならない。**

**制約事項：**
{constraints}

---

## Phase 0: Todo登録

**TodoWriteツールで以下を登録：**

```json
[
  {"content": "Phase 1: {phase1_title}", "activeForm": "{phase1_active}", "status": "pending"},
  {"content": "Phase 2: {phase2_title}", "activeForm": "{phase2_active}", "status": "pending"},
  {"content": "Phase 3: {phase3_title}", "activeForm": "{phase3_active}", "status": "pending"}
]
```

各フェーズ開始時に`in_progress`、完了時に`completed`に更新する。

---

## Phase 1: {phase1_title}

### 1-1. {substep_title}
{substep_description}

### 1-2. {substep_title}
{substep_description}

**成功確認**: {success_criteria} → Phase 2へ

---

## Phase 2: {phase2_title}

### 2-1. {substep_title}
{substep_description}

**成功確認**: {success_criteria} → Phase 3へ

---

## Phase 3: {phase3_title}

### 3-1. {substep_title}
{substep_description}

**成功確認**: {success_criteria} → 完了

---

## 詳細リファレンス

- **詳細ワークフロー**: [WORKFLOW.md](WORKFLOW.md)
- **セットアップ**: [SETUP.md](SETUP.md)

## エラー対応

| エラー | 対応 |
|-------|------|
| {error_type_1} | {error_handling_1} |
| {error_type_2} | {error_handling_2} |

**エラーフィードバックループ**:
1. エラーメッセージを確認
2. 上記の表に従って対応
3. 該当フェーズを再実行
4. 成功するまで繰り返す

## 出力形式
{output_format}

## 注意事項
{notes}
```

## 変数の説明

| 変数名 | 説明 | 例 |
|--------|------|-----|
| `{skill_name}` | スキル名（kebab-case、最大64文字） | `pdf-processor`, `data-analyzer` |
| `{description}` | スキルの説明（**最大1024文字、下記参照**） | 下記「descriptionの書き方」参照 |
| `{allowed_tools}` | 許可なしで使用できるツール | `Read, Grep, Glob` |
| `{user_invocable}` | スラッシュメニュー表示（デフォルト: true） | `true`, `false` |
| `{disable_model_invocation}` | モデルによる自動発動を無効化 | `true`, `false` |
| `{skill_title}` | スキルのタイトル | PDF処理スキル |
| `{overview}` | スキルの概要説明（1行） | PDFファイルからデータを抽出し、構造化された形式で出力する。 |
| `{role_description}` | スキルの役割 | PDFデータ抽出のエキスパートとして... |
| `{constraints}` | 制約事項のリスト | - 〜のみを使用する |
| `{phaseN_title}` | フェーズのタイトル | 情報収集 |
| `{phaseN_active}` | 進行中表示（〜中の形式） | 情報を収集中 |
| `{substep_title}` | サブステップのタイトル | 必要情報の一括収集 |
| `{substep_description}` | サブステップの説明 | AskUserQuestionツールを使用して... |
| `{success_criteria}` | 成功確認の条件 | 必要な情報がすべて揃った |
| `{error_type_N}` | エラーの種類 | 認証エラー |
| `{error_handling_N}` | エラーの対応方法 | SETUP.mdを参照して再設定 |
| `{output_format}` | 出力形式の説明 | マークダウン形式でデータを整形して出力 |
| `{notes}` | 注意事項 | 大きなPDFは分割して処理する |

## フロントマターのフィールド

| フィールド | 必須 | 説明 |
|-----------|------|------|
| `name` | ✅ | スキル識別子（小文字、数字、ハイフンのみ、最大64文字） |
| `description` | ✅ | Claudeがスキル適用判断に使う説明文（**最大1024文字**） |
| `allowed-tools` | ❌ | スキル有効時に許可なしで使えるツール |
| `model` | ❌ | 使用するモデル（sonnet/opus/haiku/inherit） |
| `context` | ❌ | `fork`でサブエージェント実行 |
| `user-invocable` | ❌ | スラッシュメニュー表示（デフォルト: true） |
| `disable-model-invocation` | ❌ | モデルによる自動発動を無効化（デフォルト: false） |
| `hooks` | ❌ | ライフサイクルフック定義 |

## descriptionの書き方（最重要）

Claudeは **descriptionだけ** を読んでスキルを自動選択します。以下の3要素を必ず含めてください。

### 必須要素

1. **何をするか**: 具体的なアクション（抽出、入力、マージ、分析）
2. **いつ使うか**: 使用タイミング（〜の時に使用、〜を依頼された時）
3. **トリガー用語**: 発動させたいキーワードを自然に含める

### ❌ 悪い例

```yaml
description: Helps with documents
```
→ 曖昧すぎて自動選択されにくい

### ✅ 良い例

```yaml
description: Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction.
```
→ 何をするか（Extract, fill, merge）＋いつ使うか（working with PDF files）＋キーワード（PDFs, forms, extraction）

### 日本語の例

```yaml
description: PDFファイルからテキストや表を抽出し、フォーム入力やドキュメント結合を行う。PDFファイルの処理を依頼された時、または「PDF」「フォーム」「抽出」などのキーワードが含まれる場合に使用。
```

## 可視性制御

| 設定 | スラッシュメニュー | 自動検出 | 用途 |
|------|-----------------|---------|------|
| `user-invocable: true`（デフォルト） | 表示 | ○ | ユーザーが明示的に呼び出し可能 |
| `user-invocable: false` | 非表示 | ○ | Claude自動判断のみ（前提知識の提供等） |
| `disable-model-invocation: true` | 表示 | ✗ | ユーザー明示呼び出しのみ（自動発動させたくない場合） |

## プログレッシブディスクロージャー

**SKILL.mdは500行以下に保つ**ことが推奨されています。詳細は別ファイルに分離してください。

### ディレクトリ構造例

```
my-skill/
├── SKILL.md          # 概要とクイックスタート（500行以下）
├── WORKFLOW.md       # 詳細ワークフロー
├── SETUP.md          # セットアップ・トラブルシューティング
├── REFERENCE.md      # 詳細リファレンス
├── EXAMPLES.md       # 使用例
└── scripts/          # ユーティリティスクリプト
```

### SKILL.md内でのリンク

```markdown
詳細は [REFERENCE.md](REFERENCE.md) を参照してください。
使用例は [EXAMPLES.md](EXAMPLES.md) を参照してください。
```

Claudeはリンク経由でサポートファイルを検出し、必要時にのみ読み込みます。

## 配置先

`~/Documents/Git/ai-toolkit/skills/{skill_name}/SKILL.md`

## チェックリスト

- [ ] nameは小文字・数字・ハイフンのみ（最大64文字）
- [ ] descriptionは「何をするか＋いつ使うか＋トリガー用語」を含む（最大1024文字）
- [ ] allowed-toolsは必要最小限の権限
- [ ] SKILL.mdは500行以下
- [ ] Phase構造で手順が明確に分かれている
- [ ] 各Phaseに成功確認がある
- [ ] エラー対応表がある
- [ ] 詳細は別ファイルに分離されている
