---
name: slash-command-best-practice
description: Claude Codeスラッシュコマンド作成・設計時にベストプラクティスを提供。「コマンド作成」「スラッシュコマンド」「/command」「新しいコマンド」「コマンド設計」などの文脈で自動適用。$ARGUMENTS/$1/$2の使い方、allowed-tools設定、!`bash`実行、@ファイル参照などの公式推奨事項を提供。
allowed-tools: Read, Glob
user-invocable: false
---

# スラッシュコマンド ベストプラクティス

Claude Code公式ドキュメントに基づくスラッシュコマンド作成のベストプラクティスです。

## ファイル構造

### 配置場所

| 場所 | パス | 適用対象 | 優先度 |
|------|------|---------|--------|
| プロジェクト | `.claude/commands/` | リポジトリメンバー | 高 |
| 個人 | `~/.claude/commands/` | すべてのプロジェクト | 低 |

**注意**: 名前が衝突した場合、プロジェクトコマンドが優先されます。

### 基本構造

```markdown
---
description: コマンドの説明
allowed-tools: Bash(git:*), Read, Write
argument-hint: [arg1] [arg2]
---

# コマンドの指示内容

$ARGUMENTSを使用して引数を受け取る
```

## 1ファイル完結の原則

スラッシュコマンドは**1つのmdファイルで完結**させてください。

### ❌ アンチパターン: 外部taskファイルへの参照

```markdown
# 手順
1. ~/Documents/Git/ai-toolkit/task/some-task.md の手順でファイルを読み取る
2. 処理を実行
```

### ✅ 推奨パターン

#### パターンA: Skillsに任せる

Skillsが自動発動する処理は、明示的な参照を書かずにSkillsに委譲：

```markdown
# 手順
1. Google Driveファイルを読み取る  ← read-google-drive-skill が自動発動
2. 処理を実行
```

#### パターンB: 手順をコマンドに統合

Skillsがない処理は、すべての手順を1ファイルに含める：

```markdown
# 手順
1. Redmineチケットを読み取る
   - URLからチケットIDを抽出
   - mcp__mcp-redmine__redmine_get_detail で詳細取得
2. 処理を実行
```

### 理由

- **保守性**: 1ファイルで完結していれば、変更時の影響範囲が明確
- **可読性**: コマンドを読むだけで全体像が把握できる
- **Skillsとの連携**: 共通処理はSkillsに委譲し、重複を排除

## フロントマターフィールド

| フィールド | 用途 | デフォルト |
|-----------|------|-----------|
| `description` | コマンドの説明（Skillツール経由での呼び出しに必要） | プロンプト1行目 |
| `allowed-tools` | 使用可能なツール | 会話から継承 |
| `argument-hint` | 期待する引数の表示 | なし |
| `model` | 使用するモデル | 会話から継承 |
| `disable-model-invocation` | Skillツール経由の呼び出しを禁止 | false |

## 引数の受け取り方

### $ARGUMENTS - 全引数

```markdown
Issue #$ARGUMENTS を修正してください
```

使用例: `/fix-issue 123 high-priority`
→ `$ARGUMENTS` = "123 high-priority"

### 位置パラメータ ($1, $2, $3...)

```markdown
---
argument-hint: [pr-number] [priority] [assignee]
description: PRをレビュー
---

PR #$1 をレビュー。優先度: $2、担当: $3
```

使用例: `/review-pr 456 high alice`
→ `$1`="456", `$2`="high", `$3`="alice"

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

## タスク
上記の変更に基づいてコミットを作成: $ARGUMENTS
```

### ファイル参照 (@filepath)

ファイル内容をプロンプトに含める：

```markdown
@src/old-version.js の実装を確認し、
@src/new-version.js と比較してください。
```

## Allowed-Tools パターン

```yaml
# 特定コマンドのみ許可
allowed-tools: Bash(git add:*), Bash(git status:*), Bash(git commit:*)

# 読み取り専用
allowed-tools: Read, Grep, Glob

# フルアクセス
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
```

## 実践的な例

### Git コミットコマンド

```markdown
---
allowed-tools: Bash(git add:*), Bash(git status:*), Bash(git commit:*)
argument-hint: [message]
description: gitコミットを作成
---

## コンテキスト

- 現在のgit status: !`git status`
- 変更差分: !`git diff HEAD`
- 現在のブランチ: !`git branch --show-current`
- 最近のコミット: !`git log --oneline -10`

## タスク

上記の変更に基づいて、メッセージ「$ARGUMENTS」でコミットを作成してください。
```

### PRレビューコマンド

```markdown
---
argument-hint: [pr-number]
description: PRをレビュー
allowed-tools: Bash(gh:*), Read
---

PR #$1 をレビューしてください。

以下の観点でチェック：
- セキュリティの脆弱性
- パフォーマンス最適化
- コードスタイル違反
- テストカバレッジ
```

## 名前空間（サブディレクトリ）

サブディレクトリでグループ化可能：

```
.claude/commands/
├── frontend/
│   └── component.md  → /component (project:frontend)
└── backend/
    └── test.md       → /test (project:backend)
```

## チェックリスト

- [ ] **外部taskファイルを参照していない（1ファイル完結）**
- [ ] **Skillsで代替可能な処理は明示的参照を書かない**
- [ ] descriptionを設定（Skillツール経由で呼び出す場合は必須）
- [ ] argument-hintで期待する引数を明示
- [ ] allowed-toolsは必要最小限
- [ ] $ARGUMENTSまたは$1, $2で引数を適切に受け取る
- [ ] !`command`でコンテキスト情報を取得（必要な場合）

## Skill との使い分け

| 用途 | 推奨 |
|------|------|
| 簡潔で頻繁に使うプロンプト | スラッシュコマンド |
| 単一ファイルの指示 | スラッシュコマンド |
| 複雑なマルチステップワークフロー | Skill |
| 複数のサポートファイルが必要 | Skill |
| チーム標準化 | Skill |

## 参考: 既存コマンドの確認

```bash
# プロジェクトのコマンド一覧
ls -la .claude/commands/

# 個人のコマンド一覧
ls -la ~/.claude/commands/
```
