# Google Driveスキル - セットアップ

## 前提条件

このスキルはGoogle Drive APIを使用するPythonスクリプトを含んでいます。

## 認証の共有について

このスキルは `generate-test-item-skill` と認証設定を共有する。
既にセットアップ済みの場合、追加の認証設定は不要。

**共有される認証ファイル**:
- `~/.config/google-drive-skills/client_secret.json`
- `~/.config/google-drive-skills/token.json`

## セットアップ確認

認証が正しく設定されているか確認：

```bash
# 読み取りテスト（任意のGoogle DriveファイルIDで実行）
python3 ~/.claude/skills/google-drive-skill/scripts/read_drive_file.py <fileId> sheets
```

**成功時**: ファイル内容がJSON形式で出力される

**エラー時**: 以下のセットアップを実行

---

## 認証セットアップ（認証エラー時）

認証エラーが発生した場合、以下の手順を**自動で**実行する。

### Step 1: client_secret.json のパスを質問

**AskUserQuestionツールで質問：**

```json
{
  "questions": [
    {
      "question": "Google認証用のclient_secret.jsonファイルのパスを「その他」から入力してください",
      "header": "認証設定",
      "options": [
        {"label": "パスを入力", "description": "「その他」を選択してファイルパスを入力"}
      ],
      "multiSelect": false
    }
  ]
}
```

※ client_secret.jsonがない場合は、下記「client_secret.json の取得方法」を案内する。

### Step 2: 認証ファイルを配置

```bash
mkdir -p ~/.config/google-drive-skills
cp "<ユーザーが指定したパス>" ~/.config/google-drive-skills/client_secret.json
```

### Step 3: 認証実行

```bash
python3 ~/.claude/skills/google-drive-skill/scripts/read_drive_file.py <fileId> sheets
```

token.jsonがない場合、自動でブラウザが開き認証フローが開始される。ユーザーにGoogle認証を完了してもらう。認証成功後、スキル本体へ進む。

---

## 認証ファイルの配置先

```
~/.config/google-drive-skills/
├── client_secret.json   # Google Cloud Console から取得
└── token.json           # 初回認証時に自動生成
```

## client_secret.json の取得方法

1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. プロジェクトを作成または選択
3. 「APIとサービス」→「認証情報」を開く
4. 「認証情報を作成」→「OAuth クライアント ID」
5. アプリケーションの種類: 「デスクトップアプリ」
6. JSONをダウンロード

## 必要なAPIの有効化

Google Cloud Consoleで以下のAPIを有効化：
- Google Sheets API
- Google Docs API
- Google Slides API
- Google Drive API

---

## 書き込み権限について

書き込み操作には以下のOAuthスコープが必要（auth.pyで自動設定済み）：

| 操作 | 必要なスコープ |
|------|---------------|
| スプレッドシート書き込み | `https://www.googleapis.com/auth/spreadsheets` |
| ドキュメント書き込み | `https://www.googleapis.com/auth/documents` |
| スライド書き込み | `https://www.googleapis.com/auth/presentations` |
| ドライブ全般 | `https://www.googleapis.com/auth/drive` |

**注意**: 読み取り専用スコープ（`.readonly` サフィックス付き）では書き込み操作は失敗する。
権限エラーが発生する場合は `token.json` を削除して再認証。

---

## 依存パッケージ

```bash
pip install google-auth google-auth-oauthlib google-api-python-client
```

---

## トラブルシューティング

| エラー | 対応 |
|-------|------|
| `python3: command not found` | `brew install python3` (macOS) または [python.org](https://www.python.org/downloads/) からダウンロード |
| `ModuleNotFoundError` | 上記の `pip install` を実行 |
| `Token has been expired` | token.json を削除して再認証 |
| `invalid_grant` | token.json を削除して再認証 |
| `Access denied` | Google Cloud Console でスコープを確認 |
| `The caller does not have permission` | 対象ファイルへの編集権限があるか確認、またはtoken.jsonを削除して再認証 |
| シートが見つかりません | `availableSheets` に表示されている正しいシート名を使用 |
