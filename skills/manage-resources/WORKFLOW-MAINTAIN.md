# メンテナンスワークフロー

## TodoWrite チェックリスト

**各Phaseの開始時に `in_progress`、完了時に `completed` に更新すること：**

```
メンテナンス進捗：
- [ ] Phase 1: 現状分析
- [ ] Phase 2: 計画立案（Planサブエージェント）
- [ ] Phase 3: ユーザー承認
- [ ] Phase 4: 修正実施
- [ ] Phase 5: 検証と完了報告
```

## Phase 1: 現状分析

**Phase 1開始時**: TodoWriteで「Phase 1」を `in_progress` に更新

### 1-1. 分析スクリプト実行

AI-Toolkitリポジトリの分析スクリプトを実行し、現状を把握する。

**実行コマンド**:
```bash
python3 ~/Documents/Git/ai-toolkit/skills/manage-resources/analyze_prompts.py
```

### 1-2. 分析結果の確認

スクリプト出力から以下を確認する：

```
Phase 1 チェックリスト：
- [ ] summary（ファイル数サマリー）を確認
- [ ] quality_issues（品質問題一覧）を確認
- [ ] refactoring_candidates（リファクタリング候補）を確認
- [ ] reference_map（task参照関係）を確認
```

### 1-3. 責務定義の確認

各リソースタイプの責務を確認し、違反がないかチェックする：

| リソース | 責務 | 違反例 |
|----------|------|--------|
| **Skills** | 自動発火の"入口"（検出→ルーティング） | 具体的な処理ロジックを持ちすぎている |
| **Slash-commands** | 明示実行の"プロダクト機能"（UX窓口） | 再利用可能な手順を直接記述している |
| **Task** | 再利用する"手順ライブラリ"（安定・単機能） | 1箇所からしか呼ばれない / 複数責務を持つ |
| **Agents** | 思考/口調/観点の"モジュール"（工程単位） | 汎用的すぎる / 専門性がない |

**Phase 1完了時**: TodoWriteで「Phase 1」を `completed` に更新

## Phase 2: 計画立案（Planサブエージェント）

**Phase 2開始時**: TodoWriteで「Phase 2」を `in_progress` に更新

### 2-1. Planサブエージェント起動

Taskツールを使用してPlanサブエージェントを起動し、メンテナンス計画を立案させる：

```
AI-Toolkitリポジトリのプロンプトメンテナンス計画を立ててください。

## 現状分析結果
{phase1_analysis_result}

## メンテナンス方針
1. 責務分離の原則に基づくリファクタリング
2. Claude公式ベストプラクティス準拠
3. READMEとの整合性確保

## 出力形式

### 1. 統合候補（task → コマンドに統合）
### 2. 抽出候補（インライン処理 → task化）
### 3. Skills昇格候補
### 4. Agent化候補
### 5. 責務違反の修正
### 6. 品質問題の修正
```

### 2-2. 計画の整理

Planサブエージェントの提案を以下のチェックリストで整理する：

```
Phase 2 チェックリスト：
- [ ] 統合候補（task → コマンドに統合）を特定
- [ ] 抽出候補（インライン処理 → task化）を特定
- [ ] Skills昇格候補を特定
- [ ] Agent化候補を特定
- [ ] 責務違反の修正箇所を特定
- [ ] 品質問題の修正箇所を特定
```

### 2-3. 判断基準の適用

#### Skills昇格の判断基準

| 基準 | 説明 | 重み |
|------|------|------|
| 再利用性 | 複数のコマンドから参照されている | 高 |
| 自動発動適性 | URL・ファイルタイプ・キーワードで発動可能 | 高 |
| 独立性 | 単独で完結するワークフロー | 中 |
| 汎用性 | プロジェクトを跨いで使用可能 | 中 |

#### Agent化の判断基準

| 基準 | 説明 |
|------|------|
| 専門的思考が必要 | 特定ドメインの判断・分析が必要 |
| 独自の観点/口調 | 一貫したペルソナやレビュー観点を持つ |
| コンテキスト分離 | 親タスクと独立して動作すべき |
| 並列実行の利点 | 他の処理と並行して実行できる |

**Phase 2完了時**: TodoWriteで「Phase 2」を `completed` に更新

## Phase 3: ユーザー承認

**Phase 3開始時**: TodoWriteで「Phase 3」を `in_progress` に更新

### 3-1. 計画の提示

Planサブエージェントが作成した計画をユーザーに提示する。

