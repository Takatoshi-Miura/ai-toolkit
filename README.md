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
├── agents/            <- サブエージェント関連の定義や設定
├── rules/             <- ルールファイルやポリシー、ワークフロー
├── templates/         <- 定型テンプレートファイル、応答フォーマットなど
├── output-style/      <- Claude Codeの出力スタイル設定
├── scripts/           <- 自動化スクリプト（Python等）
├── task/              <- タスク定義ファイル（スラッシュコマンドから参照される詳細な手順）
└── README.md          <- このファイル
```

## スラッシュコマンド一覧

| コマンド名 | 説明 |
|-----------|------|
| `/add-mcp-tool` | 既存のMCPサーバに新しいMCPツールを追加 |
| `/auto-task` | ユーザーの要望を分析し、適切なタスクを自動選択して実行 |
| `/coding` | モバイルアプリ開発のスペシャリストとして実装タスクを実施（Git ワークフロー・計画含む） |
| `/create-command` | カスタムスラッシュコマンドとタスクファイルを対話形式で作成 |
| `/create-mcp-server` | 要件に基づくMCPサーバを構築 |
| `/fetch-news` | 最新ニュース記事を取得して提供 |
| `/fetch-web-search-result` | Web検索でヒットした記事を取得して処理 |
| `/generate-test-item` | 因子・水準組み合わせに基づくテスト項目書を作成 |
| `/generate-test-plan` | テスト観点スプレッドシートと機能仕様に基づいてテスト計画を自動生成 |
| `/git-force-push` | 現在のブランチを強制プッシュ（確認プロセス付き） |
| `/git-get-code-diff-and-test-coverage` | 指定期間内のコード変更を取得し、変更ファイルのテストカバレッジを計測 |
| `/inspire-action` | 退屈な時にユーザーの目標や記録を踏まえて次のアクションを提案 |
| `/install-apk` | Android端末へのAPKインストールを支援 |
| `/research-play-console-update` | Google Play Consoleの更新情報を収集・調査 |
| `/retrospective-monthly` | 振り返りスペシャリストとして月次レトロスペクティブを実施（時間管理・家計・日次記録分析） |
| `/retrospective-weekly` | 振り返りスペシャリストとして週次レトロスペクティブを実施（時間管理・日次記録分析） |
| `/retrospective-yearly` | 振り返りスペシャリストとして年次レトロスペクティブを実施（時間管理・家計・日次記録・年間目標達成度分析） |
| `/review-document` | Google Drive文書/シート/スライド、またはGitHub PRを適切にレビュー |
| `/solve-problem` | 問題解決のスペシャリストとして7フェーズの構造化された問題解決プロセスをガイド |
| `/update-command` | 既存のカスタムスラッシュコマンドを対話形式で更新・改善 |
| `/write-letter-of-gratitude` | 手紙作成のスペシャリストとして、感謝の手紙のドラフト作成を支援 |

## タスクファイル一覧

### Git & バージョン管理 (6)
| タスク名 | 説明 |
|---------|------|
| `git-create-branch` | [prefix]/[ticket]/[implementation-name]形式でfeatureブランチを作成 |
| `git-create-empty-commit` | [prefix]/[title] refs #[ticket]形式で空コミットを作成 |
| `git-create-pull-request` | テンプレート付きドラフトPRを作成し、Redmine参照を置換してPRリンクをチケットに追加 |
| `git-force-push` | ブランチ名確認とユーザー承認後、現在のブランチを強制プッシュ |
| `git-get-code-diff` | 指定期間とユーザーのコミット情報と変更ファイルを抽出 |
| `git-push-current-branch` | `git push -u origin <branch_name>`で現在のブランチをリモートにプッシュ |

### コーディング & 実装 (5)
| タスク名 | 説明 |
|---------|------|
| `coding-english-resources` | スプレッドシートの英語テキストをアプリの言語リソースファイルに追加（日本語ファイルの順序に合わせる） |
| `coding-implementation` | 計画に従って実装、ビルド、テスト作成（必要に応じて）、動作確認 |
| `coding-plan` | Planサブエージェントを使用してコード分析と実現可能性評価を含む実装計画を作成 |
| `create-command` | 対話形式でカスタムスラッシュコマンドを設計、ファイル生成、検証 |
| `update-command` | 既存スラッシュコマンドの現状分析と変更適用、検証を実施 |

### 問題解決 (6)
| タスク名 | 説明 |
|---------|------|
| `solve-problem` | 問題定義からリスク計画まで7フェーズの問題解決プロセス全体を実行 |
| `solve-problem-analyze` | フェーズ3: 5-Why法による根本原因の掘り下げ(Why)とタスク設定 |
| `solve-problem-define` | フェーズ1-2: 問題の定義(What)と発生箇所の特定(Where) |
| `solve-problem-planning` | フェーズ5-6: 解決策をタスクに分解し、マイルストーン付き実行スケジュールを作成 |
| `solve-problem-risk` | フェーズ7: リスク特定、予防・軽減策の定義、トリガー設定 |
| `solve-problem-solution` | フェーズ4: 解決策のブレインストーミングと評価基準に基づく最適案選択 |

### データ & 統合 (5)
| タスク名 | 説明 |
|---------|------|
| `read-google-drive` | シート/タブ指定オプション付きでGoogle Driveスプレッドシートや文書を読み取り |
| `read-life-graph` | LifeGraphスプレッドシートのGoogleカレンダー集計シート(A-O列)を読み取り |
| `read-money-sheet` | 予算・財務計画シートを含む家計管理スプレッドシート(A-AN列)を読み取り |
| `read-note` | 年間目標と当月進捗タブを含むユーザーのノート文書を読み取り |
| `read-redmine-ticket` | 提供されたURLからmcp-redmineツールを使用してRedmineチケット詳細を読み取り |

### テスト & 品質保証 (3)
| タスク名 | 説明 |
|---------|------|
| `command-validation` | kebab-case命名規則に準拠しているかスラッシュコマンドとタスクファイルをチェック |
| `generate-test-plan` | 機能仕様とテスト観点を分析してテスト計画を自動生成し、スプレッドシート更新 |
| `review-document` | フレームワーク固有のレビュー観点でGitHub PRまたはGoogle Drive文書をレビュー |

### MCP開発 (2)
| タスク名 | 説明 |
|---------|------|
| `add-mcp-tool` | 要件分析と実装を通じて既存MCPサーバに新しいツールを追加 |
| `create-mcp-server` | MCP-GoogleDriveパターンに従ってゼロから完全なMCPサーバを構築 |

### 情報収集 (4)
| タスク名 | 説明 |
|---------|------|
| `fetch-web-search` | Web検索を実行し、タイトルとリンク付きで上位10件の記事結果を取得 |
| `fetch-yahoo-news` | Yahoo News(国内・国際・ビジネス)から最新ニュースを各8記事取得 |
| `inspire-action` | 4カテゴリから次のアクションを提案: 目標達成・業務効率・リフレッシュ・余暇(1時間圏内) |
| `research-play-console-update` | automata-androidアプリに影響するPlay Consoleの過去30日間の更新を調査 |

### 自動化 & その他 (4)
| タスク名 | 説明 |
|---------|------|
| `auto-task` | ユーザーリクエストを分析し、単一確認で適切なタスク/コマンドを自動選択 |
| `calendar-register-schedule` | イベントタイプに基づく色分けでGoogleカレンダーにイベントを登録(仕事・アイデア・生活・スキル・コード・本など) |
| `install-apk` | デバイス選択とエラーハンドリング付きで接続されたAndroid端末にAPKをインストール |
| `write-letter-of-gratitude` | 文書構造と条件に基づいて感謝の手紙のドラフトを作成 |

### 振り返り (5)
| タスク名 | 説明 |
|---------|------|
| `retrospective-common` | 振り返りタスク共通の前提条件（ユーザープロフィール・世帯状況・管理カテゴリ） |
| `retrospective-analyze-lifegraph` | LifeGraphデータを読み取り、時間の使い方を分析してレポート作成 |
| `retrospective-analyze-money` | 金銭管理データを読み取り、収支・予算・住宅ローン試算を分析（月次・年次） |
| `retrospective-analyze-daily` | 日々の振り返りノートを読み取り、カテゴリ別に分析してレポート作成 |
| `retrospective-analyze-yearly-goals` | 年間目標の達成度を分析し、カテゴリ別の成長と課題をレポート作成（年次のみ） |

## 使用方法

1. 各ディレクトリに適切なファイルを配置
2. Claude Codeでスラッシュコマンドを使用してファイルを参照
3. 必要に応じてテンプレートやルールをプロジェクトに適用
