# Mac移行ワークフロー

旧Macからのエクスポート、新Macへのセットアップを実行する。
スクリプト（`scripts/export.sh`, `scripts/setup.sh`）を活用し、Claude Codeが対話的にガイドする。

## スクリプトパス

```
SCRIPT_DIR: ~/Documents/Git/ai-toolkit/skills/homebrew/scripts
```

- `export.sh` - 旧Macの環境をBrewfileとしてエクスポート
- `setup.sh` - 新Macをセットアップ（Xcode CLT → Homebrew → brew bundle install）
- `Brewfile` - エクスポートされたパッケージ定義

## TodoWrite チェックリスト

**各Phaseの開始時に `in_progress`、完了時に `completed` に更新すること：**

```
Mac移行進捗：
- [ ] Phase 1: 移行モードの選択
- [ ] Phase 2-N: (選択されたモードに応じて動的に設定)
```

---

## Phase 1: 移行モードの選択

**Phase 1開始時**: TodoWriteで「Phase 1」を `in_progress` に更新

### 1-1. ユーザーにモードを質問

AskUserQuestionツールで以下の選択肢を提示:

| # | モード | 説明 |
|---|--------|------|
| 1 | エクスポート（旧Mac） | 現環境のBrewfileを生成する |
| 2 | セットアップ（新Mac） | Brewfileからパッケージを一括インストールする |

**注意**: ユーザーの発言から明確に判断できる場合は質問をスキップしてよい。

**Phase 1完了時**: TodoWriteで「Phase 1」を `completed` に更新

---

## エクスポートモード（旧Mac）

### TodoWrite チェックリスト

```
エクスポート進捗：
- [ ] Phase 2: 前提条件の確認
- [ ] Phase 3: Brewfileの生成
- [ ] Phase 4: Brewfile内容の確認・編集
- [ ] Phase 5: 結果報告
```

### Phase 2: 前提条件の確認

**Phase 2開始時**: TodoWriteで「Phase 2」を `in_progress` に更新

#### 2-1. brew と mas の確認

```bash
brew --version
```

```bash
which mas && mas version || echo "mas未インストール"
```

masが未インストールの場合はインストールを提案:

```bash
brew install mas
```

**Phase 2完了時**: TodoWriteで「Phase 2」を `completed` に更新

### Phase 3: Brewfileの生成

**Phase 3開始時**: TodoWriteで「Phase 3」を `in_progress` に更新

#### 3-1. export.sh を実行

```bash
SCRIPT_DIR=~/Documents/Git/ai-toolkit/skills/homebrew/scripts
bash "${SCRIPT_DIR}/export.sh"
```

**export.shの動作**:
- 既存Brewfileがあればバックアップ（`.bak.タイムスタンプ`）
- `brew bundle dump --describe --force` でBrewfile生成（パッケージ説明付き）
- masが利用可能ならMac App Storeアプリも含める
- ヘッダーコメント（生成日時、ホスト名、macOSバージョン）を追加

**出力先**: `~/Documents/Git/ai-toolkit/skills/homebrew/scripts/Brewfile`

**Phase 3完了時**: TodoWriteで「Phase 3」を `completed` に更新

### Phase 4: Brewfile内容の確認・編集

**Phase 4開始時**: TodoWriteで「Phase 4」を `in_progress` に更新

#### 4-1. Brewfileの内容を表示

```bash
cat ~/Documents/Git/ai-toolkit/skills/homebrew/scripts/Brewfile
```

#### 4-2. ユーザーに内容を確認させる

以下の形式でサマリーを提示:

```
## Brewfile サマリー

| 種別 | 件数 |
|------|------|
| Tap | {count} |
| Formula | {count} |
| Cask | {count} |
| MAS | {count} |
| VSCode拡張 | {count} |

不要なパッケージがあれば教えてください。編集します。
```

ユーザーが不要パッケージを指定した場合は、Brewfileから該当行を削除する。

**Phase 4完了時**: TodoWriteで「Phase 4」を `completed` に更新

### Phase 5: 結果報告

**Phase 5開始時**: TodoWriteで「Phase 5」を `in_progress` に更新

```
## エクスポート完了

Brewfile: ~/Documents/Git/ai-toolkit/skills/homebrew/scripts/Brewfile

### 次のステップ
1. このリポジトリをコミット・プッシュしてください
2. 新しいMacでこのリポジトリをクローンしてください
3. `/homebrew` → 「Mac移行」→「セットアップ」を実行してください
```

**Phase 5完了時**: TodoWriteで「Phase 5」を `completed` に更新

---

## セットアップモード（新Mac）

### TodoWrite チェックリスト

```
セットアップ進捗：
- [ ] Phase 2: システム情報の確認
- [ ] Phase 3: Xcode CLT のインストール
- [ ] Phase 4: Homebrew のインストール
- [ ] Phase 5: Brewfileからパッケージインストール
- [ ] Phase 6: 結果報告
```

