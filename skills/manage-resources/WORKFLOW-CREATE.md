# 新規作成ワークフロー

## TodoWrite チェックリスト

**各Phaseの開始時に `in_progress`、完了時に `completed` に更新すること：**

```
新規作成進捗：
- [ ] Phase 1: タイプ選択と要件収集
- [ ] Phase 2: 計画立案（Planサブエージェント）
- [ ] Phase 3: ユーザー承認
- [ ] Phase 4: ファイル生成
- [ ] Phase 5: README更新と完了
```

## Phase 1: タイプ選択と要件収集

**Phase 1開始時**: TodoWriteで「Phase 1」を `in_progress` に更新

### 1-1. リソースタイプ選択

ユーザーにリソースタイプを選択させる：

```
どの種類のリソースを作成しますか？

| # | タイプ | 説明 | 配置先 |
|---|--------|------|--------|
| 1 | スラッシュコマンド | `/command` で明示的に呼び出す | commands/{name}.md |
| 2 | サブエージェント | Taskツール経由で専門タスクを委譲 | agents/{name}.md |
| 3 | Skill | Claudeが自動判断で適用 | skills/{name}/SKILL.md |

番号で選択してください。
```

### 1-2. 要件収集

選択されたタイプに応じて質問する。

#### スラッシュコマンドの場合

```
どのようなコマンドを作成したいですか？

以下の情報を教えてください：
- **目的**: このコマンドで何を実現したいですか？
- **背景**: どのような場面で使いたいですか？
- **期待する動作**: AIにどのような作業をさせたいですか？

例: 「PRのコードレビューを効率化したい。レビュー観点に沿ってコードをチェックし、指摘事項をまとめてほしい」
```

詳細は [BEST-PRACTICES-COMMAND.md](BEST-PRACTICES-COMMAND.md) を参照。

#### サブエージェントの場合

```
どのようなサブエージェントを作成したいですか？

以下の情報を教えてください：
- **専門分野**: どのような専門タスクを担当させますか？
- **必要なツール**: どのツールへのアクセスが必要ですか？
- **入力パラメータ**: どのような情報を受け取りますか？
- **出力要件**: 完了時に何を報告しますか？

例: 「コードレビューを担当。Read, Grep, Bashツールを使用。PRの差分を受け取り、問題点と改善提案を報告」
```

詳細は [BEST-PRACTICES-AGENT.md](BEST-PRACTICES-AGENT.md) を参照。

#### Skillの場合

```
どのようなSkillを作成したいですか？

以下の情報を教えてください：
- **目的**: このスキルで何を実現したいですか？
- **発動条件**: どのような状況で自動適用されるべきですか？
- **必要なツール**: どのツールへのアクセスが必要ですか？

例: 「PDFファイルを処理する際に自動適用。フォーム入力やデータ抽出を支援」
```

詳細は [BEST-PRACTICES-SKILL.md](BEST-PRACTICES-SKILL.md) を参照。

**Phase 1完了時**: TodoWriteで「Phase 1」を `completed` に更新

## Phase 2: 計画立案（Planサブエージェント）

**Phase 2開始時**: TodoWriteで「Phase 2」を `in_progress` に更新

### 2-1. Planサブエージェント起動

Taskツールを使用してPlanサブエージェントを起動し、タイプに応じた設計を行わせる。

#### スラッシュコマンドの場合

```
ユーザーの要件に基づいて、カスタムスラッシュコマンドの設計を行ってください。

ユーザー要件:
{user_requirements}

以下を提案してください：
1. コマンド名（kebab-case）
2. コマンドの説明（description）
3. AIの役割
4. 必要なツール（allowed-tools）
5. タスクの詳細手順

既存のコマンドパターンを参考に、実用的な設計を提案してください。
参考ディレクトリ: ~/Documents/Git/ai-toolkit/commands/
```

#### サブエージェントの場合

```
ユーザーの要件に基づいて、サブエージェントの設計を行ってください。

ユーザー要件:
{user_requirements}

以下を提案してください：
1. エージェント名（kebab-case）
2. エージェントの説明（description）- Taskツールでの自動選択に使用
3. 必要なツール（tools）
4. 使用モデル（model）- haiku/sonnet/opus
5. 入力パラメータ
6. 実行手順
7. 出力要件

既存のエージェントパターンを参考に、実用的な設計を提案してください。
参考ディレクトリ: ~/Documents/Git/ai-toolkit/agents/
```

#### Skillの場合

```
ユーザーの要件に基づいて、Skillの設計を行ってください。

ユーザー要件:
{user_requirements}

以下を提案してください：
1. スキル名（kebab-case）
2. スキルの説明（description）- 自動発動の判断に使用（最大1024字）
3. 許可ツール（allowed-tools）
4. 発動条件
5. 実行手順
6. 出力形式

既存のスキルパターンを参考に、実用的な設計を提案してください。
参考ディレクトリ: ~/Documents/Git/ai-toolkit/skills/
```

### 2-2. 設計案の提示

Planサブエージェントの提案をユーザーに提示する。

#### スラッシュコマンドの場合

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

#### サブエージェントの場合

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

