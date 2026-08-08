# issue化判定基準（観点別）

WORKFLOW-ISSUE.mdの各Phaseから参照する、観点ごとの調査手順とissue化の判定基準。issue本文フォーマットはWORKFLOW-ISSUE.mdに定義済みのため、ここでは各観点固有の調査手順と判定基準のみを扱う。

## 目次
- 不具合調査
- リファクタリング候補
- ドキュメント不足
- テスト不足

---

## 不具合調査

**調査方法**:
- ビルド警告の確認（`./gradlew assembleDebug`のログから`warning:`を含む行を抽出）
- 重要パス（RealmManager, SyncManager等の`model/manager/`配下のManagerクラス群）のコードリーディングで、nullハンドリング漏れ・競合状態・仕様書との矛盾を確認
- 既存の単体テスト実行結果（失敗しているテストがあれば不具合の手がかり）

**issue化する基準**: 再現手順を具体的に明記できるもののみ。「〜かもしれない」という推測ベースのものはissue化せず、リファクタリング候補として扱う（客観的な規約違反として説明できる場合のみ）。

**ラベル**: `bug`

---

## リファクタリング候補

**調査方法**:
- CLAUDE.mdのコーディングルール（MVVM＋Repositoryパターン、Realmアクセスは必ずRealmManager経由、論理削除の徹底等）と実装コードの照合
- `./gradlew ktlintCheck`の指摘内容の確認
- 同一パターンの重複コード（3箇所以上の重複を目安）
- 肥大化したViewModel/Composable（1ファイルの行数・責務の多さ）

**issue化する基準**: 規約違反・重複箇所を客観的に指摘できるもの（該当ファイル・行を明示できる）のみ。主観的な「読みにくい」「もっと良い書き方がある」といった評価だけのものは見送る。

**ラベル**: `refactor`

---

## ドキュメント不足

**調査方法**: 直近の`references/history.md`内、WORKFLOW-KNOWLEDGE.mdの実行記録を確認する。

**issue化する基準**: フロー1（ナレッジ蓄積）が発見したが即時修正しなかった、新規ドキュメント作成が必要な規模の欠落のみ対象とする。軽微な表記ゆれ・誤字はフロー1側で直接修正する棲み分けのため、ここではissue化しない。

**ラベル**: `documentation`

---

## テスト不足

**調査方法**:
- `app/src/test/java/com/it6210/sportsnote/`配下のファイル一覧と、`viewModel/`配下のViewModel一覧を突き合わせ、対応する`XxxViewModelTest.kt`が存在しないものを抽出
- `app/src/androidTest/java/com/it6210/sportsnote/`配下が実質空である件の確認

**issue化する基準**: 対応するテストファイルが存在しないViewModel/Managerをissue化する。インストルメンテーションテスト不在は画面ごとに分割せず1件のissueに集約する。

**ラベル**: `test`
