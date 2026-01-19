# スラッシュコマンドのテンプレート

以下のテンプレートを使用してスラッシュコマンドファイルを生成してください。
用途に応じて「自己完結型」または「タスク参照型」を選択してください。

## テンプレートの選び方

| タイプ | 使用場面 | 特徴 |
|--------|---------|------|
| **自己完結型** | 手順がこのコマンド専用で、他から再利用されない場合 | 1ファイルで完結、管理が容易 |
| **タスク参照型** | 複数コマンドから共通の手順を参照する場合 | taskファイルで手順を共有、DRY原則 |

---

## テンプレートA: 自己完結型（推奨）

1つのコマンドで完結する処理に適しています。

```markdown
---
allowed-tools: {allowed_tools}
description: {description}
argument-hint: {argument_hint}
---

# 役割
{role}
日本語で回答すること。

# 前提条件（必要な場合のみ）
{prerequisites}

# 手順

## Phase 1: {phase_1_title}

1. {step_1}
2. {step_2}

## Phase 2: {phase_2_title}

3. {step_3}
4. {step_4}

## Phase 3: {phase_3_title}

5. {step_5}

# 出力フォーマット（必要な場合のみ）

```
{output_format_example}
```

# 注意事項

- {note_1}
- {note_2}
```

### 変数の説明

| 変数名 | 説明 | 例 |
|--------|------|-----|
| `{allowed_tools}` | 使用するツール | `mcp__mcp-google-drive__*`, `Read, Write, Glob` |
| `{description}` | コマンドの説明（1行） | モバイルアプリ開発のスペシャリストとしてPRのコードレビューを実施 |
| `{argument_hint}` | 期待する引数（下記参照） | `[pr-number]`, `[file-path] [output-format]` |
| `{role}` | AIの役割 | あなたはモバイルアプリ開発のスペシャリストです |
| `{prerequisites}` | 前提条件（参照ファイル、URL等） | `task/retrospective-common.md` の内容を把握していること |
| `{phase_N_title}` | フェーズのタイトル | データ収集、分析、レポート作成 |
| `{step_N}` | 具体的な手順 | スプレッドシートから売上データを読み取る |
| `{output_format_example}` | 出力形式の例 | Markdown形式のレポート |
| `{note_N}` | 注意事項 | エラー時は再認証を促す |

---

## テンプレートB: タスク参照型

複数のコマンドから共通のタスクを参照する場合に使用します。

```markdown
---
allowed-tools: {allowed_tools}
description: {description}
argument-hint: {argument_hint}
---

# 役割
{role}
日本語で回答すること。

# 手順

1. 以下のタスクファイルの内容を確認して全体像を把握する
2. ~/Documents/Git/ai-toolkit/task/{task_name}.md のタスクを実施する
3. タスク完了後、必要に応じて結果をまとめる
```

---

## フロントマターのフィールド

| フィールド | 必須 | 説明 |
|-----------|------|------|
| `description` | ✅ | コマンドの説明（Skillツール経由での呼び出しに必要） |
| `allowed-tools` | ❌ | 使用可能なツール（省略時は会話から継承） |
| `argument-hint` | ❌ | 期待する引数の表示（例: `[pr-number] [priority]`） |
| `model` | ❌ | 使用するモデル（省略時は会話から継承） |
| `disable-model-invocation` | ❌ | Skillツール経由の呼び出しを禁止（デフォルト: false） |
| `hooks` | ❌ | コマンド実行時のフック |

---

## 引数の受け取り方

### $ARGUMENTS - 全引数を一括取得

```markdown
Issue #$ARGUMENTS を修正してください
```

**使用例**: `/fix-issue 123 high-priority`
→ `$ARGUMENTS` = "123 high-priority"

### 位置パラメータ ($1, $2, $3...)

個別の引数にアクセスする場合：

```markdown
---
argument-hint: [pr-number] [priority] [assignee]
description: PRをレビュー
---

PR #$1 をレビュー。優先度: $2、担当: $3
```

**使用例**: `/review-pr 456 high alice`
→ `$1`="456", `$2`="high", `$3`="alice"

---

## 特殊構文

### Bash実行 (!`command`)

コマンド実行前にBashを実行し、結果を埋め込む：

```markdown
---
allowed-tools: Bash(git:*)
description: コミット作成
---

## 現在の状態
- git status: !`git status`
- git diff: !`git diff HEAD`
- 現在のブランチ: !`git branch --show-current`
- 最近のコミット: !`git log --oneline -10`

## タスク
上記の変更に基づいてコミットを作成: $ARGUMENTS
```

### ファイル参照 (@filepath)

ファイル内容をプロンプトに含める：

```markdown
@src/old-version.js の実装を確認し、
@src/new-version.js と比較してください。
```

---

## Allowed-Tools パターン

```yaml
# 特定コマンドのみ許可
allowed-tools: Bash(git add:*), Bash(git status:*), Bash(git commit:*)

# 読み取り専用
allowed-tools: Read, Grep, Glob

# MCP全ツール
allowed-tools: mcp__mcp-google-drive__*

# フルアクセス
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
```

---

## 設計ガイドライン

### 必須セクション

| セクション | 必須 | 説明 |
|-----------|------|------|
| フロントマター | ✅ | `description`（allowed-toolsは任意） |
| `# 役割` | ✅ | AIの専門性・ペルソナを定義 |
| `日本語で回答すること。` | ✅ | 役割セクション内に記載 |
| `# 手順` | ✅ | 実行手順をPhase分けで記載 |

### 推奨セクション

| セクション | 推奨度 | 説明 |
|-----------|-------|------|
| `# 前提条件` | 中 | 必要な事前準備・参照ファイル |
| `# 出力フォーマット` | 高 | 期待する出力形式の具体例 |
| `# 注意事項` | 高 | 制約・エラーハンドリング |

### Claude公式ベストプラクティス準拠ポイント

1. **役割定義を冒頭に**: 「あなたは〜です」で始める
2. **構造化された指示**: Phase/ステップで論理的に整理
3. **具体的な例示**: 出力フォーマットに具体例を含める
4. **制約の明示**: 注意事項で禁止事項・エラー処理を記載
5. **ポジティブな指示**: 「〜しないこと」より「〜すること」を優先

---

## Skill との使い分け

| 用途 | 推奨 |
|------|------|
| 簡潔で頻繁に使うプロンプト | **スラッシュコマンド** |
| 単一ファイルの指示 | **スラッシュコマンド** |
| 明示的な呼び出し（`/command`） | **スラッシュコマンド** |
| 複雑なマルチステップワークフロー | Skill |
| 複数のサポートファイルが必要 | Skill |
| 自動発動させたい | Skill |

---

## 命名規則

- ファイル名: `kebab-case`（例: `review-code.md`, `analyze-performance.md`）
- 配置先: `~/Documents/Git/ai-toolkit/commands/`

## チェックリスト

- [ ] descriptionを設定（Skillツール経由で呼び出す場合は必須）
- [ ] argument-hintで期待する引数を明示（引数がある場合）
- [ ] allowed-toolsは必要最小限
- [ ] $ARGUMENTSまたは$1, $2で引数を適切に受け取る
- [ ] !`command`でコンテキスト情報を取得（必要な場合）
- [ ] 役割セクションに「日本語で回答すること。」を記載
