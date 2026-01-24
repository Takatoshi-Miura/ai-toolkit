# スラッシュコマンド作成ベストプラクティス

スラッシュコマンドの作成に関する公式ベストプラクティスをまとめたリファレンスです。

## 目次

1. [共通原則](#共通原則)
2. [スラッシュコマンド](#スラッシュコマンド)
3. [使い分けガイド](#使い分けガイド)
4. [要件収集テンプレート](#要件収集テンプレート)
5. [設計案提示フォーマット](#設計案提示フォーマット)

---

## 共通原則

### Description の重要性

Claudeは **descriptionだけ** を読んで自動選択・タスク委譲を判断します。

**必須要素**:
1. **何をするか**: 具体的なアクション
2. **いつ使うか**: 使用タイミング・トリガーコンテキスト

**常に三人称で書く**（説明はシステムプロンプトに挿入されるため）:
- ✅ 良い：「Excelファイルを処理してレポートを生成します」
- ❌ 避ける：「Excelファイルの処理をお手伝いできます」
- ❌ 避ける：「これを使用してExcelファイルを処理できます」

**❌ 悪い例**:
```yaml
description: Helps with documents
```

**✅ 良い例**:
```yaml
description: PDFファイルからテキストや表を抽出し、フォーム入力やドキュメント結合を行う。PDFファイルの処理を依頼された時、または「PDF」「フォーム」「抽出」などのキーワードが含まれる場合に使用。
```

### 簡潔さが鍵

コンテキストウィンドウは共有リソースです。情報の各部分に問いかけてください：
- 「Claudeは本当にこの説明が必要か？」
- 「Claudeがこれを知っていると仮定できるか？」
- 「このパラグラフはそのトークンコストに見合う価値があるか？」

**デフォルトの仮定**: Claudeはすでに非常に賢い。Claudeが既に持っていないコンテキストのみを追加する。

### 命名規則

**小文字・数字・ハイフンのみ**（kebab-case）

✅ 良い例: `code-reviewer`, `pdf-processor`, `git-commit`
❌ 悪い例: `CodeReviewer`, `pdf_processor`, `helper`, `utils`

**動名詞形を推奨**（動詞 + -ing）:
- `processing-pdfs`
- `analyzing-spreadsheets`
- `testing-code`

---

## スラッシュコマンド

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

### フロントマターフィールド

| フィールド | 用途 | デフォルト |
|-----------|------|-----------|
| `description` | コマンドの説明（Skillツール対応に必須） | プロンプト1行目 |
| `allowed-tools` | 使用可能なツール | 会話から継承 |
| `argument-hint` | 期待する引数の表示 | なし |
| `model` | 使用するモデル | 会話から継承 |
| `disable-model-invocation` | Skillツール経由の呼び出しを禁止 | false |
| `hooks` | コマンド実行時のフック定義 | なし |

### 引数の受け取り方

#### $ARGUMENTS - 全引数

```markdown
Issue #$ARGUMENTS を修正してください
```
使用例: `/fix-issue 123 high-priority` → `$ARGUMENTS` = "123 high-priority"

#### 位置パラメータ ($1, $2, $3...)

```markdown
---
argument-hint: [pr-number] [priority]
---
PR #$1 をレビュー。優先度: $2
```
使用例: `/review-pr 456 high` → `$1`="456", `$2`="high"

### 特殊構文

#### Bash実行 (!`command`)

コマンド実行前にBashを実行し、結果を埋め込む：

```markdown
---
allowed-tools: Bash(git:*)
---

## 現在の状態
- git status: !`git status`
- 現在のブランチ: !`git branch --show-current`
- 最近のコミット: !`git log --oneline -10`
```

#### ファイル参照 (@filepath)

```markdown
@src/config.js の設定を確認してください。
```

### 1ファイル完結の原則

スラッシュコマンドは**1つのmdファイルで完結**させてください。

**❌ アンチパターン**: 外部taskファイルへの参照
```markdown
1. ~/path/to/task.md の手順で実行
```

**✅ 推奨パターン**:
- Skillsが自動発動する処理はSkillsに委譲
- それ以外は手順をコマンドに統合

### Allowed-Tools パターン

```yaml
# 特定コマンドのみ許可
allowed-tools: Bash(git add:*), Bash(git status:*), Bash(git commit:*)

# 読み取り専用
allowed-tools: Read, Grep, Glob

# フルアクセス
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
```

### 名前空間（サブディレクトリ）

```
.claude/commands/
├── frontend/
│   └── component.md  → /component (project:frontend)
└── backend/
    └── test.md       → /test (project:backend)
```

### 実用例：GitHub Issue修正コマンド

Anthropic公式ドキュメントで紹介されているパターン：

```markdown
---
description: GitHub Issueを分析して修正する
allowed-tools: Bash(gh:*), Read, Write, Edit
argument-hint: [issue-number]
---

# GitHub Issue修正

以下の手順でIssue #$ARGUMENTSを修正してください：

1. `gh issue view $ARGUMENTS` でIssue詳細を確認
2. 関連するコードを特定
3. 修正を実装
4. テストを実行
5. 結果を報告
```

使用例：`/fix-github-issue 1234`

### バージョン管理のベストプラクティス

**チーム共有のためにGitにコミット**:
- プロジェクトレベルのコマンド（`.claude/commands/`）はバージョン管理に含める
- チームメンバー全員が同じワークフローを共有できる
- コマンドの履歴管理と改善が可能

### 反復的改善

スラッシュコマンドはプロンプトチューニングと同様に反復的に改善してください：

1. **初版作成**: 基本的な機能を実装
2. **実際に使用**: 実務で効果を確認
3. **フィードバック収集**: 使いにくい点を洗い出し
4. **改善**: 必要に応じて手順を追加・修正
5. **繰り返し**: 効果的になるまで改善を続ける

### チェックリスト

- [ ] **1ファイルで完結している（外部taskファイルを参照していない）**
- [ ] **Skillsで代替可能な処理は明示的参照を書かない**
- [ ] `description`を設定（Skillツール経由で呼び出す場合は必須）
- [ ] `argument-hint`で期待する引数を明示
- [ ] `allowed-tools`は必要最小限
- [ ] `$ARGUMENTS`または`$1`, `$2`で引数を適切に受け取る
- [ ] `!`command``でコンテキスト情報を取得（必要な場合）
- [ ] 曖昧さを避けるため、プロジェクトとユーザーで異なる名前を使用
- [ ] **チーム共有の場合はGitにコミット**
- [ ] **実際の使用を通じて反復的に改善**

---

## 使い分けガイド

| 用途 | 推奨リソース |
|------|-------------|
| 簡潔で頻繁に使うプロンプト | スラッシュコマンド |
| 単一ファイルの指示 | スラッシュコマンド |
| 手動呼び出しが必要 | スラッシュコマンド |
| URL/キーワードで自動発動させたい | Skill |
| 複雑なマルチステップワークフロー | Skill |
| スクリプトやユーティリティが必要 | Skill |
| チームワークフロー標準化 | Skill |
| 専門的思考・独自の観点が必要 | サブエージェント |
| 並列実行・コンテキスト分離が必要 | サブエージェント |
| 特定のツール制限・権限を強制したい | サブエージェント |
| 大量の操作を分離したい | サブエージェント |

### 判断フローチャート

```
ユーザーが明示的に呼び出す？
├─ Yes → スラッシュコマンド
└─ No → 自動発動させたい？
         ├─ Yes → Skill
         └─ No → 専門的処理を委譲？
                  ├─ Yes → サブエージェント
                  └─ No → スラッシュコマンド
```

### スラッシュコマンドを使用する場合（詳細）

- **繰り返し使用するプロンプト**: デバッグループやログ解析など、頻繁に実行するタスク
- **即座に呼び出したい**: `/command` で明示的に実行したい処理
- **シンプルな処理フロー**: 複雑な分岐がない、直線的な手順
- **チームで標準化したいワークフロー**: 全員が同じ手順で作業できる

### メイン会話を使用する場合

- タスクが頻繁なやり取りや反復的な改善が必要
- 複数のフェーズが重要なコンテキストを共有
- 迅速でターゲット化された変更

---

## 要件収集テンプレート

スラッシュコマンド作成時は、以下の情報を収集してください：

```
どのようなコマンドを作成したいですか？

以下の情報を教えてください：
- **目的**: このコマンドで何を実現したいですか？
- **背景**: どのような場面で使いたいですか？
- **期待する動作**: AIにどのような作業をさせたいですか？

例: 「PRのコードレビューを効率化したい。レビュー観点に沿ってコードをチェックし、指摘事項をまとめてほしい」
```

---

## 設計案提示フォーマット

ユーザーとの確認時は、以下のフォーマットで提示してください：

```
## コマンド設計案

| 項目 | 内容 |
|------|------|
| コマンド名 | {command_name} |
| 説明 | {description} |
| 役割 | {role} |
| ツール | {allowed_tools} |

### 提案する手順
{steps}

この設計でよろしいですか？修正があればお知らせください。
```

---

## 実用的なパターン例

### パターン1: 自動化されたレビュー

```markdown
---
description: 変更されたコードを自動レビューし、タイポをチェックする
allowed-tools: Bash(git:*), Read, Grep
---

# コードレビュー（タイポチェック）

あなたはリンターです。mainブランチとの差分を確認し、タイポに関連する問題を報告してください。

出力形式：
- 1行目：ファイル名と行番号
- 2行目：問題の説明
- それ以外のテキストは出力しないこと

手順：
1. `git diff main` で変更を確認
2. タイポを検出
3. 上記の形式で報告
```

### パターン2: パイプライン統合

package.jsonへの統合例：

```json
{
  "scripts": {
    "lint:claude": "claude -p 'you are a linter. please look at the changes vs. main and report any issues related to typos. report the filename and line number on one line, and a description of the issue on the second line. do not return any other text.'"
  }
}
```

### パターン3: データ変換

```bash
cat build-error.txt | claude -p 'concisely explain the root cause of this build error' > output.txt
```

---

## 参考リンク

- [公式: Custom Slash Commands](https://code.claude.com/docs/ja/slash-commands)
- [Anthropic Blog: Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices)
- [Claude Code: Common Workflows](https://code.claude.com/docs/en/common-workflows)
