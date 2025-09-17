---
description: スプレッドシートを読み取り、英語文言のリソースを追加
argument-hint: <spreadsheet_url> <english_resource_file_path>
allowed-tools: mcp__mcp-google-drive__g_drive_get_file_structure, mcp__mcp-google-drive__g_drive_read_file_part, Read, Edit, Glob, Grep, TodoWrite
---

# 役割
あなたの役割は与えられたスプレッドシートを読み取り、手順に従って英語文言のリソースを追加することです。

# スプレッドシートのリンク
$1

# 英語文言リソースファイル
$2

# 実行手順
1. スプレッドシートURLからfile_idを抽出し、g_drive_get_file_structure ツールを使ってシート構造を読み取る
2. g_drive_read_file_part ツールを使用して「文言」シートを読み取り、日本語文言とそれに対応する英語文言を読み取る
3. 英語文言リソースファイルと同じプロジェクト内の日本語文言リソースファイルを探す
4. 「文言追加ルール」に従い、英語文言リソースファイルに2で読み取った英語文言を追加する

# 文言追加ルール
・シートに記載されている文言のみ追加すること（日本語リソースのみ存在する文言があっても問題ない）
・追加する位置は日本語文言リソースの並び順と合わせること

必ずTodoWriteツールを使用してタスクの進捗を管理し、各手順の完了を明確に追跡してください。