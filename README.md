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
├── output-style/      <- Claude Codeの出力スタイル設定（キャラクター別応答スタイル）
├── scripts/           <- 自動化スクリプト（Python等）
└── README.md          <- このファイル
```

## Skills一覧

| カテゴリ | スキル名 | 説明 | 自動呼び出し |
|---------|---------|------|:------------:|
| 外部連携 | `google-drive-skill` | Google Drive（Sheets/Docs/Slides）の読み書き（値挿入・シート作成・セル結合・行列操作など） | ✅ |
| 外部連携 | `redmine-skill` | RedmineチケットURLからチケット詳細を取得・参照 | ✅ |
| 外部連携 | `github-skill` | Issue・PR・強制プッシュなどGitHub/Git操作全般 | ✅ |
| 環境管理 | `skill-manager` | プライベートスキル（~/.claude/skills/）の新規作成・更新・セルフチェック | ✅ |

## 定期実行スキル一覧

Claude Code のルーチン実行が起動主体のスキル。

| カテゴリ | スキル名 | 説明 |
|---------|---------|------|
| 通知 | `line-scheduled-recommender` | 実行時刻に応じて CONFIG.md のテーマを自動選択し、LINE グループに定期通知（お出かけ提案・読書推薦など複数テーマ対応） |
| 情報収集 | `daily-notebooklm-research` | 未調査テーマリスト・Googleドキュメント・セッションログ・ai-toolkit既存リソースから調査テーマを決定し、NotebookLM用のURLリストと音声解説プロンプトを生成（working folder不要、スキルディレクトリ直下のCONFIG.md/history.mdで完結） |
| 開発 | `sportsnote-ios-maintainer` | SportsNote iOSの開発・保守を無人実行（ナレッジ蓄積/issue作成/実装の3フロー） |
| 開発 | `sportsnote-ios-full-cycle` | `sportsnote-ios-maintainer`の3フローを1回ずつ直列実行するオーケストレーター |
| 開発 | `sportsnote-android-maintainer` | SportsNote Androidの開発・保守を無人実行（ナレッジ蓄積/issue作成/実装の3フロー） |
| 開発 | `sportsnote-android-full-cycle` | `sportsnote-android-maintainer`の3フローを1回ずつ直列実行するオーケストレーター |

> セットアップ手順は各スキルの `SETUP.md` を参照。

