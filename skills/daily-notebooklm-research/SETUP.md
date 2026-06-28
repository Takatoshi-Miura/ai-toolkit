# daily-notebooklm-research - セットアップ

## 前提条件

このスキルはGoogle Docs APIを使用するPythonスクリプト（`scripts/read_doc.py`）を含む。
Googleドキュメントをフォールバック調査対象に使わない場合は、このセットアップは不要。

## 認証ファイルの配置先

```
~/.config/google-drive-skills/
├── client_secret.json   # Google Cloud Console から取得
└── token.json           # 初回認証時に自動生成
```

他スキル（`google-drive-skill`等）と認証情報を共有する設計だが、スクリプト自体はこのスキル内に自己完結している。

## セットアップ確認

```bash
python3 ~/.claude/skills/daily-notebooklm-research/scripts/read_doc.py <fileId>
```

引数省略時は当月タブ（`YYYYMM`形式）を自動選択して読み取る。タブ一覧は `--list-tabs`、特定タブの指定は `<fileId> <tabTitle>` で行う。

**成功時**: ドキュメント内容がJSON形式で出力される（タブ読み取り時は `tabTitle` フィールドも含む）

**エラー時**: 以下の認証セットアップを実行

---

## 認証セットアップ（認証エラー時）

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
python3 ~/.claude/skills/daily-notebooklm-research/scripts/read_doc.py <fileId> --list-tabs
```

token.jsonがない場合、自動でブラウザが開き認証フローが開始される。ユーザーにGoogle認証を完了してもらう。

---

## client_secret.json の取得方法

1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. プロジェクトを作成または選択
3. 「APIとサービス」→「認証情報」を開く
4. 「認証情報を作成」→「OAuth クライアント ID」
5. アプリケーションの種類: 「デスクトップアプリ」
6. JSONをダウンロード

## 必要なAPIの有効化

Google Cloud Consoleで以下のAPIを有効化：
- Google Docs API

## 依存パッケージ

```bash
pip install -r ~/.claude/skills/daily-notebooklm-research/requirements.txt
```

## トラブルシューティング

| エラー | 対応 |
|-------|------|
| `python3: command not found` | `brew install python3` (macOS) または [python.org](https://www.python.org/downloads/) からダウンロード |
| `ModuleNotFoundError` | 上記の `pip install` を実行 |
| `Token has been expired` / `invalid_grant` | `~/.config/google-drive-skills/token.json` を削除して再認証 |
| `Access denied` | Google Cloud ConsoleでGoogle Docs APIが有効化されているか確認 |
| `The caller does not have permission` | 対象ドキュメントへの閲覧権限があるか確認 |
