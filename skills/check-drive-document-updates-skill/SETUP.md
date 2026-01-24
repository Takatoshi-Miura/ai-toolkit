# Google Driveファイル更新確認スキル - セットアップ

## 前提条件

このスキルはGoogle Drive APIを使用するPythonスクリプトを含んでいます。

## セットアップ確認

認証が正しく設定されているか確認：

```bash
# 更新確認テスト（1週間前を基準）
python3 ~/.claude/skills/check-drive-document-updates-skill/scripts/check_file_modified.py 2025-01-01
```

**成功時**: ファイル情報がJSON形式で出力される

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
python3 ~/.claude/skills/check-drive-document-updates-skill/scripts/check_file_modified.py 2025-01-01
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
- Google Drive API

---

## 依存パッケージ

スクリプト実行時に未インストールの場合は**自動でインストール**されます。

手動でインストールする場合：
```bash
pip install google-auth google-auth-oauthlib google-api-python-client
```

---

## 監視対象ファイルの設定

監視対象ファイルは [TARGET_FILES.md](TARGET_FILES.md) で管理します。

### 編集方法

1. `TARGET_FILES.md` を開く
2. `## ファイルリスト` セクションにURLを追加・削除
3. 形式: `- https://docs.google.com/...`

---

## トラブルシューティング

| エラー | 対応 |
|-------|------|
| `Token has been expired` | token.json を削除して再認証 |
| `invalid_grant` | token.json を削除して再認証 |
| `Access denied` | Google Cloud Console でスコープを確認 |
| pip インストール失敗 | ネットワーク接続を確認、または手動で上記コマンドを実行 |
| `TARGET_FILES.mdが見つからない` | スキルディレクトリにファイルを作成 |
| `URLからファイルIDを抽出できない` | URLが `/d/xxxxxxx/` 形式を含むか確認 |
