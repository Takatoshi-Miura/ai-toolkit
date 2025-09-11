---
description: Convert XCTest code to Swift Testing
argument-hint: <xctest-filename> <swift-testing-filename>
---

# 役割
あなたのタスクは指定されたXCTestのコードをSwift Testingに書き直すことです。

# 指示
$1というXCTestのファイルをSwift Testingで書き直した$2ファイルを、同じ階層に作成してください。
テスト内容やテストメソッド名などは同じものを使用すること。
日本語で回答してください。
パラメータ化が可能な場合は、積極的にargumentsを利用してテストケースをまとめてください。
@MainActor、@Suite(.serialized)を付与する場合は理由をコメントしてください。
Swift Testingでは複数のテストが並列に実行されます。それでも問題ないテスト内容か精査して、問題があるなら@Suite(.serialized)を付与してください。

テストを作成したら、テストを実行し、ビルドエラーやテストが失敗しないことを確認してタスク完了としてください。