---
allowed-tools: mcp__mcp-github__*
description: 指定期間内のユーザーのコード変更ファイル取得とコードカバレッジを計測
---

# 役割
あなたの役割は ~/Documents/Git/automata-android のプロジェクトのコード差分を取得し、変更のあったファイルのテストカバレッジを計測することです。
日本語で回答すること。

# 手順
1. 以降の手順で読み取るmdファイルの内容を確認して全体像を把握し、TODOを漏れなく作成してください
2. ~/Documents/Git/ai-toolkit/task/git-get-code-diff.md のタスクを実施
3. 以下のコマンドを実行してテスト実行とカバレッジレポートを作成する
```bash
# テスト実行＋レポート生成（一括）
./gradlew generateCoverageReport

# レポート確認場所
automata-a/app/build/reports/jacoco/index.html
```
4. 手順3のカバレッジレポートを読み込み、変更のあったファイルのリストをカバレッジ率%つきで漏れなく表形式で出力
    - 表の列は「ファイル名」「カバレッジ%」としてください
    - テストファイルはリストに載せなくてOKです
    - Jetpack ComposeコンポーネントやFragment/View系のファイルもリストに載せなくてOKです