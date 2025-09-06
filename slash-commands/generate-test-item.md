---
description: スプレッドシートを読み取り、因子・水準組み合わせに基づくテスト項目書を作成
argument-hint: <spreadsheet_url> <reference_md_path>
allowed-tools: mcp__mcp-google-drive__g_drive_get_file_structure, mcp__mcp-google-drive__g_drive_read_file_part, mcp__mcp-google-drive__g_drive_copy_element, mcp__mcp-google-drive__g_drive_insert_value, Read, Task, TodoWrite
---

# 役割
あなたの役割は与えられたスプレッドシートを読み取り、手順に従ってテスト項目書を作成することです。

# スプレッドシートのリンク
$1

# 参考情報ファイルパス
$2

# 実行手順

## 準備フェーズ（メイン実行）
1. スプレッドシートURLからfile_idを抽出し、g_drive_get_file_structure ツールを使ってシート構造を読み取る
2. g_drive_read_file_part ツールを範囲指定"因子・水準!A:AB"で使用し、「因子・水準」シートを読み取る
3. g_drive_copy_elementツールを使い、2の因子水準表の数だけ「原本」シートを複製し、各シート名を表のタイトルにすること
4. g_drive_read_file_part ツールを範囲指定で使用して「原本」シートを読み取り、各列に記載する項目を把握する
5. 参考情報ファイルから情報を読み取り、テストすべき内容を把握する
   - issueの場合はmcp-gh-issue-miniのget_issue ツールで読み取る

## 並列実行フェーズ（サブエージェント実行）
6. 手順3で作成したシートの数だけtest-item-generatorサブエージェントを並列起動し、以下のパラメータを渡す：
   - spreadsheet_id: 対象スプレッドシートID
   - sheet_name: 機能名（動的に取得したシート名）
   - factors_data: 該当する因子・水準データ（動的に抽出）
   - test_requirements: 対応する参考情報とテスト仕様（動的にマッピング）
7. 起動した全てのサブエージェントのタスクが全て完了したのを確認してタスク完了としてください

必ずTodoWriteツールを使用してタスクの進捗を管理し、各フェーズの完了を明確に追跡してください。