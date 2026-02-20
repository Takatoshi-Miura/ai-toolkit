# 削除ワークフロー

## TodoWrite チェックリスト

**各Phaseの開始時に `in_progress`、完了時に `completed` に更新すること：**

```
削除進捗：
- [ ] Phase 1: 削除対象の特定
- [ ] Phase 2: 依存関係の確認
- [ ] Phase 3: 削除の実行
- [ ] Phase 4: 結果報告
```

## Phase 1: 削除対象の特定

**Phase 1開始時**: TodoWriteで「Phase 1」を `in_progress` に更新

### 1-1. ユーザーに削除対象を質問

AskUserQuestionツールで以下を質問：

```
削除したいパッケージ名を教えてください。

複数ある場合はスペース区切りで入力してください。
例: wget curl tree

現在インストール済みのパッケージを確認したい場合は「一覧」と入力してください。
```

### 1-2. 「一覧」と回答された場合

Brewfileを読み込んでインストール済みパッケージの一覧を表示する。

**Brewfileが存在する場合:**

```bash
cat ~/Brewfile
```

Brewfileの内容を整形してユーザーに提示する:
- `brew "xxx"` → Formulae
- `cask "xxx"` → Casks
- `tap "xxx"` → Taps
- `mas "xxx"` → Mac App Store

**Brewfileが存在しない場合:**

まずBrewfileを生成してから読み込む:

```bash
brew bundle dump --file=~/Brewfile --force && cat ~/Brewfile
```

一覧を提示した上で、改めて削除対象を質問する。

### 1-3. パッケージの存在確認

指定されたパッケージがインストールされているか確認：

```bash
brew list {package_name} 2>&1
```

インストールされていないパッケージがあれば、ユーザーに通知して除外する。

**成功確認**: 削除対象のパッケージが確定した → Phase 2へ

**Phase 1完了時**: TodoWriteで「Phase 1」を `completed` に更新

---

## Phase 2: 依存関係の確認

**Phase 2開始時**: TodoWriteで「Phase 2」を `in_progress` に更新

### 2-1. 各パッケージの依存関係を確認

```bash
# このパッケージに依存している他のパッケージ（逆依存）
brew uses --installed {package_name}

# このパッケージが依存しているパッケージ
brew deps {package_name}
```

### 2-2. 影響範囲をユーザーに提示

```
## 削除対象と影響範囲

| パッケージ | 種別 | 依存されているパッケージ |
|-----------|------|----------------------|
| {package_name} | formula/cask | {dependent_packages} |

**注意**: 依存されているパッケージがある場合、それらのパッケージが正常に動作しなくなる可能性があります。

続行しますか？
```

AskUserQuestionツールで続行を確認する。

**成功確認**: ユーザーが続行を承認した → Phase 3へ

**Phase 2完了時**: TodoWriteで「Phase 2」を `completed` に更新

---

## Phase 3: 削除の実行

**Phase 3開始時**: TodoWriteで「Phase 3」を `in_progress` に更新

### 3-1. パッケージの削除

各パッケージを順番に削除する：

```bash
# formulaeの場合
brew uninstall {package_name}

# caskの場合
brew uninstall --cask {package_name}
```

### 3-2. 不要な依存パッケージの自動削除

```bash
brew autoremove
```

**成功確認**: 全パッケージが削除された → Phase 4へ

**Phase 3完了時**: TodoWriteで「Phase 3」を `completed` に更新

---

## Phase 4: 結果報告

**Phase 4開始時**: TodoWriteで「Phase 4」を `in_progress` に更新

### 4-1. サマリーの表示

```
## 削除結果

| パッケージ | 結果 |
|-----------|------|
| {package_name} | 削除完了 / エラー |

### autoremoveで削除された依存パッケージ
{autoremoved_packages}
```

**Phase 4完了時**: TodoWriteで「Phase 4」を `completed` に更新

---

## エラー対応

| エラー | 対応 |
|-------|------|
| `No such keg` | パッケージ名のスペルを確認し、`brew search {name}` で正しい名前を検索 |
| `{package} is required by {other}` | 依存パッケージの情報を表示し、`--ignore-dependencies` の使用を提案（リスクを説明） |
| `Permission denied` | `sudo chown -R $(whoami) /opt/homebrew` を案内 |
