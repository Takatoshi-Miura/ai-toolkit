# 追加ワークフロー

## TodoWrite チェックリスト

**各Phaseの開始時に `in_progress`、完了時に `completed` に更新すること：**

```
追加進捗：
- [ ] Phase 1: パッケージの検索
- [ ] Phase 2: パッケージ情報の確認
- [ ] Phase 3: インストールの実行
- [ ] Phase 4: 結果報告
```

## Phase 1: パッケージの検索

**Phase 1開始時**: TodoWriteで「Phase 1」を `in_progress` に更新

### 1-1. ユーザーにインストールしたいパッケージを質問

AskUserQuestionツールで以下を質問：

```
インストールしたいパッケージ名（またはキーワード）を教えてください。

例:
- 正確なパッケージ名: wget, visual-studio-code
- キーワード検索: video editor, terminal emulator
```

### 1-2. パッケージの検索

```bash
# formulaeとcaskの両方を検索
brew search {keyword}
```

### 1-3. 検索結果の提示

検索結果をユーザーに提示し、インストール対象を選択させる：

```
## 検索結果: "{keyword}"

### Formulae
{formulae_results}

### Casks
{cask_results}

インストールしたいパッケージ名を入力してください（複数の場合はスペース区切り）。
```

AskUserQuestionツールで対象を確認する。

**成功確認**: インストール対象が確定した → Phase 2へ

**Phase 1完了時**: TodoWriteで「Phase 1」を `completed` に更新

---

## Phase 2: パッケージ情報の確認

**Phase 2開始時**: TodoWriteで「Phase 2」を `in_progress` に更新

### 2-1. パッケージ情報の取得

```bash
brew info {package_name}
```

### 2-2. 情報の提示と確認

```
## パッケージ情報

| 項目 | 内容 |
|------|------|
| パッケージ名 | {name} |
| バージョン | {version} |
| 説明 | {description} |
| 種別 | formula / cask |

インストールしてよろしいですか？
```

AskUserQuestionツールで続行を確認する。

**成功確認**: ユーザーが続行を承認した → Phase 3へ

**Phase 2完了時**: TodoWriteで「Phase 2」を `completed` に更新

---

## Phase 3: インストールの実行

**Phase 3開始時**: TodoWriteで「Phase 3」を `in_progress` に更新

### 3-1. パッケージのインストール

```bash
# formulaeの場合
brew install {package_name}

# caskの場合
brew install --cask {package_name}
```

### 3-2. インストール後の確認

```bash
brew list {package_name}
```

**成功確認**: パッケージが正常にインストールされた → Phase 4へ

**Phase 3完了時**: TodoWriteで「Phase 3」を `completed` に更新

---

## Phase 4: 結果報告

**Phase 4開始時**: TodoWriteで「Phase 4」を `in_progress` に更新

### 4-1. サマリーの表示

```
## インストール結果

| パッケージ | 種別 | バージョン | 結果 |
|-----------|------|----------|------|
| {package_name} | formula/cask | {version} | インストール完了 / エラー |
```

### 4-2. 追加インストールの確認

```
他にインストールしたいパッケージはありますか？
ある場合はパッケージ名を入力してください。ない場合は「なし」と入力してください。
```

「なし」以外が入力された場合は Phase 1 に戻る。

**Phase 4完了時**: TodoWriteで「Phase 4」を `completed` に更新

---

## エラー対応

| エラー | 対応 |
|-------|------|
| `No formulae or casks found` | キーワードを変えて再検索を提案 |
| `already installed` | バージョン情報を表示し、`brew upgrade {package}` を提案 |
| cask インストールで `It seems there is already an App` | `--force` オプションの使用を提案（リスクを説明） |
| ネットワークエラー | ネットワーク接続を確認し、再実行を案内 |
