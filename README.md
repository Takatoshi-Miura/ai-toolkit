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
├── rules/             <- ルールファイル（~/.claude/rules/に同期、paths指定で条件適用）
├── templates/         <- 定型テンプレートファイル、応答フォーマットなど
├── output-style/      <- Claude Codeの出力スタイル設定
├── scripts/           <- 自動化スクリプト（Python等）
└── README.md          <- このファイル
```

## Skills一覧

Skillsは、ユーザーの質問に応じて自動的に発動する専門スキルです。スラッシュコマンドとは異なり、明示的な呼び出しなしで適切な場面で自動的に使用されます。

| カテゴリ | スキル名 | 説明 | 自動呼び出し |
|---------|---------|------|:------------:|
| データ読み取り | `read-google-drive-skill` | Google Driveファイル（スプレッドシート/ドキュメント/スライド）を読み取り。チェックリスト形式のワークフローでURL解析から結果確認まで実行。部分読み取り対応 | ✅ |
| データ書き込み | `write-google-drive-skill` | Google Driveファイル（スプレッドシート/ドキュメント/スライド）への書き込み。値挿入、シート/スライド作成、要素コピー、セル結合に対応。Pythonスクリプトで実行 | ✅ |
| データ読み取り | `read-redmine-skill` | RedmineチケットのURLから詳細情報を自動読み取り。URLとチケット確認キーワードで自動発動 | ✅ |
| レビュー | `review-document-skill` | GitHub PRまたはGoogle Drive資料を自動レビュー。URLとレビュー依頼キーワードで自動発動 | ✅ |
| レビュー | `android-code-review` | Androidプロジェクト専用のコードレビュー。PRや差分にAndroidファイル（.kt/.java/.xml）が含まれる場合に自動発動し、ライフサイクル・状態管理・パフォーマンス等のAndroid固有観点で包括的にレビュー | ✅ |
| GitHub操作 | `github-cli-skill` | GitHub CLI (gh) を使った Issue/PR 操作ガイド。MCP を使わずコマンドで直接操作するためコンテキスト節約 | ✅ |
| Git操作 | `git-pr-setup` | ブランチ作成からPR作成までのGitワークフローを自動化。空コミット、プッシュ、ドラフトPR作成、Redmineコメント追加を一括処理。Pythonスクリプトで完全独立 | ✅ |
| パーソナライズ | `personal-context-aware-response` | パーソナルコンテキストを考慮した回答を提供。技術的意思決定、振り返り分析、アドバイス依頼などで自動発動し、PREP法による構造化された回答を生成 | ✅ |
| 目標設定 | `smart-goal-setting` | SMARTフレームワークを活用した目標設定支援。目標設定・KPI策定・OKR作成などの依頼で自動発動し、5観点での分析とリーダー行動計画を提案 | ✅ |
| リソース管理 | `manage-resources` | Claude Codeリソース(スラッシュコマンド、サブエージェント、Skills)の新規作成・更新・メンテナンス・同期を統括。条件分岐で操作タイプ選択後、適切なワークフローに誘導。ai-toolkitの変更を~/.claude/に一方向同期する機能も含む | ✅ |
| 振り返り | `retrospective` | 週次/月次のレトロスペクティブを実行。LifeGraph、日次記録、金銭データを分析してレポート作成。「振り返り」「レトロスペクティブ」などで自動発動 | ❌ |
| 振り返り | `retrospective-agent-team` | エージェントチームを活用した振り返り。LifeGraph・日次記録・金銭データを複数メンバーで並行分析し、クロスリファレンスによる深い洞察を含むレポートを作成 | ❌ |
| レビュー・問題解決 | `solve-problem` | 問題解決のスペシャリストとして7フェーズ（問題定義、所在特定、原因追及、解決策立案、タスク分解、スケジュール、リスク計画）の構造化プロセスで、現状とあるべき姿のギャップを分析し実行可能な解決策を策定 | ❌ |
| 開発・コーディング | `coding` | モバイルアプリ開発の実装タスクを統括するオーケストレーター。情報収集から実装計画、コード実装、テストまでの一連のワークフローを専門サブエージェントを活用して進行 | ❌ |
| テスト | `generate-test-item-skill` | 因子水準組み合わせに基づくテスト項目書を作成。Pythonスクリプトでペアワイズ法を適用し、効率的なテストケースを生成 | ❌ |
| ユーティリティ | `extract-pdf-images` | PDFファイルから画像を抽出して~/Downloads/に保存。pdfimagesコマンドを使用し、単一/複数PDF一括変換に対応。抽出後に各画像のサイズも報告 | ✅ |
| ユーティリティ | `check-drive-document-updates-skill` | Google Driveファイルの変更有無を日付指定で確認。TARGET_FILES.mdで監視対象を管理し、指定日以降の更新をチェック | ✅ |


## サブエージェント一覧

サブエージェントは、Taskツールから呼び出される専門特化したエージェントです。
独立したコンテキスト窓を持ち、特定のタスクに集中して処理を行います。

| カテゴリ | エージェント名 | 説明 | モデル |
|---------|--------------|------|--------|
| コーディング | `code-implementer` | 承認された実装計画に従ってコードを実装、ビルド確認まで実施 | sonnet |
| テスト | `test-writer` | テスト計画の作成、テストコード実装、テスト実行を担当 | haiku |
| テスト | `test-item-writer` | 因子・水準組み合わせに基づくテスト項目書をスプレッドシートに作成（Pythonスクリプト版） | sonnet |
| 問題解決 | `solve-problem-executor` | 問題解決Phase 1-7: 全フェーズを一括実行 | sonnet |

## スラッシュコマンド一覧

| カテゴリ | コマンド名 | 説明 |
|---------|-----------|------|
| 振り返り | `/retrospective-chipoyo-money` | ちいぽよの金銭管理スペシャリストとして月次の収支分析とアドバイスを実施 |
| 開発・コーディング | `/create-todo-issue` | 開発中に思いついたTODOをGitHub Issueとして素早く登録 |
| 開発・コーディング | `/install-apk` | Android端末へのAPKインストールを支援 |
| Git操作 | `/git-force-push` | 現在のブランチを強制プッシュ（確認プロセス付き） |
| Git操作 | `/git-get-code-diff-and-test-coverage` | 指定期間内のコード変更を取得し、変更ファイルのテストカバレッジを計測 |
| MCP・CLI開発 | `/coding-mcp` | MCP開発のスペシャリストとしてサーバー新規作成・ツール追加・ツール更新を実施 |
| 情報収集 | `/fetch-web-search-result` | Web検索でヒットした記事を取得して処理 |
| 情報収集 | `/research-play-console-update` | Google Play Consoleの更新情報を収集・調査 |

## ルールファイル一覧

ルールファイルは `~/.claude/rules/` に同期され、`paths` フロントマターで指定されたファイルを扱う際に自動適用されます。

| ルール名 | 説明 | 適用条件 |
|---------|------|----------|
| `swift-testing` | Swift Testingフレームワークのテストコード生成ルール（XCTest禁止、struct使用、#expectマクロ等） | `*Test*.swift`, `*Tests*.swift` |
| `android-development` | Android開発のコーディング規約（Kotlin優先、Coroutine/Flow、Compose、ライフサイクル等） | `.kt`, `.java`, `.xml`, `build.gradle` |

## 使用方法

1. 各ディレクトリに適切なファイルを配置
2. Claude Codeでスラッシュコマンドを使用してファイルを参照
3. 必要に応じてテンプレートやルールをプロジェクトに適用
