# 移行ワークフロー（App Store → Homebrew）

## 前提条件

`mas`（Mac App Store CLI）が必要。未インストールの場合は自動でインストールする:

```bash
brew install mas
```

## TodoWrite チェックリスト

**各Phaseの開始時に `in_progress`、完了時に `completed` に更新すること：**

```
移行進捗：
- [ ] Phase 1: App Storeアプリの一覧取得
- [ ] Phase 2: Homebrew cask版の照合
- [ ] Phase 3: 移行対象の選択
- [ ] Phase 4: 移行の実行
- [ ] Phase 5: 結果報告
```

## Phase 1: App Storeアプリの一覧取得

**Phase 1開始時**: TodoWriteで「Phase 1」を `in_progress` に更新

### 1-1. masコマンドの確認

```bash
which mas || brew install mas
```

### 1-2. App Storeアプリの一覧を取得

```bash
mas list
```

**出力形式**: `アプリID アプリ名 (バージョン)`

取得した一覧をユーザーに提示する。

**成功確認**: App Storeアプリの一覧が取得できた → Phase 2へ

**Phase 1完了時**: TodoWriteで「Phase 1」を `completed` に更新

---

## Phase 2: Homebrew cask版の照合

**Phase 2開始時**: TodoWriteで「Phase 2」を `in_progress` に更新

### 2-1. 各アプリのcask版を検索

App Storeアプリ一覧の各アプリについて、Homebrew cask版が存在するか検索する:

```bash
brew search --cask {app_name}
```

### 2-2. 照合結果の提示

以下の形式で結果を整理してユーザーに提示する:

```
## App Store → Homebrew 照合結果

### cask版あり（移行可能）
| App Storeアプリ | cask名 | 備考 |
|----------------|--------|------|
| {app_name} | {cask_name} | - |

### cask版なし（移行不可）
| App Storeアプリ | 備考 |
|----------------|------|
| {app_name} | cask版が見つかりません |
```

**成功確認**: 照合結果を提示できた → Phase 3へ

**Phase 2完了時**: TodoWriteで「Phase 2」を `completed` に更新

---

## Phase 3: 移行対象の選択

**Phase 3開始時**: TodoWriteで「Phase 3」を `in_progress` に更新

### 3-1. ユーザーに移行対象を選択させる

AskUserQuestionツールで以下を質問:

```
移行したいアプリを選択してください。

cask版が存在するアプリのみ移行可能です。
複数ある場合はスペース区切りで入力してください。
「全部」と入力するとcask版があるすべてのアプリを移行します。

⚠️ 注意: App Store版をアンインストールすると、アプリ内データが失われる場合があります。
移行前にデータのバックアップを推奨します。
```

**成功確認**: 移行対象が確定した → Phase 4へ

**Phase 3完了時**: TodoWriteで「Phase 3」を `completed` に更新

---

## Phase 4: 移行の実行

**Phase 4開始時**: TodoWriteで「Phase 4」を `in_progress` に更新

### 4-1. 各アプリを順番に移行

各アプリについて以下の手順で移行する:

#### Step 1: App Store版のアンインストール

```bash
mas uninstall {app_id}
```

**`mas uninstall` で削除できない場合**: 手動で `/Applications/{app_name}.app` を削除するか、ユーザーに手動削除を案内する。

#### Step 2: Homebrew cask版のインストール

```bash
brew install --cask {cask_name}
```

#### Step 3: インストール確認

```bash
brew list --cask {cask_name}
```

### 4-2. エラー時の対応

アプリごとに成功/失敗を記録し、失敗した場合は次のアプリに進む。
失敗したアプリは Phase 5 で報告する。

**成功確認**: 全アプリの移行処理が完了した → Phase 5へ

**Phase 4完了時**: TodoWriteで「Phase 4」を `completed` に更新

---

## Phase 5: 結果報告

**Phase 5開始時**: TodoWriteで「Phase 5」を `in_progress` に更新

### 5-1. サマリーの表示

```
## 移行結果

| アプリ名 | App Store → cask | 結果 |
|---------|-----------------|------|
| {app_name} | {cask_name} | 移行完了 / エラー |

### 成功: {success_count}件
### 失敗: {fail_count}件

{失敗がある場合は詳細とリカバリ手順を提示}
```

### 5-2. 失敗アプリのリカバリ案内

失敗したアプリがある場合:

```
### リカバリ手順

以下のアプリはApp Storeから再インストールできます:
- {app_name}: `mas install {app_id}`
```

**Phase 5完了時**: TodoWriteで「Phase 5」を `completed` に更新

---

## エラー対応

| エラー | 対応 |
|-------|------|
| `mas: command not found` | `brew install mas` を実行 |
| `mas uninstall` で `Error: No installed apps` | アプリIDを確認し、`mas list` で再取得 |
| `mas uninstall` で権限エラー | `sudo mas uninstall {app_id}` を提案、または手動削除を案内 |
| cask インストールで `already an App` | `--force` オプションの使用を提案（先にApp Store版の削除を確認） |
| 移行後にアプリが起動しない | `brew reinstall --cask {cask_name}` を提案 |
