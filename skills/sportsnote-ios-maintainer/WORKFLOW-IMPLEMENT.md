# 実装フロー

溜まっているissueから対応対象を選択し、調査・設計・実装・クロスレビュー・PR作成まで一気通貫で行う。平日は簡単なrefactor issueがあれば優先し最大3件まで（1issueずつ順番に）対応、それ以外（平日でrefactor対象なし・土日）は1件のみ対応する。issueごとに独立したPRを作成する。マージはユーザーが手動で行う。issue選定の前に、既存openPRのコンフリクト確認・修正（Phase 0）も行う。

## TodoWrite登録

```json
[
  {"content": "Phase 0: 既存PRのコンフリクト確認・修正", "activeForm": "既存PRのコンフリクトを確認中", "status": "pending"},
  {"content": "Phase 1: issue取得・対応対象選定", "activeForm": "issueを選定中", "status": "pending"},
  {"content": "Phase 2〜6: 選定issueごとの調査・実装・レビュー・PR作成", "activeForm": "選定issueを1件ずつ処理中", "status": "pending"},
  {"content": "Phase 7: 実行ログ記録", "activeForm": "実行ログを記録中", "status": "pending"}
]
```

---

## Phase 0: 既存PRのコンフリクト確認・修正

issue選定に入る前に、リポジトリの既存openPR全件にコンフリクトが発生していないか確認する。

`gh pr list --repo Takatoshi-Miura/SportsNote_iOS --state open --json number,title,headRefName,mergeable`で全openPRを取得する。

`mergeable`が`CONFLICTING`のPRを対象とする。**該当PRが0件の場合、このPhaseは即座に終了しPhase 1へ進む**（history.mdへの記録も不要）。

対象PRが1件以上ある場合は、以下を1件ずつ順番に実行する（並行実行はしない）。

### コンフリクト解消の手順

1. `git checkout main && git pull`でmainを最新化する
2. `git checkout <PRのheadRefName>`で対象ブランチに切り替える
3. `git merge main`でmainを取り込む
4. コンフリクトが発生したファイルをRead/Editで確認し、双方の変更意図（対象PRのissue本文・完了条件を損なわないこと）を踏まえて解消する
5. swift-format実行 → ビルド実行（CLAUDE.md記載のコマンド）。失敗した場合はエラーを分析し修正、**最大3回まで**自己修正を試みる
6. コンフリクト解消・修正差分を`git add`でステージし、`git commit`する（マージコミット）

**3回ビルドに失敗した場合**: このPRのコンフリクト解消を見送る。`git merge --abort`でマージを中断し、`references/history.md`に失敗理由を記録し、`gh pr comment <PR番号> --body "..."`で自動解消を見送った旨をPRにコメントする。次の対象PRに進む（次がなければPhase 1へ）。

### クロスレビュー

Phase 5と同じ手順で、Agentツール（`general-purpose`）による独立コンテキストのクロスレビューを実施する。プロンプトは`references/REVIEW-GUIDE.md`のクロスレビュー起動方法に準拠し、「対象issue」は「対象PR（コンフリクト解消の差分）」に読み替え、差分は`git diff origin/<headRefName> <headRefName>`（マージコミット以降の差分のみ）を渡す。

- must-fix指摘がある場合: 修正し再度クロスレビュー（**最大3ラウンドまで**）
- should-fix/nitのみ、または3ラウンド経過してもmust-fix指摘が残る場合: 合格扱いとし、指摘内容をPRコメントに残す

### push・記録

1. `git push`でブランチをリモートにプッシュする（マージコミットによる通常のpushであり、force-pushは行わない）
2. `gh pr comment <PR番号> --body "..."`でコンフリクト解消・レビュー結果を該当PRにコメント追記する
3. 次の対象PRがあれば手順1に戻る。なければPhase 1へ進む

**成功確認**: 対象PR全件について解消・レビュー・push完了、またはビルド失敗で見送りを記録した → Phase 1へ

---

## Phase 1: issue取得・対応対象選定

`gh issue list --repo Takatoshi-Miura/SportsNote_iOS --state open --json number,title,labels,createdAt`で全openissueを取得する。

**issueが0件の場合、ここで即座に終了する。** `references/history.md`に「対象issueなし」と記録して終了する（AskUserQuestion等では確認しない）。

1件以上ある場合は、`references/PRIORITY-RULES.md`の「平日の簡単なrefactor優先ロジック」を先に適用する。適用条件（平日）を満たし対象issueが1件以上見つかれば、それらを対応対象リスト（最大3件）とする。適用条件を満たさない、または対象0件の場合は、同ファイルの「issue選択優先度ロジック（通常時・1件選択）」で1件を選び、それを対応対象リスト（1件）とする。

