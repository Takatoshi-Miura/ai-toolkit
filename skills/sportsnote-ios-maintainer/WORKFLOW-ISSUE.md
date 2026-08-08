# issue作成フロー

不具合調査・ユーザー要望・リファクタリング候補・ドキュメント不足・テスト不足の5観点でSportsNote iOSを調査し、GitHub issueを作成する。各issueは「具体的にどう対応するか」が分かる粒度（対応方針・完了条件チェックリスト付き）で作成する。

## TodoWrite登録

```json
[
  {"content": "Phase 1: 既存issue取得と重複チェック準備", "activeForm": "既存issueを取得中", "status": "pending"},
  {"content": "Phase 2: 不具合調査", "activeForm": "不具合を調査中", "status": "pending"},
  {"content": "Phase 3: ユーザー要望の取り込み", "activeForm": "ユーザー要望を確認中", "status": "pending"},
  {"content": "Phase 4: リファクタリング候補抽出", "activeForm": "リファクタリング候補を抽出中", "status": "pending"},
  {"content": "Phase 5: ドキュメント不足の検出", "activeForm": "ドキュメント不足を検出中", "status": "pending"},
  {"content": "Phase 6: テスト不足の検出", "activeForm": "テスト不足を検出中", "status": "pending"},
  {"content": "Phase 7: input/requests.mdの更新", "activeForm": "処理済みマークを付与中", "status": "pending"},
  {"content": "Phase 8: 実行ログ記録", "activeForm": "実行ログを記録中", "status": "pending"}
]
```

---

## Phase 1: 既存issue取得と重複チェック準備

`gh issue list --repo Takatoshi-Miura/SportsNote_iOS --state open --limit 100 --json number,title,labels,body`で既存issueを取得する。以降の全観点で、新規候補と既存issueのタイトル・内容を突き合わせ、実質同一なら新規作成せず`gh issue comment`で既存issueに補足情報を追記するに留める。

初回実行時（`references/LABEL-TAXONOMY.md`記載のラベルがリポジトリに存在しない場合）、`gh label create`で`refactor`・`test`・`needs-manual-follow-up`ラベルを作成する。

**成功確認**: 既存issue一覧が取得できた → Phase 2へ

---

## Phase 2: 不具合調査

`references/ISSUE-CRITERIA.md`の「不具合調査」手順に従い、ビルド警告・重要パス（RealmManager/SyncManager等）のコードリーディングで矛盾を検出する。再現手順を明記できるもののみissue化する（推測ベースのものはPhase 4のリファクタリング候補に回す）。issue本文は`references/ISSUE-CRITERIA.md`のフォーマットに従い、`bug`ラベルを付与する。

**成功確認**: 発見した不具合をissue化した（0件でもよい） → Phase 3へ

---

## Phase 3: ユーザー要望の取り込み

`input/requests.md`を読み、未処理（取消線が付いていない）の要望を1項目=1issueで起票する。曖昧な要望でも質問はせず、「不明点」として本文に明記した上でissue化する。`enhancement`ラベルを付与する。

**成功確認**: 未処理の要望をすべてissue化した（対象なしでもよい） → Phase 4へ

---

## Phase 4: リファクタリング候補抽出

`references/ISSUE-CRITERIA.md`の「リファクタリング候補」手順に従い、CLAUDE.mdのコーディングルール違反（MVVM分離、RealmManager経由必須等）・重複コード・肥大化したViewModel/Viewを検出する。客観的に規約違反・重複が説明できるもののみissue化する（主観的な「読みにくい」は見送る）。`refactor`ラベルを付与する。

**成功確認**: リファクタリング候補をissue化した（0件でもよい） → Phase 5へ

---

## Phase 5: ドキュメント不足の検出

直近の`references/history.md`（WORKFLOW-KNOWLEDGE.mdの実行記録）を確認し、フロー1が発見したが即時修正しなかった大きめの欠落（新規ドキュメント作成級）をissue化する。軽微な表記ゆれはフロー1側で直接直す棲み分けのため対象外。`documentation`ラベルを付与する。

**成功確認**: ドキュメント不足をissue化した（0件でもよい） → Phase 6へ

---

## Phase 6: テスト不足の検出

`SportsNote_iOSTests/`とView/ViewModel一覧を突き合わせ、対応する`XxxViewModelTests.swift`が存在しないものを検出する。`SportsNote_iOSUITests/`が実在しない件も1件に集約してissue化する（画面ごとに分割しない）。`test`ラベルを付与する。

**成功確認**: テスト不足をissue化した（0件でもよい） → Phase 7へ

---

## Phase 7: input/requests.mdの更新

Phase 3で取り込んだ要望に、削除ではなく取消線（`~~要望文~~`）で処理済みマークを付与し、対応するissue番号を追記する（監査性を残すため）。

**成功確認**: 処理済みマークの付与が完了した → Phase 8へ

---

## Phase 8: 実行ログ記録

`references/history.md`に実行日時・フローID（ISSUE）・観点別の作成issue数・スキップ理由（既存issueと重複した場合等）を追記する。

**成功確認**: history.mdの更新が完了した → フロー完了

---

## issue本文フォーマット

既存issue（#1, #5）の構成をベースに、「対応方針」「完了条件」を必須項目として含める。フロー3（実装）が本文を読むだけで着手内容と完了判定を判断できる粒度にする。

```markdown
## 概要
{1-2文}

## 背景 / 再現手順 / 対象箇所
{観点ごとに異なる小見出し。ファイルパス・関数名・画面名など具体的な箇所を明記}

## 対応方針
- **変更対象ファイル**: {具体的なパス。調査時点で特定できる範囲まで}
- **やること**: {箇条書き。着手すればそのまま実装できる粒度。例:「RealmManagerのfetchXxxにnilガードを追加」}
- **やらないこと（スコープ外）**: {隣接するが対象外の変更を明記し、実装時のスコープ拡大を防ぐ}

## 完了条件
- [ ] {対応方針の「やること」各項目に対応する、検証可能な完了条件を1項目ずつ}
- [ ] ビルド成功（BUILD SUCCEEDED）
- [ ] 既存テストがすべて成功（テスト不足issueの場合は新規テストの追加・成功も含む）
- [ ] {観点固有の完了条件があれば追加。例: bugなら「再現手順で問題が再現しないこと」、documentationなら「該当doc/spec/*.mdが更新されていること」}

## 追加情報
- **優先度**: 高/中/低
- **種別**: bug/enhancement/refactor/documentation/test
```

「対応方針」「完了条件」が具体化できない場合（コード調査だけでは変更対象ファイルや完了判定基準を特定できない場合）は、issue化を見送るか、「調査自体をやること」として明記し、フロー3側で追加調査から始める前提を残す。曖昧なまま丸投げしない。

---

## エラー対応

| エラー | 対応 |
|-------|------|
| `gh issue create`が失敗する | 認証状態（`gh auth status`）を確認し、history.mdに記録して当該issueをスキップ |
| ラベルが存在しない | `gh label create`で`references/LABEL-TAXONOMY.md`の定義に従い作成してから再実行 |
| `input/requests.md`が存在しない | 要望取り込み（Phase 3）はスキップし、他の観点は継続する |
