---
allowed-tools: mcp__mcp-github__*, Bash, Read
description: 指定期間内のユーザーのコード変更ファイル取得とコードカバレッジを計測
---

# 役割
あなたの役割は ~/Documents/Git/automata-android のプロジェクトのコード差分を取得し、変更のあったファイルのテストカバレッジを計測することです。
日本語で回答すること。

# 概要
指定した期間のコード差分を取得し、変更ファイルのテストカバレッジを計測する。

# 手順

## Phase 1: 情報収集

1. 以下の情報が提供されていなければ、ユーザーに質問して提供してもらう
    - コード差分を取得したいリポジトリ
    - 期間（開始日・終了日、例: `2025-10-01` ～ `2025-11-18`）

## Phase 2: コード差分の取得

2. 以下のコマンドを使用し、コミット情報や変更ファイル情報を取得する
```bash
# コミット一覧（マージコミットを除外）
git log --author="takatoshi.miura" --since="<開始日>" --until="<終了日>" --no-merges --pretty=format:"%H|%h|%s|%ai" --all

# コミット数（マージコミットを除外）
git log --author="takatoshi.miura" --since="<開始日>" --until="<終了日>" --no-merges --all --oneline | wc -l

# 全ファイル（マージコミットを除外）
git log --author="takatoshi.miura" --since="<開始日>" --until="<終了日>" --no-merges --name-only --pretty=format: --all | grep -v '^$' | sort -u

# 本番用Kotlinのみ（マージコミットを除外）
git log --author="takatoshi.miura" --since="<開始日>" --until="<終了日>" --no-merges --name-only --pretty=format: --all | grep -v '^$' | sort -u | grep -E '\.kt$' | grep 'src/main/java'

# ファイル数（マージコミットを除外）
git log --author="takatoshi.miura" --since="<開始日>" --until="<終了日>" --no-merges --name-only --pretty=format: --all | grep -v '^$' | sort -u | wc -l
```

3. 以下の情報をユーザーに返却する
    - リポジトリ名
    - 期間
    - ユーザー名
    - コミット数
    - コミット一覧
    - 変更ファイル数
    - 変更ファイル名のリスト

## Phase 3: カバレッジ計測

4. 以下のコマンドを実行してテスト実行とカバレッジレポートを作成する
```bash
# テスト実行＋レポート生成（一括）
./gradlew generateCoverageReport

# レポート確認場所
automata-a/app/build/reports/jacoco/index.html
```

## Phase 4: 結果報告

5. カバレッジレポートを読み込み、変更のあったファイルのリストをカバレッジ率%つきで漏れなく表形式で出力
    - 表の列は「ファイル名」「カバレッジ%」としてください
    - テストファイルはリストに載せなくてOKです
    - Jetpack ComposeコンポーネントやFragment/View系のファイルもリストに載せなくてOKです
