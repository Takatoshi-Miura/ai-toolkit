# health-advisor - セットアップ

## 前提条件

Claudeの以下の2つのコネクタを接続する。OAuthトークンを使うスクリプトは使わない。

| コネクタ | 用途 |
|---------|------|
| Google Drive | スプレッドシートの読み取り（xlsxエクスポート、両フロー）、健康診断PDFの読み取り |
| Google Sheets | 「食事」シートへの書き込み（記録フロー） |

スクリプトはPython 3.9以上の標準ライブラリのみで動く（pip不要）。

## 初回準備

1. 「食事」シートの1行目を [CONFIG.md](CONFIG.md)「食事シートについて」の11列にする
2. Driveに健康診断フォルダを用意し、フォルダIDをCONFIG.mdの `drive.checkup_folder_id` に書く
3. 健康診断フォルダに `健康診断_YYYYMMDD.pdf` の名前でPDFを置く（新しい健診を受けたら追加する）

## Claude.aiへのアップロード

1. スキルディレクトリで以下を実行し、zipを作る（`input/`・`output/`・README等は含まれない。Claude.aiが受け付けないfrontmatterの項目はzip側から自動で除く）

   ```bash
   bash scripts/package_skill.sh
   ```

2. Claude.aiの「設定 > 機能 > スキル」から、できた `~/Downloads/health-advisor.zip` をアップロードする（既存があれば置き換える）
3. CONFIG.md・WORKFLOW・references・scripts を変更したら、1〜2をやり直す（ローカルのスキルディレクトリが正本）

## ルーチン登録（Claude.ai）

[SKILL.md](SKILL.md)「ルーチン登録例」のプロンプトで2つ登録し、どちらもGoogle Drive・Google Sheetsコネクタを有効にする。

## セットアップ確認

1. Google Sheetsコネクタの `get_values` で `'食事'!A1:K1` を読み、CONFIG.mdの「食事シートについて」に記載の列構成が返ることを確認する
2. Google Driveコネクタの `download_file_content` で、CONFIG.mdの `meals.url` のスプレッドシートをxlsxエクスポートし、結果がファイルに保存されることを確認する
3. 保存されたファイルで `read_sheets_export.py`（reportモード）を実行し、`success: true` が返ることを確認する
4. Artifactツールの `read_file` で、CONFIG.mdの `artifact.url` の `data/state.json` が読めることを確認する

## トラブルシューティング

| エラー | 対応 |
|-------|------|
| コネクタのツールが見つからない・認証エラー | Claudeの設定でコネクタを再接続する。ローカルで再接続によりツール名（`mcp__<コネクタID>__...`）が変わった場合は、SKILL.mdの `allowed-tools` を修正する（本文はコネクタ名で書いているため修正不要） |
| ヘッダーが一致しない | 対象シートの1行目と、CONFIG.mdの `sheet_name` を確認する |
| xlsxエクスポートの結果がファイルに保存されない | その環境ではこのスキルは動かない。ローカルのClaude Codeで実行する |
| `python3: command not found` | `brew install python3` (macOS) または [python.org](https://www.python.org/downloads/) からダウンロード |
