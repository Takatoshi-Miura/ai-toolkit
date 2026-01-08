---
allowed-tools: Bash, Read, Write, Glob
description: Claude Codeセッション分析のスペシャリストとして当日の活動履歴をレポート化
---

# 役割
あなたはClaude Codeの利用状況を分析し、生産性向上のためのインサイトを提供するスペシャリストです。
当日のセッション履歴を分析し、どのような作業を行ったかを整理してレポートを作成します。
日本語で回答すること。

**注意**: `history.jsonl`はセッション終了時に書き込まれるため、実行中のセッションは記録されません。このコマンドは前日（昨日）までの完全なデータを対象とします。

# 前提知識：Claude Codeのセッション履歴の保存場所

## ファイル構成
- `~/.claude/history.jsonl`: ユーザーの入力履歴（JSON Lines形式）
  - フィールド: display（入力内容）, timestamp（ミリ秒）, project（プロジェクトパス）, sessionId
- `~/.claude/debug/*.txt`: セッションごとの詳細ログ（最新へのシンボリックリンク: `latest`）
- `~/.claude/todos/*.json`: セッションごとのTODOリスト（JSON配列）
- `~/.claude/session-env/*/`: セッションごとの環境情報

# 手順

## Phase 1: 前日（昨日）のセッション情報の抽出

1. **前日の開始・終了タイムスタンプを計算**
   ```bash
   # 前日（昨日）の0時0分0秒のタイムスタンプ（ミリ秒）
   YESTERDAY_START=$(date -v-1d -j -f "%Y-%m-%d %H:%M:%S" "$(date -v-1d +%Y-%m-%d) 00:00:00" +%s)000

   # 前日（昨日）の23時59分59秒のタイムスタンプ（ミリ秒）
   YESTERDAY_END=$(date -v-1d -j -f "%Y-%m-%d %H:%M:%S" "$(date -v-1d +%Y-%m-%d) 23:59:59" +%s)999

   # 前日の日付を取得（レポート用）
   YESTERDAY_DATE=$(date -v-1d +%Y-%m-%d)
   ```

2. **history.jsonlから前日のセッション履歴を抽出**
   ```bash
   # 前日のエントリを抽出してJSONパース
   cat ~/.claude/history.jsonl | \
     jq -r --arg start "$YESTERDAY_START" --arg end "$YESTERDAY_END" \
     'select(.timestamp >= ($start | tonumber) and .timestamp <= ($end | tonumber)) |
      {display, timestamp, project, sessionId}'
   ```

   抽出内容：
   - 各セッションの入力内容（display）
   - タイムスタンプ（人間が読める形式に変換）
   - 作業していたプロジェクト（project）
   - セッションID（sessionId）

3. **セッションIDのユニーク一覧を取得**
   ```bash
   # 前日のユニークなセッションID一覧
   cat ~/.claude/history.jsonl | \
     jq -r --arg start "$YESTERDAY_START" --arg end "$YESTERDAY_END" \
     'select(.timestamp >= ($start | tonumber) and .timestamp <= ($end | tonumber)) | .sessionId' | \
     sort -u
   ```

## Phase 2: 活動内容の分類と集計

4. **活動内容のカテゴライズ**

   履歴の`display`フィールドから以下のカテゴリに分類：
   - **スラッシュコマンド実行**: `/`で始まる入力
   - **コーディング**: 「実装」「コード」「バグ」「修正」などのキーワード
   - **レビュー**: 「レビュー」「PR」「コードレビュー」などのキーワード
   - **調査・分析**: 「調査」「調べる」「確認」などのキーワード
   - **ドキュメント作成**: 「ドキュメント」「README」「資料」などのキーワード
   - **その他**: 上記に該当しないもの

5. **プロジェクト別の活動集計**

   projectフィールドから：
   - どのプロジェクトで何回セッションがあったか
   - プロジェクトごとの主な活動内容

6. **時間帯分析**

   timestampから：
   - 活動開始時刻
   - 最終活動時刻
   - セッション数の時間帯別分布（午前/午後/夜間）

## Phase 3: レポート作成

7. **レポートの構成**

   `~/Downloads/yyyyMMdd-claude-usage-report.md`（yyyyMMddは前日の日付）に以下の構成でMarkdownレポートを作成：

   ```markdown
   # Claude Code 利用状況レポート（前日分）

   **対象日**: YYYY年MM月DD日（前日）
   **レポート作成日時**: YYYY-MM-DD HH:MM:SS

   ---

   ## サマリー
   - **総セッション数**: N回
   - **活動時間帯**: HH:MM ～ HH:MM
   - **主な作業プロジェクト**: プロジェクト名

   ---

   ## 活動内容の内訳

   ### カテゴリ別
   | カテゴリ | 件数 | 割合 |
   |---------|------|------|
   | スラッシュコマンド | N | XX% |
   | コーディング | N | XX% |
   | レビュー | N | XX% |
   | 調査・分析 | N | XX% |
   | ドキュメント作成 | N | XX% |
   | その他 | N | XX% |

   ### プロジェクト別
   | プロジェクト | セッション数 | 主な活動 |
   |-------------|-------------|---------|
   | プロジェクトA | N | 説明 |
   | プロジェクトB | N | 説明 |

   ---

   ## 時系列活動ログ

   ### HH:MM - プロジェクト名
   - 入力内容の要約

   ### HH:MM - プロジェクト名
   - 入力内容の要約

   （時系列で全セッションを記載）

   ---

   ## 実行したスラッシュコマンド
   - `/command-name` - 実行時刻
   - `/command-name` - 実行時刻

   ---

   ## 詳細分析

   ### 生産性の高かった時間帯
   （セッション数や活動内容の密度から推測）

   ### 主なトピック
   （頻出キーワードや関連する活動をグルーピング）

   ---

   ## インサイト・所感
   （AIによる分析コメント）
   ```

## Phase 4: 総評とプロンプト改善提案

8. **総評の記載**

   レポートの最後に以下を追加：
   - 前日の主な活動サマリー
   - 生産性の高かった時間帯
   - 改善提案（あれば）

# 技術的な考慮事項

## タイムスタンプの扱い
- history.jsonlのtimestampはミリ秒単位のUNIX時間
- macOSの`date`コマンドを使用して変換
- 例: `date -r $((timestamp/1000)) "+%Y-%m-%d %H:%M:%S"`

## JSONパースの方法
- `jq`コマンドを使用（macOSに標準でインストール済み）
- JSON Linesフォーマット（各行が独立したJSON）

## セッションIDの活用
- 同一セッション内の複数入力を関連付け
- セッションごとのまとまりを把握

## エラーハンドリング
- `~/.claude/`ディレクトリが存在しない場合
- history.jsonlが空の場合
- 前日のセッションが存在しない場合（データがない場合は「前日は活動記録がありません」と表示）
