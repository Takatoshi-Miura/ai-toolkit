# 更新ワークフロー

## TodoWrite チェックリスト

**各Phaseの開始時に `in_progress`、完了時に `completed` に更新すること：**

```
更新進捗：
- [ ] Phase 1: フォーミュラ情報の更新
- [ ] Phase 2: パッケージのアップグレード
- [ ] Phase 3: 不要ファイルの削除
- [ ] Phase 4: Brewfileの生成
- [ ] Phase 5: 結果報告
```

## Phase 1: フォーミュラ情報の更新

**Phase 1開始時**: TodoWriteで「Phase 1」を `in_progress` に更新

### 1-1. brew update の実行

```bash
brew update
```

**成功確認**: `Already up-to-date.` または更新リストが表示された → Phase 2へ

**Phase 1完了時**: TodoWriteで「Phase 1」を `completed` に更新

---

## Phase 2: パッケージのアップグレード

**Phase 2開始時**: TodoWriteで「Phase 2」を `in_progress` に更新

### 2-1. アップグレード可能なパッケージの確認

```bash
brew outdated --greedy
```

### 2-2. 一括アップグレードの実行

```bash
brew upgrade --greedy
```

**`--greedy` フラグの意味**: auto_updates や version :latest が指定されている cask も含めてすべてアップグレードする。

**成功確認**: アップグレードが完了した（エラーなし） → Phase 3へ

**Phase 2完了時**: TodoWriteで「Phase 2」を `completed` に更新

---

## Phase 3: 不要ファイルの削除

**Phase 3開始時**: TodoWriteで「Phase 3」を `in_progress` に更新

### 3-1. cleanup の実行

```bash
brew cleanup --prune=all
```

**このコマンドの動作**:
- 古いバージョンのパッケージファイルを削除
- ダウンロードキャッシュを削除
- `--prune=all` で日数に関係なく全ての古いファイルを削除

### 3-2. autoremove の実行

```bash
brew autoremove
```

**このコマンドの動作**: 他のパッケージの依存関係としてのみインストールされ、現在不要になったパッケージを自動削除。

**成功確認**: cleanup と autoremove が完了した → Phase 4へ

**Phase 3完了時**: TodoWriteで「Phase 3」を `completed` に更新

---

## Phase 4: Brewfileの生成

**Phase 4開始時**: TodoWriteで「Phase 4」を `in_progress` に更新

### 4-1. Brewfileの出力

```bash
brew bundle dump --file=~/Brewfile --force
```

**`--force` フラグの意味**: 既存のBrewfileがあれば上書きする。

**出力先**: `~/Brewfile`

### 4-2. 生成されたBrewfileの内容を確認

```bash
cat ~/Brewfile
```

ユーザーにBrewfileの内容を提示する。

**成功確認**: Brewfileが生成され内容が確認できた → Phase 5へ

**Phase 4完了時**: TodoWriteで「Phase 4」を `completed` に更新

---

## Phase 5: 結果報告

**Phase 5開始時**: TodoWriteで「Phase 5」を `in_progress` に更新

### 5-1. サマリーの表示

以下の形式で結果をまとめて報告する：

```
## Homebrew 更新結果

| 操作 | 結果 |
|------|------|
| brew update | {update_result} |
| brew upgrade --greedy | {upgrade_count}件アップグレード |
| brew cleanup | {cleanup_result} |
| brew autoremove | {autoremove_result} |
| Brewfile生成 | ~/Brewfile に出力済み |

### アップグレードされたパッケージ
{upgraded_packages_list}

### Brewfile
~/Brewfile に現在のインストール状態を保存しました。
```

**Phase 5完了時**: TodoWriteで「Phase 5」を `completed` に更新

---

## エラー対応

| エラー | 対応 |
|-------|------|
| `brew update` で `Error: /opt/homebrew must be writable` | `sudo chown -R $(whoami) /opt/homebrew` を案内 |
| `brew upgrade` で特定パッケージが失敗 | 失敗パッケージを表示し、個別に `brew reinstall {package}` を提案 |
| `brew bundle dump` で `command not found: bundle` | `brew tap homebrew/bundle` の実行を案内 |
| ネットワークエラー | ネットワーク接続を確認し、再実行を案内 |
