---
name: skill-best-practice
description: Claude Code Skillの作成・設計時にベストプラクティスを提供。「Skill作成」「SKILL.md」「スキルを作りたい」「新しいスキル」「Skill設計」などの文脈で自動適用。descriptionの書き方、allowed-tools設定、発動条件設計、プログレッシブディスクロージャーなどの公式推奨事項を提供。
allowed-tools: Read, Glob
user-invocable: false
---

# Skill ベストプラクティス

Claude Code公式ドキュメントに基づくSkill作成のベストプラクティスです。

## SKILL.mdの基本構造

```markdown
---
name: your-skill-name
description: Brief description of what this Skill does and when to use it
allowed-tools: Read, Grep, Glob
---

# Your Skill Name

## 概要
Provide clear overview of the skill.

## 発動条件
When this skill should be activated.

## 手順
Step-by-step guidance for Claude.

## 出力形式
Expected output format.
```

## フロントマターフィールド

| フィールド | 必須 | 説明 |
|-----------|------|------|
| `name` | ✅ | スキル識別子（小文字、数字、ハイフンのみ、最大64文字） |
| `description` | ✅ | Claudeがスキル適用判断に使う説明文（**最大1024文字**） |
| `allowed-tools` | ❌ | 許可なしで使用できるツール |
| `model` | ❌ | 使用するモデル（sonnet/opus/haiku/inherit） |
| `context` | ❌ | `fork`でサブエージェント実行 |
| `user-invocable` | ❌ | スラッシュメニュー表示（デフォルト: true） |

## Description の書き方（最重要）

Claudeは **descriptionだけ** を読んでスキルを自動選択します。

### ❌ 悪い例
```yaml
description: Helps with documents
```

### ✅ 良い例
```yaml
description: Extract text and tables from PDF files, fill forms, merge documents.
Use when working with PDF files or when the user mentions PDFs, forms, or document extraction.
```

### 必須要素
1. **何をするか**: 具体的なアクション（抽出、入力、マージ）
2. **いつ使うか**: ユーザーが言及するキーワード
3. **トリガー用語**: 発動させたいキーワードを自然に含める

## Allowed-Tools 設定

必要最小限の権限を付与するセキュリティ原則に従う。

```yaml
# 読み取り専用
allowed-tools: Read, Grep, Glob

# 編集可能
allowed-tools: Read, Write, Edit, Bash, Grep, Glob

# 特定パターンのみ許可
allowed-tools: Bash(git:*), Bash(npm test:*)
```

## プログレッシブディスクロージャー

**SKILL.mdは500行以下に保つ**。詳細は別ファイルに分離。

```
my-skill/
├── SKILL.md          # 概要とクイックスタート（500行以下）
├── REFERENCE.md      # 詳細リファレンス
├── EXAMPLES.md       # 使用例
└── scripts/          # ユーティリティスクリプト
```

SKILL.md内でリンクを提供：
```markdown
詳細は [REFERENCE.md](REFERENCE.md) を参照してください。
```

## 可視性制御

| 設定 | スラッシュメニュー | 自動検出 | 用途 |
|------|-----------------|---------|------|
| `user-invocable: true`（デフォルト） | 表示 | ○ | ユーザー呼び出し可 |
| `user-invocable: false` | 非表示 | ○ | Claude自動判断のみ |

## 配置場所

| 場所 | パス | 適用対象 |
|------|------|---------|
| 個人 | `~/.claude/skills/` | すべてのプロジェクト |
| プロジェクト | `.claude/skills/` | リポジトリメンバー |

## チェックリスト

- [ ] nameは小文字・数字・ハイフンのみ（最大64文字）
- [ ] descriptionは具体的なアクション・キーワード・使用タイミングを含む（最大1024文字）
- [ ] allowed-toolsは必要最小限
- [ ] SKILL.mdは500行以下
- [ ] 発動条件が明確

## 参考: 既存スキルの確認

```bash
# プロジェクトのスキル一覧
ls -la .claude/skills/

# 個人のスキル一覧
ls -la ~/.claude/skills/
```
