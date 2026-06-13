# APKインストール ワークフロー

Android端末にAPKファイルをインストールする詳細手順。

## 前提条件

- Android端末がUSBデバッグモードでPCに接続されていること
- `adb` コマンドが利用可能であること（Android SDK Platform-Tools）

---

## TodoWriteチェックリスト

このワークフロー開始時に以下をTodoWriteで登録すること:

```json
[
  {"content": "Phase 1: 接続端末の確認", "activeForm": "接続端末を確認中", "status": "pending"},
  {"content": "Phase 2: 端末の選択", "activeForm": "端末を選択中", "status": "pending"},
  {"content": "Phase 3: APKファイルの確認", "activeForm": "APKファイルを確認中", "status": "pending"},
  {"content": "Phase 4: インストールの実行", "activeForm": "APKをインストール中", "status": "pending"},
  {"content": "Phase 5: 結果の報告", "activeForm": "結果を報告中", "status": "pending"}
]
```

---

## Phase 1: 接続端末の確認

### 1-1. adb devicesを実行

```bash
adb devices
```

結果をユーザーに表示する。

**成功確認**: コマンドが実行できた → Phase 2へ

---

## Phase 2: 端末の選択

### 2-1. 接続台数に応じて分岐

- **0台の場合**:
  - 「Android端末が接続されていません」と表示
  - 以下を案内する:
    - USBケーブルで端末をPCに接続してください
    - 端末のUSBデバッグモードが有効になっているか確認してください
    - 端末に「USBデバッグを許可しますか？」のダイアログが表示されていれば許可してください
  - ユーザーが準備できたら `adb devices` を再実行して確認する

- **1台の場合**: 自動的にその端末を選択してPhase 3へ

- **2台以上の場合**: ユーザーに選択させる
  - デバイスIDと接続状態を一覧表示
  - AskUserQuestionで番号選択させる

**成功確認**: インストール先の端末が決定した → Phase 3へ

---

## Phase 3: APKファイルの確認

### 3-1. デフォルトパスを確認

デフォルトのAPKパスを確認する:

```bash
ls -la ~/Downloads/app-develop-debugOptimized.apk
```

- **ファイルが存在する場合**: そのままPhase 4へ
- **ファイルが存在しない場合**: 手順3-2へ

### 3-2. APKファイルを検索

`~/Downloads/` 内の `.apk` ファイルを検索して一覧表示:

```bash
find ~/Downloads -name "*.apk" -maxdepth 2
```

- **見つかった場合**: AskUserQuestionで選択させる
- **見つからない場合**: APKファイルのパスをユーザーに入力してもらう

**成功確認**: インストールするAPKファイルのパスが確定した → Phase 4へ

---

## Phase 4: インストールの実行

### 4-1. adb installを実行

```bash
adb -s <デバイスID> install -r <APKファイルパス>
```

- `-r` オプション: 既存アプリを上書きインストール（再インストール）

インストール結果を確認する:
- **成功時** (`Success`): Phase 5へ
- **失敗時**: エラーメッセージを表示し、下記エラー対応表に従って対処する

**成功確認**: `Success` と表示された → Phase 5へ

---

## Phase 5: 結果の報告

インストール結果をサマリーとして表示する:

```markdown
## APKインストール完了

- **インストール先端末**: <デバイスID>
- **インストールしたAPK**: <APKファイル名>
- **結果**: 成功 ✓
```

**成功確認**: サマリーを表示した → 完了

---

## エラー対応

| エラー状況 | 対処法 |
|-----------|--------|
| 端末未接続 | USBケーブルの接続確認、USBデバッグ有効化の確認を促す |
| APKファイル不存在 | 正しいパスの入力を促す、Downloadsフォルダを検索 |
| 端末がオフライン状態 | 端末でUSBデバッグの許可ダイアログを確認するよう促す |
| `INSTALL_FAILED_ALREADY_EXISTS` | `-r` オプションで上書きインストール（本ワークフローでは対応済み） |
| `INSTALL_FAILED_INSUFFICIENT_STORAGE` | 端末のストレージ空き容量を確認 |
| `INSTALL_FAILED_UPDATE_INCOMPATIBLE` | 既存アプリをアンインストールしてから再インストール |
| `INSTALL_FAILED_VERSION_DOWNGRADE` | 古いバージョンはインストールできないため、端末のアプリをアンインストール |
