# 更新ワークフロー

## TodoWrite チェックリスト

**各Phaseの開始時に `in_progress`、完了時に `completed` に更新すること：**

```
更新進捗：
- [ ] Phase 1: タイプ選択と対象リソース選択
- [ ] Phase 2: 現状分析
- [ ] Phase 3: 更新要件の収集
- [ ] Phase 4: 更新計画の作成
- [ ] Phase 5: 更新実行
- [ ] Phase 6: 完了
```

## Phase 1: タイプ選択と対象リソース選択

**Phase 1開始時**: TodoWriteで「Phase 1」を `in_progress` に更新

### 1-1. リソースタイプ選択

ユーザーにリソースタイプを選択させる：

```
どの種類のリソースを更新しますか？

| # | タイプ | 説明 | 配置先 |
|---|--------|------|--------|
| 1 | スラッシュコマンド | `/command` で明示的に呼び出す | commands/{name}.md |
| 2 | サブエージェント | Taskツール経由で専門タスクを委譲 | agents/{name}.md |
| 3 | Skill | Claudeが自動判断で適用 | skills/{name}/SKILL.md |

番号で選択してください。
```

### 1-2. 既存リソース一覧表示

タイプに応じた既存リソース一覧を表示する。

#### スラッシュコマンドの場合

`~/Documents/Git/ai-toolkit/README.md` を読み込み、「## スラッシュコマンド一覧」セクションの表を抽出して表示する：

```
## 既存スラッシュコマンド一覧

（README.mdから抽出した表を表示）

更新したいコマンドの番号またはコマンド名を入力してください。
```

#### サブエージェントの場合

`~/Documents/Git/ai-toolkit/README.md` を読み込み、「## サブエージェント一覧」セクションの表を抽出して表示する：

```
## 既存サブエージェント一覧

（README.mdから抽出した表を表示）

更新したいエージェントの番号または名前を入力してください。
```

#### Skillの場合

`~/Documents/Git/ai-toolkit/README.md` を読み込み、「## Skills一覧」セクションの表を抽出して表示する：

```
## 既存Skill一覧

（README.mdから抽出した表を表示）

更新したいスキルの番号または名前を入力してください。
```

### 1-3. ユーザー選択の受け取り

ユーザーの選択を受け取る。

**Phase 1完了時**: TodoWriteで「Phase 1」を `completed` に更新

## Phase 2: 現状分析

**Phase 2開始時**: TodoWriteで「Phase 2」を `in_progress` に更新

### 2-1. 関連ファイルの読み込み

選択されたリソースの関連ファイルを読み込む。

#### スラッシュコマンドの場合

- スラッシュコマンドファイル: `~/Documents/Git/ai-toolkit/commands/{command_name}.md`

#### サブエージェントの場合

- エージェントファイル: `~/Documents/Git/ai-toolkit/agents/{agent_name}.md`

#### Skillの場合

- スキルファイル: `~/Documents/Git/ai-toolkit/skills/{skill_name}/SKILL.md`

### 2-2. 現状の構造・内容分析

現在の構造・内容を分析し、タイプに応じた形式でユーザーに提示する。

#### スラッシュコマンドの場合

```
## 現在のコマンド構成

### スラッシュコマンド
- allowed-tools: {tools}
- description: {description}
- 役割: {role}

### テンプレート整合性チェック
- [OK/NG] フロントマター形式（---で囲まれている）
- [OK/NG] allowed-toolsが存在する
- [OK/NG] descriptionが存在する
- [OK/NG] 役割セクションが存在する
- [OK/NG] 「日本語で回答すること。」が含まれている
- [OK/NG] 手順セクションが存在する
- [OK/NG] 命名規則（kebab-case）に準拠
```

詳細は [BEST-PRACTICES-COMMAND.md](BEST-PRACTICES-COMMAND.md) を参照。

#### サブエージェントの場合

```
## 現在のエージェント構成

### 基本情報
- name: {name}
- description: {description}
- tools: {tools}
- model: {model}

### 役割
{role_description}

### 入力パラメータ
{input_parameters}

### 実行手順
{steps_summary}

### テンプレート整合性チェック
- [OK/NG] フロントマター形式（---で囲まれている）
- [OK/NG] nameが存在する
- [OK/NG] descriptionが存在する
- [OK/NG] 役割セクションが存在する
- [OK/NG] 実行手順セクションが存在する
- [OK/NG] 出力要件セクションが存在する
- [OK/NG] 命名規則（kebab-case）に準拠
```