```
## メンテナンス計画

### 1. 統合候補（task → コマンドに統合）
{integration_candidates}

### 2. 抽出候補（インライン処理 → task化）
{extraction_candidates}

### 3. Skills昇格候補
{skills_promotion_candidates}

### 4. Agent化候補
{agent_conversion_candidates}

### 5. 責務違反の修正
{responsibility_violations}

### 6. 品質問題の修正
{quality_issues}

この計画でよろしいですか？修正があればお知らせください。
```

### 3-2. 承認の取得

```
Phase 3 チェックリスト：
- [ ] 計画をユーザーに提示
- [ ] ユーザーからの承認を取得
- [ ] 修正点があれば計画を更新
```

**重要**: 修正は必ずユーザーの承認を得てから実施する。

**Phase 3完了時**: TodoWriteで「Phase 3」を `completed` に更新

## Phase 4: 修正実施

**Phase 4開始時**: TodoWriteで「Phase 4」を `in_progress` に更新

### 4-1. 修正の実行

以下の優先順位で修正を実施する：

```
Phase 4 チェックリスト：
- [ ] 責務違反の修正（アーキテクチャ整合性）
- [ ] 統合（不要ファイル削除でシンプル化）
- [ ] 抽出（重複排除）
- [ ] Skills昇格
- [ ] Agent化
- [ ] 品質問題の修正
```

**優先順位**: 上から順に実施する。

### 4-2. 修正時の注意事項

#### 統合時
- task → コマンドに統合する場合、元のtaskファイルを削除
- 参照元のコマンドファイルを更新
- READMEから削除されたtaskへの参照を除去

#### 抽出時
- 新しいtaskファイルを作成
- 元のコマンドファイルから該当部分を削除し、taskへの参照に置き換え
- READMEに新しいtaskを追加（必要な場合）

#### Skills昇格時
- 新しいSkillディレクトリとSKILL.mdを作成
- 元のコマンド/taskファイルを更新または削除
- README.mdのSkills一覧に追加
- descriptionに自動発動キーワードを含める

#### Agent化時
- 新しいエージェントファイルを作成
- 元のコマンド/taskを更新してエージェント呼び出しに変更
- README.mdのエージェント一覧に追加（必要な場合）

#### 品質問題修正時
- フロントマター形式の修正
- 必須フィールドの追加
- テンプレートとの整合性確保
- 命名規則の適用

**Phase 4完了時**: TodoWriteで「Phase 4」を `completed` に更新

## Phase 5: 検証と完了報告

**Phase 5開始時**: TodoWriteで「Phase 5」を `in_progress` に更新

### 5-1. 検証の実施

```
Phase 5 チェックリスト：
- [ ] 依存関係の再検証（壊れた参照がないか）
- [ ] README記載内容との整合性確認
- [ ] 分析スクリプトの再実行（問題が解消されたか確認）
```

### 5-2. 分析スクリプトの再実行

修正後、再度分析スクリプトを実行して問題が解消されたことを確認する：

```bash
python3 ~/Documents/Git/ai-toolkit/skills/manage-resources/analyze_prompts.py
```

### 5-3. 完了報告

修正内容と結果をユーザーに報告する：

```
## メンテナンス完了

### 実施した修正
- 統合: {integration_summary}
- 抽出: {extraction_summary}
- Skills昇格: {skills_promotion_summary}
- Agent化: {agent_conversion_summary}
- 責務違反修正: {responsibility_fix_summary}
- 品質問題修正: {quality_fix_summary}

### 更新されたファイル
{updated_files_list}

### 削除されたファイル
{deleted_files_list}

### 検証結果
- [OK] 依存関係に問題なし
- [OK] README.mdと整合性あり
- [OK] 分析スクリプトで問題検出なし

### 変更内容の確認
`git diff` で変更内容を確認できます。
```

**Phase 5完了時**: TodoWriteで「Phase 5」を `completed` に更新

## 分析スクリプト参照

メンテナンス時は以下のスクリプトとリファレンスを使用する：

- 分析スクリプト: `~/Documents/Git/ai-toolkit/skills/manage-resources/analyze_prompts.py`
- ベストプラクティス（3ファイル）:
  - スラッシュコマンド: `~/Documents/Git/ai-toolkit/skills/manage-resources/BEST-PRACTICES-COMMAND.md`
  - サブエージェント: `~/Documents/Git/ai-toolkit/skills/manage-resources/BEST-PRACTICES-AGENT.md`
  - Skills: `~/Documents/Git/ai-toolkit/skills/manage-resources/BEST-PRACTICES-SKILL.md`

## 注意事項

- 実際の修正は必ずユーザーの承認を得てから行う
- 大きな変更を行う場合は、段階的に実施することを提案する
- 不明な点がある場合は、推測せずユーザーに確認する
- 修正後は必ず依存関係を検証し、壊れた参照がないか確認する
- README.mdとの整合性を常に保つ
