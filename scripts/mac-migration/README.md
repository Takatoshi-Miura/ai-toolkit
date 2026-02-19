# Mac 移行スクリプト

移行アシスタントを使わず、Homebrew 中心で新しい Mac をセットアップするためのスクリプト。

## 使い方

### 1. 旧 Mac でエクスポート

```bash
./export.sh
```

現環境の Homebrew パッケージ・Cask・Mac App Store アプリを `Brewfile` として出力する。
生成後、Brewfile を確認して不要なパッケージがあれば削除する。

### 2. 新 Mac でセットアップ

```bash
# まず何がインストールされるか確認
./setup.sh --dry-run

# 実行（各フェーズで確認プロンプトあり）
./setup.sh
```

Xcode CLT → Homebrew → Brewfile のパッケージを順にインストールする。

## ファイル構成

| ファイル | 役割 |
|---------|------|
| `export.sh` | 旧 Mac で実行。Brewfile を自動生成 |
| `setup.sh` | 新 Mac で実行。Homebrew とパッケージを一括インストール |
| `Brewfile` | export.sh で生成されるパッケージ定義 |