詳細は [BEST-PRACTICES-AGENT.md](BEST-PRACTICES-AGENT.md) を参照。

#### Skillの場合

```
## 現在のSkill構成

### 基本情報
- name: {name}
- description: {description}
- allowed-tools: {allowed_tools}

### 発動条件
{trigger_conditions}

### 実行手順
{steps_summary}

### テンプレート整合性チェック
- [OK/NG] フロントマター形式（---で囲まれている）
- [OK/NG] nameが存在する
- [OK/NG] descriptionが存在する（最大1024字）
- [OK/NG] 概要セクションが存在する
- [OK/NG] 発動条件セクションが存在する
- [OK/NG] 手順セクションが存在する
- [OK/NG] 命名規則（kebab-case）に準拠
```

詳細は [BEST-PRACTICES-SKILL.md](BEST-PRACTICES-SKILL.md) を参照。

**Phase 2完了時**: TodoWriteで「Phase 2」を `completed` に更新

## Phase 3: 更新要件の収集

**Phase 3開始時**: TodoWriteで「Phase 3」を `in_progress` に更新

### 3-1. 更新要件のヒアリング

ユーザーに以下を質問する：

```
このリソースをどのように更新したいですか？

以下の情報を教えてください：
- **更新したい点**: 何を変えたいですか？
- **理由**: なぜ変更が必要ですか？
- **期待する結果**: 変更後にどうなってほしいですか？

例: 「手順3の説明が分かりにくいので、より具体的にしたい」
例: 「新しいツールを追加したい」
例: 「発動条件を変更したい」
```

**Phase 3完了時**: TodoWriteで「Phase 3」を `completed` に更新

## Phase 4: 更新計画の作成

**Phase 4開始時**: TodoWriteで「Phase 4」を `in_progress` に更新

### 4-1. Planサブエージェント起動

Taskツールを使用してPlanサブエージェントを起動し、タイプに応じた更新計画を立案させる。

#### スラッシュコマンドの場合

```
ユーザーの更新要件に基づいて、既存コマンドの更新計画を立ててください。

対象コマンド: {command_name}
現在の内容:
{current_content}

ユーザーの更新要件:
{update_requirements}

以下を提案してください：
1. 変更が必要な箇所の特定
2. 具体的な変更内容
3. テンプレートとの整合性確認

参考テンプレート:
- スラッシュコマンド: ~/Documents/Git/ai-toolkit/templates/slash-command-template.md
- タスクファイル: ~/Documents/Git/ai-toolkit/templates/task-template.md
```

#### サブエージェントの場合

```
ユーザーの更新要件に基づいて、既存サブエージェントの更新計画を立ててください。

対象エージェント: {agent_name}
現在の内容:
{current_content}

ユーザーの更新要件:
{update_requirements}

以下を提案してください：
1. 変更が必要な箇所の特定
2. 具体的な変更内容
3. テンプレートとの整合性確認

参考テンプレート:
- サブエージェント: ~/Documents/Git/ai-toolkit/templates/agent-template.md
```

#### Skillの場合

```
ユーザーの更新要件に基づいて、既存Skillの更新計画を立ててください。

対象スキル: {skill_name}
現在の内容:
{current_content}

ユーザーの更新要件:
{update_requirements}

以下を提案してください：
1. 変更が必要な箇所の特定
2. 具体的な変更内容
3. テンプレートとの整合性確認
4. descriptionの変更がある場合、自動発動への影響

参考テンプレート:
- Skill: ~/Documents/Git/ai-toolkit/templates/skill-template.md
```

### 4-2. 変更点の提示

変更点を差分形式でユーザーに提示する。

#### スラッシュコマンドの場合

```
## 更新計画

### 変更概要
{change_summary}

### スラッシュコマンドの変更
ファイル: commands/{command_name}.md

```diff
- 変更前の行
+ 変更後の行
```

### テンプレート整合性
- [OK] 更新後もテンプレートに準拠しています

この更新でよろしいですか？修正があればお知らせください。
```

#### サブエージェントの場合

```
## 更新計画

### 変更概要
{change_summary}

### エージェントファイルの変更
ファイル: agents/{agent_name}.md

```diff
- 変更前の行
+ 変更後の行
```

### テンプレート整合性
- [OK] 更新後もテンプレートに準拠しています

この更新でよろしいですか？修正があればお知らせください。
```

#### Skillの場合