対応対象リストの各issueは、Phase 2〜6を1issueずつ独立して実行する（詳細は「Phase 2〜6: 選定issueごとの実装ループ」参照）。**候補をすべて試しても着手できるissueが1件もない場合、ここで終了する。** `references/history.md`に「対応方針が確定できず全候補をスキップ」と記録して終了する。

**成功確認**: 着手可能なissueが1件以上確定した、またはissue無し・全候補スキップで終了した → issueがあればPhase 2〜6のループへ

---

## Phase 2〜6: 選定issueごとの実装ループ

Phase 1で確定した対応対象リストの各issueについて、以下のPhase 2〜6を**1issueずつ順番に**最後まで実行する（並行実行はしない）。あるissueがPhase 2・4・5でスキップ・失敗しても、他のissueには影響しない。次のissueについて改めてPhase 2から実行する。全issue処理後にPhase 7へ進む。

### Phase 2: ラベル別調査分岐

選択したissueのラベルに応じ、`references/PRIORITY-RULES.md`の「ラベル別対応分岐」表に従って調査する（bug=再現確認、refactor=影響範囲確認、test=対象カバレッジ確認、documentation=doc/実装差分確認、enhancement=関連仕様書確認）。issue本文の「対応方針」「完了条件」を出発点とし、記載が古くなっていないか実装前に再確認する。

平日の簡単なrefactor優先ロジックで選定したissueについては、この調査で「Phase 2での再判定」（`references/PRIORITY-RULES.md`参照）も行い、変更対象ファイルが3を超える、または呼び出し元が5箇所を超えると判明した場合は「簡単ではない」としてこのissueをスキップする（次点issueへの繰り上げは行わない）。

**対応方針が無効と判断する基準（いずれか1つでも該当したら無効）**:
- issue本文に「対応方針」セクション自体が存在しない、または変更対象ファイル・やることが具体的に書かれていない（旧形式のissue等）
- 調査の結果、記載された変更対象ファイル・原因箇所が実際には確認できない、または既に対策済みで問題を再現できない
- 調査を尽くしても原因箇所・修正範囲を1つに絞り込めない（複数の仮説が残り、いずれも決め手がない）

**対応方針が無効な場合、または簡単ではないと判明した場合**: このissueへの自動着手を見送る。調査で分かったこと（見送り理由）を`gh issue comment`でissueに追記し、`references/history.md`に「対応方針を確定できずスキップ」（または「簡単でないと判明しスキップ」）と記録する。対応対象リストの次のissueに進み、Phase 2を再実行する（次のissueがなければPhase 7へ）。

**成功確認**: 調査結果が確定し、issue本文の対応方針が現状も有効と確認できた → Phase 3へ

---

### Phase 3: 設計・実装計画策定

Agentツールで`Plan`サブエージェントを起動する。

```
subagent_type: "Plan"
prompt: |
  以下のissueに基づいて実装計画を立ててください。

  ## 対象issue
  #{issue番号}: {issueタイトル}
  {issue本文全体（対応方針・完了条件チェックリストを含む）}

  ## 参照情報
  - CLAUDE.md: /Users/it6210/Documents/Git/SportsNote_iOS/CLAUDE.md
  - 仕様書: /Users/it6210/Documents/Git/SportsNote_iOS/doc/spec/（関連ファイルを確認）

  ## 作成してほしいもの
  1. issue本文の「対応方針」を踏まえた具体的な実装ステップ
  2. 既存の類似実装パターン調査（SportsNote_iOS内）
  3. 修正対象ファイルの特定（issue記載と実際の調査結果に差異があれば明記）
  4. issue本文の「完了条件」チェックリストとの対応関係
```

無人実行のためユーザー承認は行わず、Phase 5のクロスレビューで品質を担保する。

**成功確認**: 実装計画が策定された → Phase 4へ

---

### Phase 4: ブランチ作成・実装・ビルド・テスト

1. `git checkout main && git pull`でmainを最新化する
2. `git checkout -b issue-<issue番号>-<短い説明>`でブランチを作成する
3. 実装計画に従いEdit/Writeでコードを変更する（CLAUDE.mdのコーディングルールに従う）
4. swift-format実行（CLAUDE.md記載のコマンド）
5. ビルド実行（CLAUDE.md記載のコマンド）。失敗した場合はエラーを分析し修正、**最大3回まで**自己修正を試みる
6. issue本文の「完了条件」チェックリストの各項目を確認する（テストが必要な場合は`SportsNote_iOSTests/`にXCTestで追加・実行）

**3回ビルドに失敗した場合**: このissueをスキップし、`references/history.md`に失敗理由を記録する。作成済みのブランチは`main`に切り戻し、対応対象リストの次のissueに進み、Phase 2を再実行する（次のissueがなければPhase 7へ）。

**完了条件（すべて満たすこと）**:
- [ ] swift-formatが正常に完了
- [ ] ビルドが成功（BUILD SUCCEEDED）
- [ ] issue本文の完了条件チェックリストをすべて満たす

