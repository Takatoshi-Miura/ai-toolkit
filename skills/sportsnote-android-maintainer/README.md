# sportsnote-android-maintainer（sportsnote-android-maintainer）

## 1. 概要

- **何をするスキルか**: SportsNote Android（`/Users/it6210/Documents/Git/SportsNote_Android`）の開発・保守を無人実行するオーケストレーター。コード調査によるdoc/仕様書の更新（ナレッジ蓄積）、5観点（不具合・ユーザー要望・リファクタリング候補・ドキュメント不足・テスト不足）からのissue起票（issue作成）、issueの選択から実装・クロスレビュー・PR作成まで（実装）の3フローを提供する。
- **発動条件**:
  - 自動発動キーワード: なし（`disable-model-invocation: true`のため明示呼び出しのみ）
  - スラッシュ呼び出し: `/sportsnote-android-maintainer` で可能
  - 自動発動: なし（明示呼び出しのみ）
- **依存の有無**: `gh`（GitHub CLI、ログイン済み必須）、SportsNote_Androidリポジトリのローカルクローン、Gradle（`./gradlew`、リポジトリに同梱のwrapperを使用）
- **想定する利用シーン**: Claudeデスクトップの「ローカルルーチン」機能から、3つのフローがそれぞれ独立して定期的に呼び出される想定（無人実行）。

## 2. 事前準備（セットアップ）

- `gh auth status`でGitHub CLIにログイン済みであることを確認する（アカウント: `Takatoshi-Miura`、リポジトリ: `Takatoshi-Miura/SportsNote_Android`）
- SportsNote_Androidリポジトリが`/Users/it6210/Documents/Git/SportsNote_Android`にクローンされていること
- issueラベル`refactor`・`test`・`needs-manual-follow-up`は未作成でも問題ない。WORKFLOW-ISSUE.md初回実行時に自動作成される（[references/LABEL-TAXONOMY.md](references/LABEL-TAXONOMY.md)参照）
- `doc/spec/`ディレクトリはリポジトリに未作成の状態からスタートする。WORKFLOW-KNOWLEDGE.md初回実行時に`00_overview.md`から自動作成される

## 3. 使い方

- **呼び出し方法**: `/sportsnote-android-maintainer` での明示呼び出し、または以下3種の依頼文言で自動判定（Phase 1のフロー判定表に対応）
  - ナレッジ蓄積: 「ナレッジ蓄積フローを実行して」「doc更新して」等
  - issue作成: 「issue作成フローを実行して」「issue棚卸しして」等
  - 実装: 「実装フローを実行して」「issueを片付けて」等
- **入力例**:
  - `input/requests.md`: ユーザーが自由記述で要望を書き溜める（issue作成フローが取り込む）
  - `input/feedback.md`: スキルの動作に対するフィードバックを自由記述で書き溜める（各フローが反映を試みる）
- **出力例**:
  - ナレッジ蓄積: `doc/spec/*.md`・`CLAUDE.md`の更新（作業ブランチ上でコミットし、mainにローカルマージ・push後、作業ブランチを削除。PRは作成しない）
  - issue作成: GitHub issue（`Takatoshi-Miura/SportsNote_Android`）の新規作成
  - 実装: 実装ブランチのプッシュ・GitHub PRの作成（マージはしない）
  - 各フロー共通: [references/history.md](references/history.md)に実行履歴を追記
- **手順**:
  1. SKILL.mdのPhase 1でどのフローかを判定
  2. [WORKFLOW-KNOWLEDGE.md](WORKFLOW-KNOWLEDGE.md) / [WORKFLOW-ISSUE.md](WORKFLOW-ISSUE.md) / [WORKFLOW-IMPLEMENT.md](WORKFLOW-IMPLEMENT.md) のいずれかのPhase構成に従い最後まで実行
  3. 承認待ちで停止せず、成果物は確定情報として直接反映される
