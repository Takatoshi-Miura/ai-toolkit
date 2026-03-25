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
├── claude-web-skills/ <- Claude Web用スキル（プロジェクトのナレッジとして使用）
├── agents/            <- サブエージェント関連の定義や設定
├── global/            <- グローバル設定（~/.claude/CLAUDE.mdに同期）
├── rules/             <- ルールファイル（~/.claude/rules/に同期、paths指定で条件適用）
├── templates/         <- 定型テンプレートファイル、応答フォーマットなど
├── output-style/      <- Claude Codeの出力スタイル設定
├── scripts/           <- 自動化スクリプト（Python等）
├── statusline/        <- Claude Codeステータスライン表示スクリプト（~/.claude/に同期）
└── README.md          <- このファイル
```

## Skills一覧

| カテゴリ | スキル名 | 説明 | 自動呼び出し |
|---------|---------|------|:------------:|
| データ操作 | `google-drive-skill` | Google Drive（Sheets/Docs/Slides）の読み書き（値挿入・シート作成・セル結合・行列操作など） | ✅ |
| データ操作 | `redmine-skill` | RedmineチケットURLからチケット詳細を取得・参照 | ✅ |
| レビュー | `review-skill` | GitHub PRレビュー（Android/汎用を自動判定）とGoogle Drive資料レビュー | ✅ |
| GitHub/Git操作 | `github-skill` | Issue・PR・強制プッシュなどGitHub/Git操作全般 | ✅ |
| Git操作 | `git-pr-setup` | Redmineチケットを元にブランチ作成・空コミット・PR作成・Redmineコメントを一括自動化 | ✅ |
| パーソナライズ | `personal-context-aware-response` | Google Driveのパーソナルコンテキストを読み取り、価値観・思考スタイルに合わせた回答を提供 | ✅ |
| リソース管理 | `manage-resources` | Claude Codeリソース（コマンド/エージェント/Skills）の新規作成・更新・メンテナンス・~/.claude/への同期 | ✅ |
| 振り返り | `retrospective` | LifeGraph・日次記録・金銭データを分析して週次/月次レポートを作成 | ❌ |
| 開発・コーディング | `coding` | モバイルアプリ・MCP開発・SportsNote iOS・OpenSpecプロポーザル作成のオーケストレーター | ❌ |
| テスト | `generate-test-item-skill` | 因子水準の全組み合わせからテスト項目書をスプレッドシートに自動生成 | ❌ |
| ユーティリティ | `extract-pdf-images` | PDFから埋め込み画像を抽出し~/Downloads/に保存（単一/複数対応） | ✅ |
| ユーティリティ | `check-drive-document-updates-skill` | 指定日以降のGoogle Driveファイル更新有無を確認 | ✅ |
| ユーティリティ | `homebrew` | Homebrewの更新・追加・削除・App Store移行・Mac環境移行を統括 | ✅ |
| 情報収集 | `research` | Web検索・PlayConsole更新情報・Claude Changelog確認を統合管理 | ❌ |
| Slack連携 | `slack-message-router` | SlackメッセージをSocket Modeで監視し、キーワードに基づいてClaude Codeスキルにルーティング | ❌ |


## Claude Web用スキル一覧

[Claude.ai](https://claude.ai/) のプロジェクト機能で使用するスキル。
プロジェクトのカスタマイズからカスタムスキルとしてアップロードして使用する。

| カテゴリ | スキル名 | 説明 |
|---------|---------|------|
| 振り返り | `retrospective` | LifeGraph・日次記録をコネクタで取得・分析し週次レポートを作成（金銭分析はClaude Code版のみ） |
| 振り返り | `retro-questions` | 2016年からの振り返り記録を活用し、振り返り質問を作成 |

## サブエージェント一覧

| カテゴリ | エージェント名 | 説明 |
|---------|--------------|------|
| テスト | `test-item-writer` | テスト項目書をスプレッドシートに書き込む |

## スラッシュコマンド一覧

| カテゴリ | コマンド名 | 説明 |
|---------|-----------|------|
| 開発・コーディング | `/create-todo-issue` | 思いついたTODOをGitHub Issueとして登録 |
| 開発・コーディング | `/install-apk` | Android端末へのAPKインストール |

## ルールファイル一覧

| ルール名 | 説明 | 適用条件 |
|---------|------|----------|
| `swift-testing` | Swift Testingフレームワークのコード生成規約 | `*Test*.swift`, `*Tests*.swift` |
| `android-development` | Android開発のコーディング規約 | `.kt`, `.java`, `.xml`, `build.gradle` |

## 使用方法

1. 各ディレクトリに適切なファイルを配置
2. Claude Codeでスラッシュコマンドを使用してファイルを参照
3. 必要に応じてテンプレートやルールをプロジェクトに適用
