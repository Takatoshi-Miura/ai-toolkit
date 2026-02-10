---
paths:
  - "**/*Test*.swift"
  - "**/*Tests*.swift"
  - "**/Tests/**/*.swift"
---

# Swift Testingコード生成ルール

Swift Testingフレームワークを用いたテストコードを記述する際のルール。

## 使用するテストフレームワーク

- テストコードはすべて [Swift Testing](https://developer.apple.com/documentation/testing) を使用する
- XCTest は使用しない

## テストコードの記述形式

- `struct` を用いて記述する（`class` は使用しない）
- アサーションには `#expect` マクロを使用する
- 失敗時の処理には `Issue.record` を使用する

## パラメータ化の活用

- パラメータ化（parameterized test）が利用できる場合は積極的に活用する
- パラメータ数が多くなりすぎる場合は、適宜メソッドを分割する

## @MainActor の付与

- UI操作（ボタンタップ、画面遷移、Viewの表示状態確認など）を含むテストメソッドには `@MainActor` を付与する

## @Suite(.serialized) の適用条件

以下のいずれかを利用するテストでは同期実行とする:

- `UserDefaults`
- データベース（`Realm` 等）
- `NotificationCenter`
- シングルトン（共有インスタンス）

## テストの実行と確認

テストコード生成後は必ず以下を確認する:
- コンパイルエラーがないこと
- すべてのテストが成功すること

## 命名

- テストケース名・メソッド名は、テスト対象の動作や条件が明確に分かる名前にする
- 必要に応じてモックやスタブを利用して副作用を抑制する
