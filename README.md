# AI Toolkit

Claude CodeのカスタムスラッシュコマンドやAI活用のためのリソースをまとめたリポジトリです。

## 目的

今後のAI活用において、効率的な開発環境を構築し、再利用可能なリソースを体系的に管理することを目的としています。

## ディレクトリ構成

```
ai-toolkit/
├── .github/
│   └── workflows/     <- GitHub Actions ワークフロー定義
├── commands/          <- Claude Codeのカスタムスラッシュコマンド用
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
| データ読み取り | `read-google-drive-skill` | Google Driveファイル（スプレッドシート/ドキュメント/スライド）を読み取り。チェックリスト形式のワークフローでURL解析から結果確認まで実行。部分読み取り対応 |
| データ書き込み | `write-google-drive-skill` | Google Driveファイル（スプレッドシート/ドキュメント/スライド）への書き込み。値挿入、シート/スライド作成、要素コピー、セル結合に対応。Pythonスクリプトで実行 |
| データ読み取り | `read-redmine-skill` | RedmineチケットのURLから詳細情報を自動読み取り。URLとチケット確認キーワードで自動発動 |
| レビュー | `review-document-skill` | GitHub PRまたはGoogle Drive資料を自動レビュー。URLとレビュー依頼キーワードで自動発動 |
| レビュー | `android-code-review` | Androidプロジェクト専用のコードレビュー。PRや差分にAndroidファイル（.kt/.java/.xml）が含まれる場合に自動発動し、ライフサイクル・状態管理・パフォーマンス等のAndroid固有観点で包括的にレビュー |
| GitHub操作 | `github-cli-skill` | GitHub CLI (gh) を使った Issue/PR 操作ガイド。MCP を使わずコマンドで直接操作するためコンテキスト節約 |
| パーソナライズ | `personal-context-aware-response` | パーソナルコンテキストを考慮した回答を提供。技術的意思決定、振り返り分析、アドバイス依頼などで自動発動し、PREP法による構造化された回答を生成 |
| 目標設定 | `smart-goal-setting` | SMARTフレームワークを活用した目標設定支援。目標設定・KPI策定・OKR作成などの依頼で自動発動し、5観点での分析とリーダー行動計画を提案 |
| メンテナンス・ベストプラクティス | `maintain-prompts` | AI-Toolkitのプロンプトをメンテナンス・リファクタリング。スラッシュコマンド・Skill・サブエージェント作成時にClaude公式ベストプラクティスも自動提供（$ARGUMENTS、description、model選択基準など） |
| 振り返り | `retrospective` | 週次/月次のレトロスペクティブを実行。LifeGraph、日次記録、金銭データを分析してレポート作成。「振り返り」「レトロスペクティブ」などで自動発動 |
| 開発・コーディング | `coding` | モバイルアプリ開発の実装タスクを統括するオーケストレーター。情報収集からGit準備、実装計画、コード実装、テストまでの一連のワークフローを専門サブエージェントを活用して進行 |

## サブエージェント一覧

サブエージェントは、Taskツールから呼び出される専門特化したエージェントです。
独立したコンテキスト窓を持ち、特定のタスクに集中して処理を行います。

| カテゴリ | エージェント名 | 説明 | モデル |
|---------|--------------|------|--------|
| Git操作 | `git-workflow-setup` | ブランチ作成、空コミット、プッシュ、PR作成、Redmineコメント追加を自動実行 | haiku |
| コーディング | `code-implementer` | 承認された実装計画に従ってコードを実装、ビルド確認まで実施 | sonnet |
| テスト | `test-writer` | テスト計画の作成、テストコード実装、テスト実行を担当 | haiku |
| テスト | `test-item-generator` | 因子・水準組み合わせに基づくテスト項目書をスプレッドシートに作成（MCPツール版） | - |
| テスト | `test-item-writer` | 因子・水準組み合わせに基づくテスト項目書をスプレッドシートに作成（Pythonスクリプト版、MCP不使用） | sonnet |
| 問題解決 | `solve-problem-executor` | 問題解決Phase 1-7: 全フェーズを一括実行 | sonnet |
| 問題解決 | `solve-problem-define` | 問題解決Phase 1-2: 問題の定義（What）と所在の特定（Where） | sonnet |
| 問題解決 | `solve-problem-analyze` | 問題解決Phase 3: 原因追及・課題設定（Why） | sonnet |
| 問題解決 | `solve-problem-solution` | 問題解決Phase 4: 解決策立案（How） | sonnet |
| 問題解決 | `solve-problem-planning` | 問題解決Phase 5-6: タスク分解・スケジュール作成 | sonnet |
| 問題解決 | `solve-problem-risk` | 問題解決Phase 7: リスク計画 | sonnet |

## スラッシュコマンド一覧

| カテゴリ | コマンド名 | 説明 |
|---------|-----------|------|
| 振り返り | `/retrospective-chipoyo-money` | ちいぽよの金銭管理スペシャリストとして月次の収支分析とアドバイスを実施 |
| 開発・コーディング | `/create-todo-issue` | 開発中に思いついたTODOをGitHub Issueとして素早く登録 |
| 開発・コーディング | `/generate-test-item` | 因子・水準組み合わせに基づくテスト項目書を作成 |
| 開発・コーディング | `/install-apk` | Android端末へのAPKインストールを支援 |
| Git操作 | `/git-force-push` | 現在のブランチを強制プッシュ（確認プロセス付き） |
| Git操作 | `/git-get-code-diff-and-test-coverage` | 指定期間内のコード変更を取得し、変更ファイルのテストカバレッジを計測 |
| MCP・CLI開発 | `/coding-mcp` | MCP開発のスペシャリストとしてサーバー新規作成・ツール追加・ツール更新を実施 |
| MCP・CLI開発 | `/create-command` | カスタムスラッシュコマンド、サブエージェント、Skillsを対話形式で作成 |
| MCP・CLI開発 | `/update-command` | 既存のカスタムスラッシュコマンド、サブエージェント、Skillsを対話形式で更新・改善 |
| 情報収集 | `/fetch-news` | 最新ニュース記事を取得して提供 |
| 情報収集 | `/fetch-web-search-result` | Web検索でヒットした記事を取得して処理 |
| 情報収集 | `/research-play-console-update` | Google Play Consoleの更新情報を収集・調査 |
| 情報収集 | `/check-drive-document-updates` | Google Driveのファイルの変更有無を日付指定で確認 |
| レビュー・問題解決 | `/solve-problem` | 問題解決のスペシャリストとして7フェーズの構造化された問題解決プロセスをガイド |

## タスクファイル一覧

タスクファイルは、スラッシュコマンドから参照される再利用可能な手順定義です。
1つのスラッシュコマンドからのみ参照されるタスクは、コマンドファイルに統合されています。

| カテゴリ | タスク名 | 説明 |
|---------|---------|------|
| コーディング・実装 | `coding-english-resources` | スプレッドシートの英語テキストをアプリの言語リソースファイルに追加（日本語ファイルの順序に合わせる） |

## 使用方法

1. 各ディレクトリに適切なファイルを配置
2. Claude Codeでスラッシュコマンドを使用してファイルを参照
3. 必要に応じてテンプレートやルールをプロジェクトに適用
