# AI Toolkit

Claude CodeのカスタムスラッシュコマンドやAI活用のためのリソースをまとめたリポジトリです。

## 目的

今後のAI活用において、効率的な開発環境を構築し、再利用可能なリソースを体系的に管理することを目的としています。

## ディレクトリ構成

```
ai-toolkit/
├── .github/
│   └── workflows/     <- GitHub Actions ワークフロー定義
├── slash-commands/    <- Claude Codeのカスタムスラッシュコマンド用
├── skills/            <- Claude Code Skills（自動発動する専門スキル）
├── agents/            <- サブエージェント関連の定義や設定
├── rules/             <- ルールファイルやポリシー、ワークフロー
├── templates/         <- 定型テンプレートファイル、応答フォーマットなど
├── output-style/      <- Claude Codeの出力スタイル設定
├── scripts/           <- 自動化スクリプト（Python等）
├── task/              <- タスク定義ファイル（スラッシュコマンドから参照される詳細な手順）
└── README.md          <- このファイル
```

## Skills一覧

Skillsは、ユーザーの質問に応じて自動的に発動する専門スキルです。スラッシュコマンドとは異なり、明示的な呼び出しなしで適切な場面で自動的に使用されます。

| カテゴリ | スキル名 | 説明 |
|---------|---------|------|
| データ読み取り | `read-google-drive-skill` | Google Driveファイル（スプレッドシート/ドキュメント/スライド）を適切に読み取り。シート名・タブ名・ページ番号指定時は構造確認後に部分読み取り |
| レビュー | `review-document-skill` | GitHub PRまたはGoogle Drive資料を自動レビュー。URLとレビュー依頼キーワードで自動発動 |
| GitHub操作 | `github-cli-skill` | GitHub CLI (gh) を使った Issue/PR 操作ガイド。MCP を使わずコマンドで直接操作するためコンテキスト節約 |
| パーソナライズ | `personal-context-aware-response` | パーソナルコンテキストを考慮した回答を提供。技術的意思決定、振り返り分析、アドバイス依頼などで自動発動し、PREP法による構造化された回答を生成 |
| 目標設定 | `smart-goal-setting` | SMARTフレームワークを活用した目標設定支援。目標設定・KPI策定・OKR作成などの依頼で自動発動し、5観点での分析とリーダー行動計画を提案 |

## サブエージェント一覧

サブエージェントは、Taskツールから呼び出される専門特化したエージェントです。
独立したコンテキスト窓を持ち、特定のタスクに集中して処理を行います。

| カテゴリ | エージェント名 | 説明 | モデル |
|---------|--------------|------|--------|
| Git操作 | `git-workflow-setup` | ブランチ作成、空コミット、プッシュ、PR作成、Redmineコメント追加を自動実行 | haiku |
| コーディング | `code-implementer` | 承認された実装計画に従ってコードを実装、ビルド確認まで実施 | sonnet |
| テスト | `test-writer` | テスト計画の作成、テストコード実装、テスト実行を担当 | haiku |
| テスト | `test-item-generator` | 因子・水準組み合わせに基づくテスト項目書をスプレッドシートに作成 | - |
| 振り返り | `retrospective-reporter` | 指定された資料を読み取り、分析観点に従ってレポートを作成する汎用レポーター | sonnet |
| 問題解決 | `solve-problem-define` | 問題解決Phase 1-2: 問題の定義（What）と所在の特定（Where） | sonnet |
| 問題解決 | `solve-problem-analyze` | 問題解決Phase 3: 原因追及・課題設定（Why） | sonnet |
| 問題解決 | `solve-problem-solution` | 問題解決Phase 4: 解決策立案（How） | sonnet |
| 問題解決 | `solve-problem-planning` | 問題解決Phase 5-6: タスク分解・スケジュール作成 | sonnet |
| 問題解決 | `solve-problem-risk` | 問題解決Phase 7: リスク計画 | sonnet |

## スラッシュコマンド一覧