### Phase 2: システム情報の確認

**Phase 2開始時**: TodoWriteで「Phase 2」を `in_progress` に更新

#### 2-1. システム情報の取得

```bash
echo "ホスト名: $(hostname)" && echo "macOS: $(sw_vers -productVersion)" && echo "アーキテクチャ: $(uname -m)"
```

#### 2-2. Brewfileの存在確認

```bash
BREWFILE=~/Documents/Git/ai-toolkit/skills/homebrew/scripts/Brewfile
ls -la "${BREWFILE}" 2>&1
```

Brewfileが存在しない場合:
- エクスポートモードの実行を案内
- または `~/Brewfile` など別のパスにBrewfileがないか確認

**Phase 2完了時**: TodoWriteで「Phase 2」を `completed` に更新

### Phase 3: Xcode CLT のインストール

**Phase 3開始時**: TodoWriteで「Phase 3」を `in_progress` に更新

#### 3-1. Xcode CLTの確認

```bash
xcode-select -p 2>&1
```

#### 3-2. 未インストールの場合

AskUserQuestionツールでインストールを確認してから実行:

```bash
xcode-select --install
```

**注意**: GUIダイアログが表示されるため、ユーザーに手動操作を案内する。

**Phase 3完了時**: TodoWriteで「Phase 3」を `completed` に更新

### Phase 4: Homebrew のインストール

**Phase 4開始時**: TodoWriteで「Phase 4」を `in_progress` に更新

#### 4-1. Homebrewの確認

```bash
which brew && brew --version || echo "未インストール"
```

#### 4-2. 未インストールの場合

AskUserQuestionツールでインストールを確認してから実行:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Apple シリコンの場合はPATH設定を案内:

```bash
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
```

**Phase 4完了時**: TodoWriteで「Phase 4」を `completed` に更新

### Phase 5: Brewfileからパッケージインストール

**Phase 5開始時**: TodoWriteで「Phase 5」を `in_progress` に更新

#### 5-1. インストール対象のプレビュー

```bash
BREWFILE=~/Documents/Git/ai-toolkit/skills/homebrew/scripts/Brewfile
echo "Tap: $(grep -c '^tap ' ${BREWFILE} 2>/dev/null || echo 0)"
echo "Formula: $(grep -c '^brew ' ${BREWFILE} 2>/dev/null || echo 0)"
echo "Cask: $(grep -c '^cask ' ${BREWFILE} 2>/dev/null || echo 0)"
echo "MAS: $(grep -c '^mas ' ${BREWFILE} 2>/dev/null || echo 0)"
echo "VSCode: $(grep -c '^vscode ' ${BREWFILE} 2>/dev/null || echo 0)"
```

#### 5-2. ユーザー確認後にインストール

AskUserQuestionツールで確認後:

```bash
brew bundle install --file=~/Documents/Git/ai-toolkit/skills/homebrew/scripts/Brewfile --verbose --no-lock 2>&1
```

#### 5-3. インストール結果の確認

```bash
brew bundle check --file=~/Documents/Git/ai-toolkit/skills/homebrew/scripts/Brewfile 2>&1 || true
```

**Phase 5完了時**: TodoWriteで「Phase 5」を `completed` に更新

### Phase 6: 結果報告

**Phase 6開始時**: TodoWriteで「Phase 6」を `in_progress` に更新

```
## セットアップ結果

| 項目 | 結果 |
|------|------|
| Xcode CLT | {status} |
| Homebrew | {status} |
| Formula | {installed_count}件インストール |
| Cask | {installed_count}件インストール |
| MAS | {installed_count}件インストール |

### 未インストールパッケージ
{missing_packages}
```

**Phase 6完了時**: TodoWriteで「Phase 6」を `completed` に更新

---

## スクリプト直接実行（上級者向け）

スクリプトを直接実行する場合は以下のコマンドを使用:

```bash
SCRIPT_DIR=~/Documents/Git/ai-toolkit/skills/homebrew/scripts

# エクスポート
bash "${SCRIPT_DIR}/export.sh"

# セットアップ（dry-run）
bash "${SCRIPT_DIR}/setup.sh" --dry-run

# セットアップ（実行）
bash "${SCRIPT_DIR}/setup.sh"
```

## エラー対応

| エラー | 対応 |
|-------|------|
| Brewfileが見つからない | エクスポートモードの実行を案内 |
| Xcode CLTのインストールが止まる | Apple ID でサインインしているか確認 |
| `brew bundle` で特定パッケージが失敗 | 失敗パッケージを表示し、個別に `brew install` を提案 |
| masアプリのインストールに失敗 | Apple IDでApp Storeにサインイン済みか確認 |
| `Permission denied` | `sudo chown -R $(whoami) /opt/homebrew` を案内 |
