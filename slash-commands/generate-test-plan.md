---
description: スプレッドシートのテスト観点を読み取り、機能仕様に基づいてテスト計画を自動生成
argument-hint: <spreadsheet_url> <reference_md_path>
allowed-tools: mcp__mcp-google-drive__g_drive_get_file_structure, mcp__mcp-google-drive__g_drive_read_file_part, mcp__mcp-google-drive__g_drive_copy_element, mcp__mcp-google-drive__g_drive_insert_value, Read, TodoWrite
---

# 役割
あなたの役割は与えられたスプレッドシートのテスト観点を読み取り、機能仕様に基づいてテスト計画（実施要否とテスト内容）を自動生成することです。

# スプレッドシートのリンク
$1

# 参考情報ファイルパス
$2

# 実行手順

## 1. ドキュメント構造の把握
- スプレッドシートURLからfile_idを抽出し、mcp__mcp-google-drive__g_drive_get_file_structure ツールを使ってシート構造を読み取る

## 2. 原本シートの複製
- mcp__mcp-google-drive__g_drive_copy_element ツールを使い、「原本」シートを複製
- 複製シート名は適切な名前（例：「テスト計画_YYYYMMDD」）に設定

## 3. 機能仕様の読み取り
- 引数2で指定されたmdファイルから、テスト対象機能の仕様について読み取る
- 機能の目的、操作方法、期待される動作を把握

## 4. テスト観点の読み取り
- mcp__mcp-google-drive__g_drive_read_file_part ツールを範囲指定A:Jで使用し、既存のテスト観点を読み取る

## 5. テスト実施要否の判定
- 手順3で読み取った機能仕様と手順4で読み取ったテスト観点を照らし合わせる
- 各観点について、今回開発する機能でテストが必要かを判定
- O列に既に記載がある観点については判定をスキップ
- mcp__mcp-google-drive__g_drive_insert_value ツールを使い、O列に判定結果を記載：
  - 「実施必要」：その観点でのテストが必要
  - 「実施不要」：その観点でのテストは不要
  - g_drive_insert_value ツールはセルの上書きはできない仕様のため、既に記載のあるセルを避け、複数回に分けて実行すること

## 6. テスト内容の記載
- O列で「実施必要」と判定した行について、具体的なテスト内容をP列に記載
- mcp__mcp-google-drive__g_drive_insert_value ツールを使い、以下の形式で箇条書きで記載：
  - どのような操作を行うか
  - 何を確認するか
  - 期待される結果
- 簡潔で実行可能な内容とする

## 注意事項
- O列に既に記載がある観点については、判定や内容記載を行わない
- テスト内容は機能仕様に基づいて具体的かつ実用的なものとする
- 複数の観点で同じようなテストが必要な場合も、それぞれ独立して記載する

必ずTodoWriteツールを使用してタスクの進捗を管理し、各手順の完了を明確に追跡してください。