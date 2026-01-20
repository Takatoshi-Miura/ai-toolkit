---
name: review-document-skill
description: Review GitHub PRs and Google Drive documents. Automatically triggered when user shares a GitHub PR URL (github.com/*/pull/*) or Google Drive URL (docs.google.com, drive.google.com) and asks for review, feedback, or comments. Also activates for phrases like "このPRレビューして", "このドキュメント見て", "レビューお願い", "フィードバックちょうだい".
allowed-tools: mcp__mcp-google-drive__*, mcp__mcp-gh-pr-mini__*, Read, Grep, Glob
---

# ドキュメント・PRレビュースキル

GitHub PRまたはGoogle Drive資料（ドキュメント、スプレッドシート、スライド）を自動的にレビューします。

## 発動条件

このスキルは以下の状況で自動的に適用されます：

- GitHub PR URL（`github.com/.../pull/...`）が含まれ、レビューを依頼されたとき
- Google Drive URL（`docs.google.com`、`drive.google.com`）が含まれ、レビューを依頼されたとき
- 「レビューして」「見て」「確認して」「フィードバック」などのキーワードとURLが組み合わさったとき

## 手順

### 1. URL種類の判別

ユーザーのメッセージからURLを抽出し、種類を判別する：

| URLパターン | 種類 | 次のステップ |
|------------|------|-------------|
| `github.com` を含む | GitHub PR | → Phase 2A へ |
| `docs.google.com` または `drive.google.com` を含む | Google Drive | → Phase 2B へ |

### 2A. GitHub PRレビュー（GitHub URLの場合）

[PR-REVIEW-GUIDE.md](PR-REVIEW-GUIDE.md) の手順に従ってレビューを実施する。

**主なレビュー観点:**
- 変更の目的・スコープ
- 仕様・ロジック・データ整合性
- プラットフォーム固有の考慮事項
- 画面遷移・状態管理・非同期処理
- UI/UX・ユーザビリティ
- 設計・可読性・保守性
- テスト
- セキュリティ
- パフォーマンス・リソース

### 2B. Google Driveレビュー（Google Drive URLの場合）

[DRIVE-REVIEW-GUIDE.md](DRIVE-REVIEW-GUIDE.md) の手順に従ってレビューを実施する。

**主なレビュー観点:**
- 内容の要約
- 構成分析
- 良い点
- 改善提案（優先度別）
- 確認事項・質問

## 出力形式

レビュー結果は各ガイドファイルで定義されたテンプレートに従って出力する。

## 注意事項

- PRレビューの場合、対象ブランチにチェックアウトされているか確認が必要
- Google Driveの場合、`g_drive_search_files`は使用しない（ファイルIDがURLから取得可能なため）
- 追加のコンテキスト（PBI、概要設計書、テスト項目書など）が提供された場合は、それも考慮してレビューする
- 日本語で回答すること
