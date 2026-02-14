---
name: review-skill
description: GitHub PRおよびGoogle Drive資料（ドキュメント、スプレッドシート、スライド）のレビューを実施。GitHub PR URL（github.com/*/pull/*）やGoogle Drive URL（docs.google.com, drive.google.com）が含まれ、レビューを依頼された時に自動発動。Androidファイル（.kt、.java、.xml、build.gradle）を含むPRはAndroid専門レビューを実施。「レビューして」「PRレビュー」「コードレビュー」「このPRレビューして」「このドキュメント見て」「レビューお願い」「フィードバックちょうだい」「差分見て」「変更確認して」などの依頼で適用。
allowed-tools: mcp__mcp-google-drive__*, mcp__mcp-gh-pr-mini__*, Read, Grep, Glob, Bash
---

# レビュースキル

GitHub PR または Google Drive 資料のレビューを実施します。レビュー対象に応じて適切なガイドに分岐します。

日本語で回答すること。

---

## Phase 0: Todo登録

**TodoWriteツールで以下を登録：**

```json
[
  {"content": "Phase 1: レビュー対象の判別", "activeForm": "レビュー対象を判別中", "status": "pending"},
  {"content": "Phase 2: レビュー実施", "activeForm": "レビューを実施中", "status": "pending"},
  {"content": "Phase 3: 結果出力", "activeForm": "結果を出力中", "status": "pending"}
]
```

---

## Phase 1: レビュー対象の判別

ユーザーのメッセージからURLを抽出し、レビュー種類を判別する。

### 1-1. URL種類の判別

| URLパターン | 種類 | 次のステップ |
|------------|------|-------------|
| `github.com` を含む | GitHub PR | → 1-2 へ |
| `docs.google.com` または `drive.google.com` を含む | Google Drive | → Phase 2C へ |

### 1-2. Androidプロジェクト判定（GitHub PRの場合）

PRの変更ファイルを確認し、以下のいずれかに該当する場合は **Androidレビュー** として扱う：

- 変更ファイルに `.kt`, `.java`, `.xml`, `.gradle`, `.kts` が含まれる
- プロジェクトに `AndroidManifest.xml`, `build.gradle`, `app/src/main/` が存在する

| 判定結果 | 次のステップ |
|---------|-------------|
| Androidプロジェクト | → Phase 2B（Androidレビュー） |
| その他 | → Phase 2A（汎用PRレビュー） |

**成功確認**: レビュー種類が確定した → Phase 2へ

---

## Phase 2: レビュー実施

判別結果に応じて、対応するガイドファイルを参照してレビューを実施する。

### Phase 2A: 汎用PRレビュー

[PR-REVIEW-GUIDE.md](PR-REVIEW-GUIDE.md) の手順に従ってレビューを実施する。

**主なレビュー観点:**
- 変更の目的・スコープ
- 仕様・ロジック・データ整合性
- プラットフォーム固有の考慮事項
- 画面遷移・状態管理・非同期処理
- UI/UX・ユーザビリティ
- 設計・可読性・保守性
- テスト・セキュリティ・パフォーマンス

### Phase 2B: Android PRレビュー

[ANDROID-REVIEW-GUIDE.md](ANDROID-REVIEW-GUIDE.md) の手順に従ってレビューを実施する。

**汎用観点に加え、Android固有の重点観点:**
- Activity/Fragment/Serviceのライフサイクル管理
- Jetpackアーキテクチャコンポーネント
- Coroutineとライフサイクルの連携
- RecyclerView最適化・メモリリーク防止
- Galaxy端末のIME問題

### Phase 2C: Google Driveレビュー

[DRIVE-REVIEW-GUIDE.md](DRIVE-REVIEW-GUIDE.md) の手順に従ってレビューを実施する。

**主なレビュー観点:**
- 内容の正確性
- 構成・論理性
- 読みやすさ
- 完全性

**成功確認**: レビューが完了した → Phase 3へ

---

## Phase 3: 結果出力

レビュー結果を各ガイドファイルで定義されたテンプレートに従って出力する。

**成功確認**: ユーザーにレビュー結果が共有された → 完了

---

## 注意事項

- PRレビューの場合、対象ブランチにチェックアウトされているか確認が必要
- Google Driveの場合、`g_drive_search_files`は使用しない（ファイルIDがURLから取得可能なため）
- 追加のコンテキスト（PBI、概要設計書、テスト項目書など）が提供された場合は、それも考慮してレビューする

## エラー対応

| エラー | 対応 |
|-------|------|
| PR URLからPR情報を取得できない | `gh auth status`で認証状態を確認 |
| Google Drive URLからファイルを読み取れない | ファイルの共有設定を確認するようユーザーに依頼 |
| Androidプロジェクト判定ができない | PRの差分ファイル一覧を手動確認し、ユーザーに確認 |
