---
paths:
  - "**/*.kt"
  - "**/*.java"
  - "**/res/**/*.xml"
  - "**/build.gradle*"
  - "**/AndroidManifest.xml"
---

# Android開発ルール

Androidプロジェクトのコード作成・修正時に適用されるルール。

## 言語

- 新規コードは**Kotlin**で書く
- Javaは既存コードの修正のみ許容

## Coroutine / Flow

- ViewModelでは `viewModelScope` を使用する
- UIへのデータ公開は `StateFlow` または `SharedFlow` を使用する
- `GlobalScope` は使用しない
- 例外処理は `CoroutineExceptionHandler` またはtry-catchで適切に行う

## Jetpack Compose

- 新規画面は Compose を優先する
- Composable関数は**副作用を持たない**ようにする
- 状態管理は `remember` / `rememberSaveable` を適切に使い分ける

## ライフサイクル

- Activity/Fragmentのライフサイクルに応じたリソース解放を行う
- `onDestroy` でのリソースリーク防止を確認する
- `repeatOnLifecycle` でFlowのcollectを行う

## テスト

- 単体テストは JUnit + MockK を使用する
- UIテストは Espresso または Compose Testing を使用する
- カバレッジ計測は JaCoCo を使用する

## セキュリティ

- ハードコードされたAPIキー・シークレットを含めない
- SharedPreferencesの機密データは EncryptedSharedPreferences を使用する
- WebViewの `setJavaScriptEnabled(true)` は必要最小限に限定する

## コードレビュー

`android-code-review` スキルのレビュー観点と本ルールは整合している。
実装時からこのルールに従うことで、レビュー指摘を事前に防止する。