#### Skillの場合

```
## Skill設計案

| 項目 | 内容 |
|------|------|
| スキル名 | {skill_name} |
| 説明 | {description} |
| 許可ツール | {allowed_tools} |

### 発動条件
{trigger_conditions}

### 実行手順
{steps}

### 出力形式
{output_format}

この設計でよろしいですか？修正があればお知らせください。
```

### 2-3. 修正対応

修正点があれば修正し、承認を得る。

**Phase 2完了時**: TodoWriteで「Phase 2」を `completed` に更新

## Phase 3: ユーザー承認

**Phase 3開始時**: TodoWriteで「Phase 3」を `in_progress` に更新

ユーザーの最終承認を得る。修正点があれば修正する。

**Phase 3完了時**: TodoWriteで「Phase 3」を `completed` に更新

## Phase 4: ファイル生成

**Phase 4開始時**: TodoWriteで「Phase 4」を `in_progress` に更新

### 4-1. 既存リソースの重複確認

生成前に既存リソースと重複しないか確認する：

- スラッシュコマンド: `~/Documents/Git/ai-toolkit/commands/`
- サブエージェント: `~/Documents/Git/ai-toolkit/agents/`
- Skill: `~/Documents/Git/ai-toolkit/skills/`

### 4-2. ファイル生成

タイプに応じてファイルを生成する。

#### スラッシュコマンドの場合

- タスクファイルを生成する（必要な場合）
  - パス: `~/Documents/Git/ai-toolkit/task/{command_name}.md`
  - テンプレート: `~/Documents/Git/ai-toolkit/templates/task-template.md`
- スラッシュコマンドファイルを生成する
  - パス: `~/Documents/Git/ai-toolkit/commands/{command_name}.md`
  - テンプレート: `~/Documents/Git/ai-toolkit/templates/slash-command-template.md`

#### サブエージェントの場合

- エージェントファイルを生成する
  - パス: `~/Documents/Git/ai-toolkit/agents/{agent_name}.md`
  - テンプレート: `~/Documents/Git/ai-toolkit/templates/agent-template.md`

#### Skillの場合

- スキルディレクトリを作成し、SKILL.mdを生成する
  - パス: `~/Documents/Git/ai-toolkit/skills/{skill_name}/SKILL.md`
  - テンプレート: `~/Documents/Git/ai-toolkit/templates/skill-template.md`

### 4-3. 生成内容の確認

生成したファイルの内容をユーザーに提示し、最終確認を求める。

**Phase 4完了時**: TodoWriteで「Phase 4」を `completed` に更新

## Phase 5: README更新と完了

**Phase 5開始時**: TodoWriteで「Phase 5」を `in_progress` に更新

### 5-1. README更新

パス: `~/Documents/Git/ai-toolkit/README.md`

- スラッシュコマンドの場合: スラッシュコマンド一覧に追加
- サブエージェントの場合: 適切なセクションに追加（必要に応じて新規セクション作成）
- Skillの場合: Skills一覧に追加

### 5-2. 使用方法の説明

作成したリソースの使用方法を説明する。

#### スラッシュコマンドの場合

```
## 作成完了

以下のファイルを作成しました：
- commands/{command_name}.md
- task/{command_name}.md（該当する場合）
- README.mdに追加

### コマンドの使用方法
`/{command_name}` で呼び出せます。
```

#### サブエージェントの場合

```
## 作成完了

以下のファイルを作成しました：
- agents/{agent_name}.md
- README.mdに追加

### エージェントの使用方法
Taskツールの `subagent_type` に `{agent_name}` を指定して呼び出せます。
```

#### Skillの場合

```
## 作成完了

以下のファイルを作成しました：
- skills/{skill_name}/SKILL.md
- README.mdに追加

### スキルの使用方法
発動条件に合致すると自動的に適用されます。
```

### 5-3. 次のステップ

**生成後は必ずメンテナンスワークフローを実行し、整合性を確認すること**
- `/manage-resources` → 「3. メンテナンス」を選択
- または `WORKFLOW-MAINTAIN.md` を参照

**Phase 5完了時**: TodoWriteで「Phase 5」を `completed` に更新

## テンプレート参照

ファイル生成時は以下のテンプレートファイルを参照すること：

- スラッシュコマンド: `~/Documents/Git/ai-toolkit/templates/slash-command-template.md`
- タスクファイル: `~/Documents/Git/ai-toolkit/templates/task-template.md`
- サブエージェント: `~/Documents/Git/ai-toolkit/templates/agent-template.md`
- Skill: `~/Documents/Git/ai-toolkit/templates/skill-template.md`

## 命名規則

- すべての名前: kebab-case（例: `create-command`, `code-reviewer`, `pdf-processor`）
- スラッシュコマンドとタスクファイルは同じ名前にする（タスクファイルがある場合）

## 注意事項

- 既存のリソースと重複しないよう、生成前に該当ディレクトリを確認する
- 生成前に必ずユーザーの承認を得る
- Planサブエージェントには既存のパターンを参考にさせる
- Skillの `description` は自動発動の判断に使用されるため、キーワードを自然な言葉で含めること