| カテゴリ | コマンド名 | 説明 |
|---------|-----------|------|
| 振り返り | `/retrospective` | 振り返りスペシャリストとして週次/月次のレトロスペクティブを並列実行 |
| 振り返り | `/retrospective-claude-usage-daily` | Claude Codeセッション分析のスペシャリストとして前日の活動履歴をレポート化 |
| 振り返り | `/retrospective-competency` | コンピテンシー評価のスペシャリストとして前日の活動とノート記録からコンピテンシー評価のエビデンスを抽出 |
| 振り返り | `/retrospective-chipoyo-money` | ちいぽよの金銭管理スペシャリストとして月次の収支分析とアドバイスを実施 |
| 開発・コーディング | `/coding` | モバイルアプリ開発のスペシャリストとして実装タスクを実施（Git ワークフロー・計画含む） |
| 開発・コーディング | `/create-todo-issue` | 開発中に思いついたTODOをGitHub Issueとして素早く登録 |
| 開発・コーディング | `/generate-test-item` | 因子・水準組み合わせに基づくテスト項目書を作成 |
| 開発・コーディング | `/install-apk` | Android端末へのAPKインストールを支援 |
| Git操作 | `/git-force-push` | 現在のブランチを強制プッシュ（確認プロセス付き） |
| Git操作 | `/git-get-code-diff-and-test-coverage` | 指定期間内のコード変更を取得し、変更ファイルのテストカバレッジを計測 |
| MCP・CLI開発 | `/coding-mcp` | MCP開発のスペシャリストとしてサーバー新規作成・ツール追加・ツール更新を実施 |
| MCP・CLI開発 | `/create-command` | カスタムスラッシュコマンド、サブエージェント、Skillsを対話形式で作成 |
| MCP・CLI開発 | `/update-command` | 既存のカスタムスラッシュコマンド、サブエージェント、Skillsを対話形式で更新・改善 |
| メンテナンス | `/maintain-prompts` | AI-Toolkitのプロンプトを責務分離の原則とベストプラクティスに沿ってメンテナンス・リファクタリング |
| 情報収集 | `/fetch-news` | 最新ニュース記事を取得して提供 |
| 情報収集 | `/fetch-web-search-result` | Web検索でヒットした記事を取得して処理 |
| 情報収集 | `/research-play-console-update` | Google Play Consoleの更新情報を収集・調査 |
| 情報収集 | `/check-drive-document-updates` | Google Driveのファイルの変更有無を日付指定で確認 |
| レビュー・問題解決 | `/review-document` | Google Drive文書/シート/スライド、またはGitHub PRを適切にレビュー |
| レビュー・問題解決 | `/solve-problem` | 問題解決のスペシャリストとして7フェーズの構造化された問題解決プロセスをガイド |
| その他 | `/inspire-action` | 退屈な時にユーザーの目標や記録を踏まえて次のアクションを提案 |

## タスクファイル一覧

タスクファイルは、スラッシュコマンドから参照される再利用可能な手順定義です。
1つのスラッシュコマンドからのみ参照されるタスクは、コマンドファイルに統合されています。

| カテゴリ | タスク名 | 説明 |
|---------|---------|------|
| コーディング・実装 | `coding-plan` | Planサブエージェントを使用してコード分析と実現可能性評価を含む実装計画を作成 |
| コーディング・実装 | `coding-english-resources` | スプレッドシートの英語テキストをアプリの言語リソースファイルに追加（日本語ファイルの順序に合わせる） |
| Git・バージョン管理 | `git-create-branch` | [prefix]/[ticket]/[implementation-name]形式でfeatureブランチを作成 |
| Git・バージョン管理 | `git-create-empty-commit` | [prefix]/[title] refs #[ticket]形式で空コミットを作成 |
| Git・バージョン管理 | `git-push-current-branch` | `git push -u origin <branch_name>`で現在のブランチをリモートにプッシュ |
| Git・バージョン管理 | `git-create-pull-request` | テンプレート付きドラフトPRを作成し、Redmine参照を置換してPRリンクをチケットに追加 |
| データ読み取り | `read-google-drive` | シート/タブ指定オプション付きでGoogle Driveスプレッドシートや文書を読み取り |
| データ読み取り | `read-note` | 年間目標と当月進捗タブを含むユーザーのノート文書を読み取り |
| データ読み取り | `read-redmine-ticket` | 提供されたURLからmcp-redmineツールを使用してRedmineチケット詳細を読み取り |
| レビュー | `review-pull-request` | GitHub PRをコード品質・設計・セキュリティ等の観点でレビュー |
| レビュー | `review-google-drive` | Google Drive資料（ドキュメント/スプレッドシート/スライド）をレビュー |
| その他 | `command-validation` | kebab-case命名規則に準拠しているかスラッシュコマンドとタスクファイルをチェック |

## 使用方法

1. 各ディレクトリに適切なファイルを配置
2. Claude Codeでスラッシュコマンドを使用してファイルを参照
3. 必要に応じてテンプレートやルールをプロジェクトに適用
