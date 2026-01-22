# Google Drive読み取りスキル - セットアップ

## 前提条件

このスキルはGoogle Drive APIを使用するPythonスクリプトを含んでいます。

## セットアップ確認

認証が正しく設定されているか確認：

```bash
# 読み取りテスト（任意のGoogle DriveファイルIDで実行）
python3 ~/.claude/skills/read-google-drive-skill/scripts/read_drive_file.py <fileId> sheets
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
python3 ~/.claude/skills/read-google-drive-skill/scripts/read_drive_file.py <fileId> sheets
```

token.jsonがない場合、自動でブラウザが開き認証フローが開始される。ユーザーにGoogle認証を完了してもらう。認証成功後、スキル本体へ進む。

---

## 認証ファイルの配置先

```
~/.config/google-drive-skills/
├── client_secret.json   # Google Cloud Console から取得
└── token.json           # 初回認証時に自動生成
```

**注意**: このスキルは `write-google-drive-skill` / `generate-test-item-skill` と認証設定を共有する。

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
