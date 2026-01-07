# AI Toolkit

Claude CodeのカスタムスラッシュコマンドやAI活用のためのリソースをまとめたリポジトリです。

## 目的

今後のAI活用において、効率的な開発環境を構築し、再利用可能なリソースを体系的に管理することを目的としています。

## ディレクトリ構成

```
ai-toolkit/
├── .github/
│   └── workflows/     <- GitHub Actions ワークフロー定義
├── slash-commands/     <- Claude Codeのカスタムスラッシュコマンド用
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

## スラッシュコマンド一覧

| カテゴリ | コマンド名 | 説明 |
|---------|-----------|------|
| 振り返り | `/retrospective-weekly` | 振り返りスペシャリストとして週次レトロスペクティブを実施（時間管理・日次記録分析） |
| 振り返り | `/retrospective-monthly` | 振り返りスペシャリストとして月次レトロスペクティブを実施（時間管理・家計・日次記録分析） |
| 振り返り | `/retrospective-yearly` | 振り返りスペシャリストとして年次レトロスペクティブを実施（時間管理・家計・日次記録・年間目標達成度分析） |
| 振り返り | `/retrospective-claude-usage-daily` | Claude Codeセッション分析のスペシャリストとして前日の活動履歴をレポート化 |
| 振り返り | `/retrospective-competency` | コンピテンシー評価のスペシャリストとして前日の活動とノート記録からコンピテンシー評価のエビデンスを抽出 |
| 振り返り | `/retrospective-chipoyo-money` | ちいぽよの金銭管理スペシャリストとして月次の収支分析とアドバイスを実施 |
| 開発・コーディング | `/coding` | モバイルアプリ開発のスペシャリストとして実装タスクを実施（Git ワークフロー・計画含む） |
| 開発・コーディング | `/create-todo-issue` | 開発中に思いついたTODOをGitHub Issueとして素早く登録 |
| 開発・コーディング | `/generate-test-item` | 因子・水準組み合わせに基づくテスト項目書を作成 |
| 開発・コーディング | `/install-apk` | Android端末へのAPKインストールを支援 |
| Git操作 | `/git-force-push` | 現在のブランチを強制プッシュ（確認プロセス付き） |
| Git操作 | `/git-get-code-diff-and-test-coverage` | 指定期間内のコード変更を取得し、変更ファイルのテストカバレッジを計測 |
| MCP・CLI開発 | `/create-mcp-server` | 要件に基づくMCPサーバを構築 |
| MCP・CLI開発 | `/add-mcp-tool` | 既存のMCPサーバに新しいMCPツールを追加 |
| MCP・CLI開発 | `/update-mcp-tool` | 既存のMCPサーバー内のMCPツールを修正・改善 |
| MCP・CLI開発 | `/create-command` | カスタムスラッシュコマンド、サブエージェント、Skillsを対話形式で作成 |
| MCP・CLI開発 | `/update-command` | 既存のカスタムスラッシュコマンド、サブエージェント、Skillsを対話形式で更新・改善 |
| 情報収集 | `/fetch-news` | 最新ニュース記事を取得して提供 |
| 情報収集 | `/fetch-web-search-result` | Web検索でヒットした記事を取得して処理 |
| 情報収集 | `/research-play-console-update` | Google Play Consoleの更新情報を収集・調査 |
| 情報収集 | `/check-drive-document-updates` | Google Driveのファイルの変更有無を日付指定で確認 |
| レビュー・問題解決 | `/review-document` | Google Drive文書/シート/スライド、またはGitHub PRを適切にレビュー |
| レビュー・問題解決 | `/solve-problem` | 問題解決のスペシャリストとして7フェーズの構造化された問題解決プロセスをガイド |
| その他 | `/auto-task` | ユーザーの要望を分析し、適切なタスクを自動選択して実行 |
| その他 | `/inspire-action` | 退屈な時にユーザーの目標や記録を踏まえて次のアクションを提案 |
| その他 | `/create-release-handbook` | リリース作業のハンドブックを作成 |

## タスクファイル一覧

タスクファイルは、スラッシュコマンドから参照される再利用可能な手順定義です。
1つのスラッシュコマンドからのみ参照されるタスクは、コマンドファイルに統合されています。

| カテゴリ | タスク名 | 説明 |
|---------|---------|------|
| 振り返り | `retrospective-common` | 振り返りタスク共通の前提条件 |
| 振り返り | `retrospective-analyze-lifegraph` | LifeGraphデータを読み取り、時間の使い方を分析してレポート作成 |
| 振り返り | `retrospective-analyze-money` | 金銭管理データを読み取り、収支・予算・住宅ローン試算を分析（月次・年次） |
| 振り返り | `retrospective-analyze-daily` | 日々の振り返りノートを読み取り、カテゴリ別に分析してレポート作成 |
| 振り返り | `retrospective-analyze-yearly-goals` | 年間目標の達成度を分析し、カテゴリ別の成長と課題をレポート作成（年次のみ） |
| 振り返り | `retrospective-claude-usage-daily` | history.jsonlから前日のClaude Code利用状況を抽出・分析してレポート作成 |
| 振り返り | `retrospective-analyze-chipoyo-money` | ちいぽよの金銭管理データを読み取り、月次の収支を分析してレポート作成 |
| 振り返り | `retrospective-competency` | 前日のClaude Code使用履歴とノート記録をコンピテンシー評価基準に照らし合わせ、エビデンスをレポート化 |
| コーディング・実装 | `coding-plan` | Planサブエージェントを使用してコード分析と実現可能性評価を含む実装計画を作成 |
| コーディング・実装 | `coding-implementation` | 計画に従って実装、ビルド、テスト作成（必要に応じて）、動作確認 |
| コーディング・実装 | `coding-english-resources` | スプレッドシートの英語テキストをアプリの言語リソースファイルに追加（日本語ファイルの順序に合わせる） |
| Git・バージョン管理 | `git-create-branch` | [prefix]/[ticket]/[implementation-name]形式でfeatureブランチを作成 |
| Git・バージョン管理 | `git-create-empty-commit` | [prefix]/[title] refs #[ticket]形式で空コミットを作成 |
| Git・バージョン管理 | `git-push-current-branch` | `git push -u origin <branch_name>`で現在のブランチをリモートにプッシュ |
| Git・バージョン管理 | `git-create-pull-request` | テンプレート付きドラフトPRを作成し、Redmine参照を置換してPRリンクをチケットに追加 |
| 問題解決 | `solve-problem` | 問題定義からリスク計画まで7フェーズの問題解決プロセス全体を実行 |
| 問題解決 | `solve-problem-define` | フェーズ1-2: 問題の定義(What)と発生箇所の特定(Where) |
| 問題解決 | `solve-problem-analyze` | フェーズ3: 5-Why法による根本原因の掘り下げ(Why)とタスク設定 |
| 問題解決 | `solve-problem-solution` | フェーズ4: 解決策のブレインストーミングと評価基準に基づく最適案選択 |
| 問題解決 | `solve-problem-planning` | フェーズ5-6: 解決策をタスクに分解し、マイルストーン付き実行スケジュールを作成 |
| 問題解決 | `solve-problem-risk` | フェーズ7: リスク特定、予防・軽減策の定義、トリガー設定 |
| データ読み取り | `read-google-drive` | シート/タブ指定オプション付きでGoogle Driveスプレッドシートや文書を読み取り |
| データ読み取り | `read-life-graph` | LifeGraphスプレッドシートのGoogleカレンダー集計シートを読み取り |
| データ読み取り | `read-money-sheet` | 予算・マネープランシートを含む家計管理スプレッドシートを読み取り |
| データ読み取り | `read-note` | 年間目標と当月進捗タブを含むユーザーのノート文書を読み取り |
| データ読み取り | `read-redmine-ticket` | 提供されたURLからmcp-redmineツールを使用してRedmineチケット詳細を読み取り |
| レビュー | `review-pull-request` | GitHub PRをコード品質・設計・セキュリティ等の観点でレビュー |
| レビュー | `review-google-drive` | Google Drive資料（ドキュメント/スプレッドシート/スライド）をレビュー |
| その他 | `command-validation` | kebab-case命名規則に準拠しているかスラッシュコマンドとタスクファイルをチェック |
| その他 | `inspire-action` | 4カテゴリから次のアクションを提案: 目標達成・業務効率・リフレッシュ・余暇(1時間圏内) |
| その他 | `calendar-register-schedule` | イベントタイプに基づく色分けでGoogleカレンダーにイベントを登録(仕事・アイデア・生活・スキル・コード・本など) |

## 使用方法

1. 各ディレクトリに適切なファイルを配置
2. Claude Codeでスラッシュコマンドを使用してファイルを参照
3. 必要に応じてテンプレートやルールをプロジェクトに適用
