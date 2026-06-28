# AI Toolkit

Claude CodeのカスタムスラッシュコマンドやAI活用のためのリソースをまとめたリポジトリです。

## 目的

今後のAI活用において、効率的な開発環境を構築し、再利用可能なリソースを体系的に管理することを目的としています。

## ディレクトリ構成

```
ai-toolkit/
├── .github/
│   └── workflows/     <- GitHub Actions ワークフロー定義
├── skills/            <- Claude Code Skills（自動発動する専門スキル）
├── agents/            <- サブエージェント関連の定義や設定
├── output-style/      <- Claude Codeの出力スタイル設定（キャラクター別応答スタイル）
├── scripts/           <- 自動化スクリプト（Python等）
├── statusline/        <- Claude Codeステータスライン表示スクリプト（~/.claude/に同期）
└── README.md          <- このファイル
```

## Skills一覧

| カテゴリ | スキル名 | 説明 | 自動呼び出し |
|---------|---------|------|:------------:|
| 外部連携 | `google-drive-skill` | Google Drive（Sheets/Docs/Slides）の読み書き（値挿入・シート作成・セル結合・行列操作など） | ✅ |
| 外部連携 | `redmine-skill` | RedmineチケットURLからチケット詳細を取得・参照 | ✅ |
| 外部連携 | `github-skill` | Issue・PR・強制プッシュなどGitHub/Git操作全般 | ✅ |
| 自動化基盤 | `slack-message-router` | SlackメッセージをSocket Modeで監視し、キーワードに基づいてClaude Codeスキルにルーティング | ❌ |
| 開発 | `coding` | モバイルアプリ・MCP開発・SportsNote iOS・OpenSpecプロポーザル作成・FE開発のオーケストレーター | ❌ |
| 開発 | `generate-test-item-skill` | 因子水準の全組み合わせからテスト項目書をスプレッドシートに自動生成 | ❌ |
| 開発 | `review-skill` | GitHub PRレビュー（Android/汎用を自動判定）とGoogle Drive資料レビュー | ✅ |
| 開発 | `dev-tools` | AndroidデバイスへのAPKインストール、PDFからの画像抽出などの開発効率化ツール群 | ❌ |
| 情報収集 | `research` | Web検索・PlayConsole更新情報・Claude Changelog確認を統合管理 | ❌ |
| 内省・分析 | `retrospective` | LifeGraph・日次記録・金銭データを分析して週次/月次レポートを作成 | ❌ |
| 内省・分析 | `claude-session-log-to-rules` | セッションログ全プロジェクト横断でフィードバック・指示・承認を抽出し、ルールファイルへの反映を提案 | ❌ |
| 内省・分析 | `session-reflection` | 作業セッションの内容から学びや気づきをログ転記しやすい形式で抽出・整理 | ❌ |
| 環境管理 | `homebrew` | Homebrewの更新・追加・削除・App Store移行・Mac環境移行を統括 | ✅ |
| 環境管理 | `skill-manager` | プライベートスキル（~/.claude/skills/）の新規作成・更新・セルフチェック | ✅ |
| ゲーム | `genshin-advisor` | 原神アカウントの公式HoYoLAB APIでキャラ・聖遺物・パーティ編成・深境螺旋などをアドバイス | ✅ |

## Cowork 定期実行スキル一覧

Claude Code ではなく **Cowork のスケジューラ** が起動主体のスキル。
working folder（Cowork 上に作成）が必須で、LINE などへの自動通知に使用する。

| カテゴリ | スキル名 | 説明 |
|---------|---------|------|
| 通知 | `line-scheduled-recommender` | 実行時刻に応じて CONFIG.md のテーマを自動選択し、LINE グループに定期通知（お出かけ提案・読書推薦など複数テーマ対応） |
| 情報収集 | `daily-notebooklm-research` | 未調査テーマリスト・Googleドキュメント・セッションログ・ai-toolkit既存リソースから調査テーマを決定し、NotebookLM用のURLリストと音声解説プロンプトを生成（working folder不要、スキルディレクトリ直下のCONFIG.md/history.mdで完結） |

> セットアップ手順は各スキルの `SETUP.md` を参照。

## サブエージェント一覧

| カテゴリ | エージェント名 | 説明 |
|---------|--------------|------|
| テスト | `test-item-writer` | テスト項目書をスプレッドシートに書き込む |

