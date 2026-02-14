---
name: code-diff-and-coverage
description: |
  指定期間内のコード差分を取得し、変更ファイルのテストカバレッジを計測する。
  Pythonスクリプトでgit log解析とJaCoCoレポート抽出を自動化。
  「コードカバレッジ」「カバレッジ計測」「テストカバレッジ」「コード差分」
  「差分とカバレッジ」「変更ファイルのテスト」「カバレッジ」などで自動発動。
allowed-tools: Bash, Read, TodoWrite, AskUserQuestion
user-invocable: true
---

# コード差分 & カバレッジ計測スキル

指定期間のコード差分を取得し、変更ファイルのテストカバレッジ（JaCoCo Instruction Coverage）を計測する。

## スクリプト

| スクリプト | 用途 |
|-----------|------|
| `~/.claude/skills/code-diff-and-coverage/scripts/git_diff_analyzer.py` | Git差分分析 |
| `~/.claude/skills/code-diff-and-coverage/scripts/jacoco_coverage_extractor.py` | JaCoCoカバレッジ抽出 |

## ワークフロー

### Phase 0: Todo登録

TodoWriteツールで以下のフェーズをpending登録する:
1. 情報収集
2. コード差分取得
3. カバレッジ計測
4. 結果報告

### Phase 1: 情報収集

以下の情報が提供されていなければ、ユーザーに質問して取得する:

| 項目 | 説明 | デフォルト |
|------|------|-----------|
| リポジトリパス | Gitリポジトリの絶対パス | `~/Documents/Git/automata-android` |
| 期間 | 開始日・終了日（YYYY-MM-DD） | なし（必須） |
| 作者 | git log --author に渡す値 | `takatoshi.miura` |

**成功確認**: 3つの情報が揃っていること

### Phase 2: コード差分取得

`git_diff_analyzer.py` を実行してコード差分を取得する:

```bash
python3 ~/.claude/skills/code-diff-and-coverage/scripts/git_diff_analyzer.py \
  "<リポジトリパス>" "<作者>" "<開始日>" "<終了日>"
```

JSON出力から以下をユーザーに表形式で報告する:
- リポジトリ名・期間・ユーザー名
- コミット数
- コミット一覧（日付・メッセージ）
- 本番用Kotlinファイルのリスト（`src/main/java` 配下の `.kt` ファイル）

**成功確認**: `"success": true` が返ること

### Phase 3: カバレッジ計測

#### Step 1: テスト実行

```bash
cd <リポジトリパス>/automata-a && ./gradlew testDevelopForTestingSourceUnitTest --continue 2>&1 | tail -10
```

> **重要**: `--continue` フラグを付けること。テスト失敗があってもexecファイルは生成される。

#### Step 2: レポート生成

```bash
cd <リポジトリパス>/automata-a && ./gradlew generateCoverageReportOnly 2>&1
```

> **重要**: `generateCoverageReport` ではなく `generateCoverageReportOnly` を使用すること。
> - `generateCoverageReport`: テスト依存あり → テスト失敗時にレポート未生成
> - `generateCoverageReportOnly`: テスト依存なし → 既存execデータからレポート生成
>
> AGP自動生成タスク `jacocoTestReportDevelopForTestingSource` は**使用禁止**（クラス不一致が発生する）

#### Step 3: コンパイルエラー対応

テストのコンパイルエラーが発生した場合:
1. エラー内容をユーザーに報告する
2. 一時修正してテスト実行するか、スキップするか確認する
3. 一時修正した場合は、Phase 4完了後に必ず元に戻す

**成功確認**: `generateCoverageReportOnly` が `BUILD SUCCESSFUL` になること

### Phase 4: 結果報告

#### Step 1: カバレッジ抽出

ユーザーが対象ファイルを指定している場合:

```bash
python3 ~/.claude/skills/code-diff-and-coverage/scripts/jacoco_coverage_extractor.py \
  "<リポジトリパス>/automata-a/app/build/reports/jacoco" \
  File1.kt File2.kt File3.kt
```

指定がない場合はPhase 2の本番用Kotlinファイルからファイル名部分のみを抽出して渡す:

```bash
python3 ~/.claude/skills/code-diff-and-coverage/scripts/jacoco_coverage_extractor.py \
  "<リポジトリパス>/automata-a/app/build/reports/jacoco" \
  ContinuousReceiptViewModel.kt ContinuousReceiptAction.kt ...
```

#### Step 2: 結果表示

JSON出力から表形式で報告する:

| ファイル名 | カバレッジ |
|-----------|:---------:|
| ファイル名.kt | 数値 |

- テストファイル（`src/test` 配下）はリストに載せない
- Compose画面・Fragment・Viewコンポーネントは除外可（ユーザーに確認）
- sealed classのサブクラスがある場合は補足として個別に表示

**成功確認**: 全対象ファイルのカバレッジが表示されること

## エラー対応表

| エラー | 原因 | 対応 |
|--------|------|------|
| `no such file or directory: ./gradlew` | 実行ディレクトリが違う | `automata-a/` 配下で実行 |
| `Classes do not match with execution data` | 不正なJaCoCoタスク使用 | `generateCoverageReportOnly` を使用 |
| コンパイルエラー | テストコードの問題 | ユーザーに報告して判断を仰ぐ |
| `BUILD FAILED` + テスト失敗 | テスト自体の失敗 | `--continue` で続行し Step 2 へ進む |
| レポートが見つからない | レポート未生成 | Step 1, 2 を順番に再実行 |