- **使う際のテクニック・コツ**:
  - `doc/spec/`が未作成のため、初回はナレッジ蓄積フローを実行すると`00_overview.md`が自動作成される。その後は`model/` → `viewModel/` → `ui/` → `model/manager/` → `doc/spec/整合性`の順にローテーション調査される
  - 3フローはローカルルーチンから独立して呼ばれる前提のため、ナレッジ蓄積を先に何度か回してから issue作成→実装を回すと、issueの質（doc/CLAUDE.mdとの整合性）が上がる
  - 実装フローはissueが0件だと即終了する。issueが枯渇しないよう、issue作成フローを定期的に回す
  - リポジトリのテストディレクトリ（`app/src/test/`・`app/src/androidTest/`）は現状空のため、実装フローは既存テストがある場合のみ`./gradlew test`を必須完了条件にする（テスト不足issueの対応時は新規テスト追加が必須）
  - 実装フローが選んだissueの対応方針が具体化できない（旧形式のissue等）場合、そのissueは自動的にスキップされ次点issueに切り替わる。対応方針・完了条件チェックリストのないissueが多いと実装フローが空振りしやすいため、issue作成フローで新規作成したissue（対応方針付き）を優先的に消化させるとよい

## 4. 保守・拡張ガイド

### ファイル構成

| ファイル | 役割 |
|---------|------|
| SKILL.md | 起動インターフェース。Todo登録とフロー判定のみ |
| WORKFLOW-KNOWLEDGE.md | ナレッジ蓄積フロー（コード調査→doc/CLAUDE.md更新。初回は`doc/spec/00_overview.md`自動作成を含む） |
| WORKFLOW-ISSUE.md | issue作成フロー（5観点の調査→issue起票） |
| WORKFLOW-IMPLEMENT.md | 実装フロー（issue選択→実装→クロスレビュー→PR作成） |
| references/LABEL-TAXONOMY.md | issueラベル体系の定義 |
| references/ISSUE-CRITERIA.md | issue作成フローの観点別調査手順・判定基準 |
| references/PRIORITY-RULES.md | 実装フローのissue選択優先度・ラベル別対応分岐・連続スキップ検知 |
| references/REVIEW-GUIDE.md | クロスレビューサブエージェントの起動プロンプト設計 |
| references/review-insights.md | レビュー観点ナレッジの蓄積（自己改善ループ、初期状態は空） |
| references/knowledge-map.md | ナレッジ蓄積フローのスキャン対象ローテーション管理 |
| references/history.md | 3フロー共通の実行履歴（初期状態は空） |
| input/requests.md | ユーザー自由記述の要望 |
| input/feedback.md | ユーザーフィードバック蓄積 |

### 修正時の手順と注意点

- `description`を変更すると自動発動の挙動（現状は`disable-model-invocation: true`で自動発動なし）が変わるため、変更時は意図を確認する
- issueラベルの追加・変更時は[references/LABEL-TAXONOMY.md](references/LABEL-TAXONOMY.md)と[references/ISSUE-CRITERIA.md](references/ISSUE-CRITERIA.md)の両方を更新する（対応表が2箇所に分かれているため）
- issue選択の優先度ロジックを変更する場合は[references/PRIORITY-RULES.md](references/PRIORITY-RULES.md)のみを編集すればよい（他ファイルからは参照のみ）
- `references/review-insights.md`が100行を超えたら、古い指摘を1行要約に圧縮する（[references/REVIEW-GUIDE.md](references/REVIEW-GUIDE.md)の肥大化対策を参照）
- テストディレクトリにテストが蓄積され「テスト文化が未確立」でなくなった場合、WORKFLOW-IMPLEMENT.mdのPhase 4完了条件（テスト実行を必須にしない条件分岐）を見直す

### 依存

- ツール: `Read, Write, Edit, Bash, Agent, TodoWrite, Glob, Grep`
- 外部コマンド（Bash経由で実行）: `gh`（GitHub CLI）、`./gradlew`（assembleDebug/test/ktlintFormat/ktlintCheck）

### 動作確認・テスト方法

- `/sportsnote-android-maintainer`を呼び出し、「ナレッジ蓄積フローを実行して」と依頼し、Phase 1のフロー判定が正しく[WORKFLOW-KNOWLEDGE.md](WORKFLOW-KNOWLEDGE.md)に分岐すること、初回は`doc/spec/00_overview.md`が承認なしで作成されることを確認する
- 「issue作成フローを実行して」と依頼し、GitHub上に対応方針・完了条件チェックリスト付きのissueが作成されることを確認する
- 「実装フローを実行して」と依頼し、issueが0件の場合に即終了すること、1件以上ある場合は優先度ロジックに従って選択されPRが作成されることを確認する
