---
name: android-code-review
description: Androidプロジェクトのコードレビューを専門的に実施。GitHub PRまたはローカル差分のレビュー依頼時、対象にAndroidファイル（.kt、.java、.xml）やAndroidプロジェクト構造（build.gradle、AndroidManifest.xml）が含まれる場合に自動発動。「レビューして」「PRレビュー」「コードレビュー」「差分見て」「変更確認して」などの依頼で、Activity/Fragment/Serviceのライフサイクル、Jetpack、Coroutine、画面遷移、状態管理、非同期処理、UI/UX、セキュリティ、パフォーマンスなどAndroid固有の観点で包括的にレビュー。Kotlin/Java/XMLのコード品質、リソース管理、メモリリーク防止も確認。
allowed-tools: mcp__mcp-gh-pr-mini__*, mcp__mcp-google-drive__g_drive_read_file, Read, Grep, Glob, Bash
---

# AndroidコードレビューSkill

Androidプロジェクト（Kotlin/Java/XML）のコードレビューを専門的に実施します。

## 発動条件

このスキルは以下の状況で自動的に適用されます：

- GitHub PR URLが含まれ、レビューを依頼されたとき（PRにAndroidファイルが含まれる場合）
- 「差分をレビューして」「変更を確認して」などの依頼（カレントディレクトリがAndroidプロジェクトの場合）
- 変更ファイルに `.kt`, `.java`, `.xml`, `.gradle`, `.kts` が含まれる場合
- プロジェクトに `AndroidManifest.xml`, `build.gradle`, `app/src/main/` が存在する場合

## 手順

### Phase 1: 情報収集

1. **追加情報の確認（任意）**
   - PBI（Product Backlog Item）のURL
   - 概要設計書のURL
   - テスト項目書のURL
   - Figmaデザインのリンク

2. **PR/差分情報の取得**

   **GitHub PRの場合:**
   ```bash
   # PR情報の取得
   gh pr view <PR番号> --repo owner/repo

   # 変更差分の取得
   gh pr diff <PR番号> --repo owner/repo
   ```

   **ローカル差分の場合:**
   ```bash
   # ステージング済み + 未ステージングの差分
   git diff HEAD

   # または特定ブランチとの差分
   git diff <base-branch>..HEAD
   ```

3. **追加資料の読み取り（提供された場合）**
   - Google Driveの場合: `g_drive_read_file` で読み取り
   - Redmineの場合: `redmine_get_detail` で読み取り

### Phase 2: Androidコードレビュー

4. **変更ファイルの分類**

   変更されたファイルを以下のカテゴリに分類:

   | カテゴリ | ファイルパターン | 重点確認ポイント |
   |---------|-----------------|-----------------|
   | Activity/Fragment | `*Activity.kt`, `*Fragment.kt` | ライフサイクル管理 |
   | ViewModel | `*ViewModel.kt` | 状態管理、LiveData/Flow |
   | Repository/UseCase | `*Repository.kt`, `*UseCase.kt` | データ層設計 |
   | UI/Compose | `*.xml`, `*Composable.kt` | UI構造、アクセシビリティ |
   | DI | `*Module.kt`, `*Component.kt` | 依存関係 |
   | テスト | `*Test.kt`, `*AndroidTest.kt` | カバレッジ、品質 |
   | ビルド設定 | `*.gradle`, `*.kts` | 依存関係、設定 |

5. **レビュー観点チェック**

   ~/Documents/Git/ai-toolkit/task/review-pull-request.md の観点に従い、特に以下のAndroid固有項目を重点的にレビュー:

   #### Androidプラットフォーム／ライフサイクル
   - Activity/Fragment/Serviceのライフサイクル管理
   - 画面回転・バックグラウンド復帰・低メモリ時の動作
   - Context/Drawable/Stringのリソース管理（リーク防止）
   - Jetpackアーキテクチャコンポーネントの適切な利用
   - Main/IOスレッド切り替え
   - プロセス終了時の状態保持・復元
   - Coroutineとライフサイクルの連携（キャンセル漏れ防止）

   #### 画面遷移・状態管理・非同期処理
   - 画面遷移・戻る動作の一貫性
   - Bundle/Intent/Navigation Argsのデータ受け渡し
   - 二重タップ・多重遷移防止
   - バックスタック復帰時の状態維持
   - Deep Link対応
   - ローディング状態管理
   - 二重送信防止
   - オフライン時の処理
   - Coroutineスコープの選択
   - Galaxy端末のIME問題

   #### パフォーマンス・リソース
   - メインスレッドでの重い処理
   - 不必要な再描画・再計算
   - RecyclerViewの最適化（ViewHolder再利用、DiffUtil）
   - 画像読み込みの最適化
   - メモリ使用量・OOM防止
   - メモリリーク（Context保持、リスナー未解除）
   - ネットワーク通信の最適化

### Phase 3: レビュー結果の出力

6. **レビュー結果をユーザーに共有**

## 出力形式

```markdown
## Androidコードレビュー結果

### 概要
- **PR/差分**: [PR番号 or ブランチ名]
- **変更ファイル数**: X件
- **Androidファイル内訳**: Kotlin: X件, Java: X件, XML: X件, その他: X件

---

### レビューサマリー

| 観点 | 評価 | 指摘件数 | 重要度高 |
|------|------|----------|----------|
| ライフサイクル管理 | ⚪/△/✕ | X件 | X件 |
| 画面遷移・状態管理 | ⚪/△/✕ | X件 | X件 |
| 非同期処理 | ⚪/△/✕ | X件 | X件 |
| UI/UX | ⚪/△/✕ | X件 | X件 |
| セキュリティ | ⚪/△/✕ | X件 | X件 |
| パフォーマンス | ⚪/△/✕ | X件 | X件 |
| テスト | ⚪/△/✕ | X件 | X件 |

---

### 指摘事項

#### [MUST] 修正必須
1. **[ファイル名:行番号]** - [観点カテゴリ]
   - 問題: [具体的な問題点]
   - 理由: [なぜ問題なのか]
   - 修正案: [具体的な修正方法]

#### [SHOULD] 修正推奨
1. **[ファイル名:行番号]** - [観点カテゴリ]
   - 問題: [具体的な問題点]
   - 理由: [なぜ問題なのか]
   - 修正案: [具体的な修正方法]

#### [COULD] 改善提案
1. **[ファイル名:行番号]** - [観点カテゴリ]
   - 提案: [改善内容]
   - 効果: [改善による効果]

---

### 良い点
- [認めるべき良い実装ポイント]

---

### 確認事項
- [ ] [確認が必要な事項]
```

## 注意事項

- PRレビューの場合、対象ブランチにチェックアウトされているか確認が必要
- 追加のコンテキスト（PBI、概要設計書、テスト項目書など）が提供された場合は、それも考慮してレビューする
- 日本語で回答すること
- 詳細なレビュー観点は ~/Documents/Git/ai-toolkit/task/review-pull-request.md を参照
