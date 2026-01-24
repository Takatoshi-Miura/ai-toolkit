# サブエージェント作成ベストプラクティス

サブエージェントの作成に関する公式ベストプラクティスをまとめたリファレンスです。

## 目次

1. [共通原則](#共通原則)
2. [サブエージェント](#サブエージェント)
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

## 要件収集テンプレート

サブエージェント作成時は、以下の情報を収集してください：

```
どのようなサブエージェントを作成したいですか？

以下の情報を教えてください：
- **専門分野**: どのような専門タスクを担当させますか？
- **必要なツール**: どのツールへのアクセスが必要ですか？
- **入力パラメータ**: どのような情報を受け取りますか？
- **出力要件**: 完了時に何を報告しますか？

例: 「コードレビューを担当。Read, Grep, Bashツールを使用。PRの差分を受け取り、問題点と改善提案を報告」
```

---

## 設計案提示フォーマット

ユーザーとの確認時は、以下のフォーマットで提示してください：

```
## サブエージェント設計案

| 項目 | 内容 |
|------|------|
| エージェント名 | {agent_name} |
| 説明 | {description} |
| ツール | {tools} |
| モデル | {model} |

### 入力パラメータ
{input_parameters}

### 実行手順
{steps}

### 出力要件
{output_requirements}

この設計でよろしいですか？修正があればお知らせください。
```

---

## 参考リンク

- [公式: Sub-agents](https://code.claude.com/docs/ja/sub-agents)
