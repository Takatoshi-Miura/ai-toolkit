---
paths:
  - "**/*.swift"
---

# SportsNote_iOS開発ルール

SportsNote_iOSのコード作成・修正時に適用されるアーキテクチャ規約。

## View/ディレクトリ構成

- 機能ごとにディレクトリを分け、関連するComponentも同じ機能ディレクトリ配下に置く
  - 例: Menu関連のComponentは `View/Setting/` に置く（MenuはSetting機能の一部）
  - 例: Group関連のComponentは `View/Group/` に置く
- メイン画面以外のコンポーネントは機能ディレクトリ内の `Component` 等のサブディレクトリに分割する