```
## 更新計画

### 変更概要
{change_summary}

### Skillファイルの変更
ファイル: skills/{skill_name}/SKILL.md

```diff
- 変更前の行
+ 変更後の行
```

### 自動発動への影響
{auto_trigger_impact}

### テンプレート整合性
- [OK] 更新後もテンプレートに準拠しています

この更新でよろしいですか？修正があればお知らせください。
```

### 4-3. 修正対応

修正点があれば修正し、承認を得る。

**Phase 4完了時**: TodoWriteで「Phase 4」を `completed` に更新

## Phase 5: 更新実行

**Phase 5開始時**: TodoWriteで「Phase 5」を `in_progress` に更新

### 5-1. ファイル更新

ユーザーの承認後、Editツールでファイルを更新する。

#### スラッシュコマンドの場合
- スラッシュコマンドファイル
- タスクファイル（該当する場合）

#### サブエージェントの場合
- エージェントファイル

#### Skillの場合
- SKILL.mdファイル

### 5-2. 更新内容の最終確認

更新後のファイル内容全体をユーザーに提示し、最終確認を求める。

**Phase 5完了時**: TodoWriteで「Phase 5」を `completed` に更新

## Phase 6: 完了

**Phase 6開始時**: TodoWriteで「Phase 6」を `in_progress` に更新

### 6-1. README更新

descriptionが変更された場合のみREADME.mdを更新する：

- `~/Documents/Git/ai-toolkit/README.md` を読み込む
- スラッシュコマンドの場合: 「## スラッシュコマンド一覧」セクションを更新
- サブエージェントの場合: 該当セクションを更新（存在する場合）
- Skillの場合: 「## Skills一覧」セクションを更新

### 6-2. 更新完了の報告

#### スラッシュコマンドの場合

```
## 更新完了

以下のファイルを更新しました：
- commands/{command_name}.md
- README.md（descriptionが変更された場合）

### コマンドの使用方法
`/{command_name}` で呼び出せます。

### 変更内容の確認
`git diff` で変更内容を確認できます。
```

#### サブエージェントの場合

```
## 更新完了

以下のファイルを更新しました：
- agents/{agent_name}.md
- README.md（descriptionが変更された場合）

### エージェントの使用方法
Taskツールの `subagent_type` に `{agent_name}` を指定して呼び出せます。

### 変更内容の確認
`git diff` で変更内容を確認できます。
```

#### Skillの場合

```
## 更新完了

以下のファイルを更新しました：
- skills/{skill_name}/SKILL.md
- README.md（descriptionが変更された場合）

### スキルの使用方法
発動条件に合致すると自動的に適用されます。

### 変更内容の確認
`git diff` で変更内容を確認できます。
```

### 6-3. 次のステップ

**更新後は必ずメンテナンスワークフローを実行し、整合性を確認すること**
- `/manage-resources` → 「3. メンテナンス」を選択
- または `WORKFLOW-MAINTAIN.md` を参照

**Phase 6完了時**: TodoWriteで「Phase 6」を `completed` に更新

## テンプレート参照

更新時は以下のテンプレートファイルを参照すること：

- スラッシュコマンド: `~/Documents/Git/ai-toolkit/templates/slash-command-template.md`
- タスクファイル: `~/Documents/Git/ai-toolkit/templates/task-template.md`
- サブエージェント: `~/Documents/Git/ai-toolkit/templates/agent-template.md`
- Skill: `~/Documents/Git/ai-toolkit/templates/skill-template.md`

## タスクファイル分離の判断基準（スラッシュコマンドの場合）

以下の場合はタスクファイルを分離して管理する：
- 複数のスラッシュコマンドから参照される共通タスク（例: read-redmine-ticket.md）
- サブタスクとして段階的に実行されるタスク群（例: solve-problem-*.md）

以下の場合はスラッシュコマンドに統合する：
- 1つのスラッシュコマンドからのみ参照されるタスク
- 手順がシンプルで再利用性がないタスク

## 注意事項

- 更新前に必ず現在の内容をユーザーに提示する
- 大幅な構造変更の場合は、新規作成を提案する
- 更新後は `git diff` で変更内容を確認できることを案内する
- 既存のリソースと重複する名前への変更は避ける
- Skillの `description` を変更する場合は、自動発動への影響を説明すること
- 内部で他のタスクファイルやSkillsを参照しているコマンドを更新する場合、参照先も確認すること
- 複数タスクを参照するコマンドの構造を変更する場合は、参照先との整合性を保つこと