**成功確認**: 完了条件をすべて満たした → Phase 5へ

---

### Phase 5: クロスレビュー

`references/REVIEW-GUIDE.md`に従い、Agentツールで実装者とは別コンテキストのレビュー専用サブエージェント（`general-purpose`）を起動する。

- must-fix指摘がある場合: 指摘に基づき修正し、再度クロスレビューを行う。**最大3ラウンドまで**
- should-fix/nitのみの場合: 合格扱いとし、指摘内容をPR本文に残す
- 3ラウンド経過してもmust-fix指摘が残る場合: 実装を放棄せず、残った指摘をPR本文に明記した上でPhase 6に進む

各ラウンドの指摘は`references/review-insights.md`に追記する。

**成功確認**: レビューが合格、または3ラウンド上限に到達し残指摘を記録した → Phase 6へ

---

### Phase 6: PR作成・issue紐付け

1. `git push`でブランチをリモートにプッシュ
2. `gh pr create --base main --title "..." --body "..."`でPRを作成する。本文には以下を含める:
   - 概要
   - `Closes #<issue番号>`（issueとPRを自動リンクし、マージ時にissueを自動クローズさせる）
   - 変更ファイル一覧
   - ビルド・テスト結果
   - issue本文の完了条件チェックリストを転記し、チェック状態を反映
   - クロスレビューで残ったmust-fix指摘（あれば）
3. `gh issue comment <issue番号> --body "PR作成: <PR URL>"`で該当issueに直接PRリンクをコメント追記する
4. `git checkout main`でmainに戻る（対応対象リストに次のissueがある場合、Phase 2からの再実行はmainを起点に行う）

**マージは行わない。** ユーザーが内容を確認して手動でマージする。

**成功確認**: PRが作成され、issueにPRリンクがコメントされた → 対応対象リストに次のissueがあればPhase 2へ、なければPhase 7へ

---

## Phase 7: 実行ログ記録

`references/history.md`に実行日時・フローID（IMPLEMENT）・対応対象issue番号（複数件の場合は全件）・各issueの結果（PR作成完了/対応方針が確定できずスキップ/簡単でないと判明しスキップ/ビルド失敗でスキップ/レビュー上限到達）を追記する。平日の簡単なrefactor優先ロジックで複数issueを選定した場合は、その旨（何件選定し何件PR作成に至ったか）も記録する。Phase 0でコンフリクト対象PRがあった場合は、対象PR番号ごとの結果（解消・push完了/ビルド失敗で見送り）もあわせて記録する。

**連続スキップ検知**: スキップした各issue番号について、`references/history.md`の直近2件の記録が両方とも「スキップ」（対応方針が確定できず・簡単でないと判明・ビルド失敗・レビュー上限超過のいずれか）であれば、`gh issue edit <issue番号> --add-label needs-manual-follow-up`を実行し、以降の自動選択対象から除外する。

`input/feedback.md`に未反映のフィードバックがあれば、優先度判定・レビュー基準への反映を検討し、反映したら処理済みマークを付与する。

**成功確認**: history.mdの更新・連続スキップ検知が完了した → フロー完了

---

## エラー対応

| エラー | 対応 |
|-------|------|
| `gh issue list`が失敗する | 認証状態を確認し、history.mdに記録して終了 |
| `gh pr list`が失敗する（Phase 0） | 認証状態を確認し、history.mdに記録してPhase 0をスキップしPhase 1へ進む |
| `git merge main`でコンフリクト解消後もビルドが3回失敗する（Phase 0） | `git merge --abort`でマージを中断し、理由を記録して対象PRのコンフリクト解消を見送り、次の対象PRに進む（Phase 0参照） |
| issue本文の対応方針が無効（旧形式・原因箇所を特定できない等） | issueにコメントを残し、対応対象リストの次のissueでPhase 2からやり直す（Phase 1・Phase 2参照）。次のissueがなければPhase 7へ |
| Phase 2の再判定で「簡単ではない」と判明する（平日の簡単なrefactor優先ロジック選定分のみ） | issueをスキップし、対応対象リストの次のissueでPhase 2からやり直す（Phase 2参照）。次のissueがなければPhase 7へ |
| ビルドが3回失敗する | issueをスキップし理由を記録して対応対象リストの次のissueに進む（Phase 4参照）。次のissueがなければPhase 7へ |
| クロスレビューが3ラウンドでも不合格 | 実装を放棄せず残指摘をPR本文に明記してPR作成（Phase 5参照） |
| `git push`・`gh pr create`が失敗する | エラーメッセージを分析し再試行（最大3回）、失敗が続く場合はhistory.mdに記録して終了 |
| mainブランチに未コミットの変更がある | `git status`で確認し、無関係な変更ならstashしてから続行、関係する変更ならhistory.mdに記録して終了 |
