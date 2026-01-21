# Claude Code リソース作成ベストプラクティス

スラッシュコマンド、サブエージェント、Skillの作成に関する公式ベストプラクティスをまとめたリファレンスです。

## 目次

1. [共通原則](#共通原則)
2. [スラッシュコマンド](#スラッシュコマンド)
3. [サブエージェント](#サブエージェント)
4. [Skill](#skill)
5. [使い分けガイド](#使い分けガイド)

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

### チェックリスト

- [ ] **1ファイルで完結している（外部taskファイルを参照していない）**
- [ ] **Skillsで代替可能な処理は明示的参照を書かない**
- [ ] `description`を設定（Skillツール経由で呼び出す場合は必須）
- [ ] `argument-hint`で期待する引数を明示
- [ ] `allowed-tools`は必要最小限
- [ ] `$ARGUMENTS`または`$1`, `$2`で引数を適切に受け取る
- [ ] `!`command``でコンテキスト情報を取得（必要な場合）
- [ ] 曖昧さを避けるため、プロジェクトとユーザーで異なる名前を使用

---

## サブエージェント

### 配置場所

| 場所 | スコープ | 優先度 |
|------|---------|--------|
| `--agents` CLIフラグ | セッション | 1（最高） |
| `.claude/agents/` | プロジェクト | 2 |
| `~/.claude/agents/` | ユーザー | 3 |

**ベストプラクティス**: プロジェクトエージェント（`.claude/agents/`）をバージョン管理にチェックイン

### 基本構造

```markdown
---
name: code-reviewer
description: Expert code review specialist. Proactively reviews code for quality, security, and maintainability. Use immediately after writing or modifying code.
tools: Read, Grep, Glob, Bash
model: inherit
permissionMode: default
---

You are a senior code reviewer.

When invoked:
1. Run git diff to see recent changes
2. Focus on modified files
3. Begin review immediately

Review checklist:
- Code is clear and readable
- Proper error handling
- No exposed secrets
- Good test coverage
```

### フロントマターフィールド

| フィールド | 必須 | 説明 |
|-----------|------|------|
| `name` | ✅ | 小文字とハイフンの一意の識別子 |
| `description` | ✅ | Claudeが委譲を判断する基準（詳細に！） |
| `tools` | ❌ | 使用可能なツール（省略時はすべて継承） |
| `disallowedTools` | ❌ | 拒否するツール |
| `model` | ❌ | `sonnet`/`opus`/`haiku`/`inherit`（デフォルト: sonnet） |
| `permissionMode` | ❌ | 権限モード |
| `skills` | ❌ | プリロードするスキル |
| `hooks` | ❌ | ライフサイクルフック |

### Model 選択基準

| モデル | 特徴 | 用途 |
|-------|------|------|
| `haiku` | 高速・軽量 | 検索、読み取り専用タスク、シンプルな処理 |
| `sonnet` | バランス型（デフォルト） | 一般的なコード解析・修正 |
| `opus` | 最高性能 | 複雑な推論、アーキテクチャ設計 |
| `inherit` | 親と同じ | 一貫性が必要な場合 |

**モデル別のテスト考慮事項**:
- **Haiku**: スキルは十分なガイダンスを提供しているか？
- **Sonnet**: スキルは明確で効率的か？
- **Opus**: スキルは過度な説明を避けているか？

### Permission Mode

| モード | 説明 |
|-------|------|
| `default` | 通常の権限チェック |
| `acceptEdits` | ファイル編集を自動承認 |
| `dontAsk` | 権限プロンプトを自動拒否 |
| `bypassPermissions` | 全権限をバイパス（注意！） |
| `plan` | 計画モード（読み取り専用） |

### Description の書き方

**必須要素**:
1. **何をするか**: 専門分野を明確に述べる
2. **いつ使うか**: 使用タイミングを指示
3. **"use proactively"**: 自動委譲を促すフレーズ

```yaml
# ❌ 悪い例
description: Code reviewer

# ✅ 良い例
description: Expert code review specialist. Proactively reviews code for quality, security, and maintainability. Use immediately after writing or modifying code.
```

### Tools 設定パターン

```yaml
# 読み取り専用レビュアー
tools: Read, Grep, Glob, Bash
disallowedTools: Write, Edit

# 完全なアクセス
tools: Read, Write, Edit, Bash, Grep, Glob

# 特定ツールのみ
tools: Bash, Read
```

### チェックリスト

- [ ] `name`は小文字・ハイフンのみ
- [ ] `description`は詳細（何をするか・いつ使うか・"use proactively"）
- [ ] `tools`は必要最小限（セキュリティと焦点のため）
- [ ] `model`はタスク複雑度に応じて選択
- [ ] システムプロンプトに明確な手順を記載
- [ ] 焦点を絞った単一目的のエージェント（複数の役割を兼ねさせない）
- [ ] プロジェクトエージェントをバージョン管理に含める

---

## Skill

### 配置場所

| 場所 | パス | 適用対象 |
|------|------|---------|
| 個人 | `~/.claude/skills/` | すべてのプロジェクト |
| プロジェクト | `.claude/skills/` | リポジトリメンバー |

### 基本構造

```markdown
---
name: pdf-processor
description: PDFファイルからテキストや表を抽出。「PDF」「抽出」などのキーワードで自動適用。
allowed-tools: Read, Bash
user-invocable: true
---

# PDF処理スキル

## 概要
PDFファイルを処理するスキルです。

## 発動条件
- PDFファイルの処理を依頼された時
- 「PDF」「抽出」などのキーワードが含まれる場合

## 手順
1. ファイルを確認
2. 処理を実行
```

### フロントマターフィールド

| フィールド | 必須 | 説明 |
|-----------|------|------|
| `name` | ✅ | 最大64文字、小文字・数字・ハイフンのみ、予約語不可（anthropic, claude） |
| `description` | ✅ | 最大1024文字、何をするか・いつ使用するか、XMLタグ不可 |
| `allowed-tools` | ❌ | 許可なしで使用できるツール |
| `model` | ❌ | 使用するモデル（sonnet/opus/haiku/inherit） |
| `context` | ❌ | `fork`でサブエージェント実行 |
| `user-invocable` | ❌ | スラッシュメニュー表示（デフォルト: true） |
| `hooks` | ❌ | ライフサイクルフック定義 |

### 段階的開示パターン

**SKILL.mdは500行以下に保つ**。詳細は別ファイルに分離。

```
my-skill/
├── SKILL.md          # 概要とクイックスタート（500行以下）
├── REFERENCE.md      # 詳細リファレンス
├── EXAMPLES.md       # 使用例
└── scripts/          # ユーティリティスクリプト
```

SKILL.md内でリンク：
```markdown
詳細は [REFERENCE.md](REFERENCE.md) を参照してください。
使用例は [EXAMPLES.md](EXAMPLES.md) を参照してください。
```

**重要**: 深くネストされた参照を避ける。SKILL.mdから**1レベル深い参照**を保つ。

### 可視性制御

| 設定 | スラッシュメニュー | 自動検出 | 用途 |
|------|-----------------|---------|------|
| `user-invocable: true`（デフォルト） | 表示 | ○ | ユーザーが明示的に呼び出し可能 |
| `user-invocable: false` | 非表示 | ○ | Claude自動判断のみ |

### ワークフローとフィードバックループ

複雑な操作を明確なステップに分割し、チェックリストを提供：

````markdown
## ワークフロー

このチェックリストをコピーして進行状況を追跡：

```
タスク進捗：
- [ ] ステップ1：フォームを分析する
- [ ] ステップ2：フィールドマッピングを作成する
- [ ] ステップ3：マッピングを検証する
- [ ] ステップ4：フォームに入力する
- [ ] ステップ5：出力を確認する
```
````

**フィードバックループパターン**: バリデータを実行 → エラーを修正 → 繰り返す

### 時間に敏感な情報を避ける

**❌ 悪い例**:
```markdown
2025年8月前にこれを行っている場合は、古いAPIを使用してください。
```

**✅ 良い例**:
```markdown
## 現在の方法
v2 APIエンドポイントを使用

<details>
<summary>レガシーv1 API（2025-08で廃止）</summary>
...
</details>
```

### MCPツール参照

完全修飾ツール名を使用：`ServerName:tool_name`

```markdown
BigQuery:bigquery_schemaツールを使用してテーブルスキーマを取得します。
GitHub:create_issueツールを使用して問題を作成します。
```

### チェックリスト

#### コア品質
- [ ] `name`は小文字・数字・ハイフンのみ（最大64文字）
- [ ] `description`は「何をするか＋いつ使うか＋トリガー用語」を含む（最大1024文字）
- [ ] `description`は三人称で記述
- [ ] `allowed-tools`は必要最小限
- [ ] SKILL.mdボディは**500行以下**
- [ ] 追加の詳細は別ファイルに分離（必要な場合）
- [ ] ファイル参照は**1レベル深い**（深くネストしない）
- [ ] 発動条件が明確に記載されている
- [ ] 時間に敏感な情報がない（または「古いパターン」セクションに）
- [ ] 全体で一貫した用語
- [ ] 例は抽象的ではなく具体的
- [ ] ワークフローに明確なステップがある
- [ ] 段階的開示が適切に使用されている

#### コードとスクリプト（該当する場合）
- [ ] スクリプトは問題を解決し、Claudeに任せない
- [ ] エラー処理は明示的で有用
- [ ] 「マジックナンバー」がない（すべての値が正当化されている）
- [ ] 必要なパッケージが指示にリストされている
- [ ] スクリプトに明確なドキュメントがある
- [ ] Windowsスタイルのパスがない（すべてフォワードスラッシュ）
- [ ] 重要な操作の検証/確認ステップ
- [ ] 品質が重要なタスクにフィードバックループを含む

#### テスト
- [ ] 少なくとも3つの評価シナリオが作成されている
- [ ] Haiku、Sonnet、Opusでテストされている
- [ ] 実際の使用シナリオでテストされている
- [ ] チームフィードバックが組み込まれている（該当する場合）

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

### サブエージェントを使用する場合（詳細）

- タスクが詳細な出力を生成し、メインコンテキストに必要ない
- 特定のツール制限または権限を強制したい
- 作業が自己完結型で、要約を返すことができる
- 大量の操作を分離したい
- 並列研究を実行したい

### メイン会話を使用する場合

- タスクが頻繁なやり取りや反復的な改善が必要
- 複数のフェーズが重要なコンテキストを共有
- 迅速でターゲット化された変更

---

## 参考リンク

- [公式: Custom Slash Commands](https://code.claude.com/docs/ja/slash-commands)
- [公式: Sub-agents](https://code.claude.com/docs/ja/sub-agents)
- [公式: Skills Overview](https://platform.claude.com/docs/ja/agents-and-tools/agent-skills/overview)
- [公式: Skills Best Practices](https://platform.claude.com/docs/ja/agents-and-tools/agent-skills/best-practices)
