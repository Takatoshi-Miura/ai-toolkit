# OpenSpec プロポーザル作成ワークフロー

OpenSpecの変更（change）を新規作成するワークフロー。ai-code-trackerの利用可否を確認・セットアップした上で、`/opsx:new` スキルに処理を委譲する。

## TodoWrite登録

```json
[
  {"content": "Phase 1: ai-code-tracker の確認・セットアップ", "activeForm": "ai-code-tracker を確認・セットアップ中", "status": "pending"},
  {"content": "Phase 2: /opsx:new の実行", "activeForm": "/opsx:new を実行中", "status": "pending"}
]
```

---

## Phase 1: ai-code-tracker の確認・セットアップ

### 1-1. aict コマンドの利用可否チェック

以下のコマンドを実行して `aict` が利用可能か確認する:

```bash
aict --version
```

### 1-2. 結果に応じた分岐

**利用可能な場合**（バージョンが表示された場合）:
- 「aict が利用可能です（バージョン: {表示されたバージョン}）」と報告
- Phase 2 へ進む

**利用不可の場合**（コマンドが見つからない等）:
- ユーザーに「aict が見つかりません。セットアップを実行します。」と報告
- **1-3. 自動セットアップ** へ進む

### 1-3. 自動セットアップ

以下の手順を順番に実行する。各ステップでエラーが発生した場合はユーザーに報告して指示を仰ぐ。

#### Step 1: Go の確認・インストール

```bash
go version
```

- Go が利用可能 → Step 2 へ
- Go が未インストール → 以下を実行:

```bash
brew install go
```

#### Step 2: PATH 設定の確認

```bash
echo $PATH | grep -q "$(go env GOPATH)/bin" && echo "OK" || echo "NOT_SET"
```

- `OK` → Step 3 へ
- `NOT_SET` → 以下を実行:

```bash
echo 'export PATH="$(go env GOPATH)/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

#### Step 3: aict のインストール

```bash
go install github.com/y-hirakaw/ai-code-tracker/cmd/aict@latest
```

インストール完了後、バージョン確認:

```bash
aict --version
```

バージョンが表示されればインストール成功。

#### Step 4: リポジトリでの初期化

現在の作業ディレクトリ（リポジトリルート）で以下を実行:

```bash
aict init
aict setup-hooks
```

**注意**: `aict setup-hooks` により `.claude/settings.json` に hooks 設定が追加される。必要に応じてユーザーに設定の確認を促す。

### 1-4. セットアップ完了の確認

セットアップ結果をユーザーに報告:

```
aict セットアップ完了:
- aict バージョン: {バージョン}
- リポジトリ初期化: 完了
- hooks 設定: 追加済み
```

Phase 2 へ進む。

---

## Phase 2: /opsx:new の実行

### 2-1. /opsx:new スキルの呼び出し

Skillツールで `/opsx:new` を呼び出す:

```
skill: "opsx:new"
```

以降は `/opsx:new` スキルの指示に従って進行する。

---

## 注意事項

- このワークフローの主な役割は aict の利用可否チェックとセットアップ
- 実際のプロポーザル作成処理は `/opsx:new` スキルが担当する
- aict のセットアップには Go と Homebrew が前提として必要
