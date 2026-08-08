# ナレッジ蓄積フロー

SportsNote iOSのコードを調査し、`doc/spec/`の仕様書とプロジェクトルール（`CLAUDE.md`）を実装の実体に合わせて更新する。承認は不要で、確定情報として直接更新する。

## TodoWrite登録

```json
[
  {"content": "Phase 1: 調査範囲の決定", "activeForm": "調査範囲を決定中", "status": "pending"},
  {"content": "Phase 2: コード調査", "activeForm": "コードを調査中", "status": "pending"},
  {"content": "Phase 3: doc/への反映", "activeForm": "doc/を更新中", "status": "pending"},
  {"content": "Phase 4: ルールへの反映", "activeForm": "CLAUDE.md等を確認中", "status": "pending"},
  {"content": "Phase 5: コミット・マージ・ブランチ削除", "activeForm": "コミット・マージ・ブランチ削除を実行中", "status": "pending"},
  {"content": "Phase 6: 実行ログ記録", "activeForm": "実行ログを記録中", "status": "pending"}
]
```

---

## Phase 1: 調査範囲の決定

`references/knowledge-map.md`を読み、前回スキャン済みの範囲を確認する。1回の実行につき調査対象を1〜2ディレクトリ程度に絞る（`Model/`, `ViewModel/`, `View/<サブディレクトリ>`等をローテーションする）。全件走査はコンテキスト消費が大きいため行わない。

`git checkout main && git pull`でmainを最新化し、`git checkout -b knowledge-update-<日付>`で作業ブランチを作成する。

**成功確認**: 今回の調査対象ディレクトリが確定し、作業ブランチを作成した → Phase 2へ

---

## Phase 2: コード調査

対象ディレクトリをRead/Grepで調査し、以下の観点で`doc/spec/`との差分を洗い出す。

| 観点 | 確認方法 |
|------|---------|
| doc未記載の新機能・新画面 | 対象ディレクトリのファイル一覧と`doc/spec/00_overview.md`の画面一覧を突き合わせる |
| doc記載と実装の乖離 | 該当`doc/spec/NN_*.md`の記述と実装コードを読み比べる |
| CLAUDE.mdと実体の乖離 | ビルドコマンドのパス、ディレクトリ構成の記載、テストディレクトリの実在確認等 |

**成功確認**: 差分候補のリストができた（0件でもよい） → Phase 3へ

---

## Phase 3: doc/への反映

差分候補ごとに該当する`doc/spec/NN_*.md`を、既存のMarkdownテーブル形式を踏襲して更新する。新規画面がある場合は新規ファイルを既存のナンバリング規則（`NN_画面名.md`）で作成し、`00_overview.md`の画面一覧・画面遷移図も更新する。承認は不要で直接更新する。

**成功確認**: 該当するdoc更新が完了した（差分候補が0件ならスキップと明記） → Phase 4へ

---

## Phase 4: ルールへの反映

Phase 2で見つかった差分のうち、**開発運用ルールに関わるもの**（ビルドコマンドのパス誤り、コーディング規約の実体との乖離等）のみを対象に`CLAUDE.md`を更新する。仕様レベルの乖離はPhase 3のdoc更新で吸収し、CLAUDE.mdの編集範囲は運用ルールに厳格に絞る。

**成功確認**: 該当あれば更新完了、なければ「該当なし」と明記 → Phase 5へ

---

## Phase 5: コミット・マージ・ブランチ削除

Phase 3・Phase 4で更新がなかった場合（doc/CLAUDE.mdともに変更なし）、このPhaseはスキップしてPhase 6へ進む。

1. `git status`で変更ファイルを確認し、`git add doc/ CLAUDE.md`で更新分のみをステージする
2. `git commit -m "docs: ナレッジ蓄積フローによるdoc/CLAUDE.md更新"`でコミットする
3. `git checkout main && git pull`でmainを最新化する
4. `git merge --no-ff knowledge-update-<日付>`でmainに作業ブランチをマージする
5. `git push`でリモートのmainに反映する
6. `git branch -d knowledge-update-<日付>`でローカルの作業ブランチを削除する（リモートに同名ブランチをpushしていた場合は`git push origin --delete knowledge-update-<日付>`も実行する）

**成功確認**: mainへのマージ・push・作業ブランチ削除が完了した（更新がない場合はスキップと明記） → Phase 6へ

---

## Phase 6: 実行ログ記録

`references/history.md`に以下を追記する:
- 実行日時、フローID（KNOWLEDGE）
- 今回の調査対象ディレクトリ
- 更新したファイル一覧（doc/spec/, CLAUDE.md）
- コミットハッシュ・マージ結果（更新がなかった場合は「更新なし」と明記）
- 次回の調査対象（ローテーションの次の候補）

`references/knowledge-map.md`のローテーション状態を更新する。

**成功確認**: history.mdとknowledge-map.mdの更新が完了した → フロー完了

---

## エラー対応

| エラー | 対応 |
|-------|------|
| `doc/spec/`が見つからない | パスを確認し、history.mdに記録して終了 |
| 差分候補がdoc/CLAUDE.mdどちらに属するか判断できない | 仕様に関わるものはdoc/、開発運用に関わるものはCLAUDE.mdに寄せる（判断に迷う場合はdoc/を優先） |
| mainに未コミットの変更が残っている（Phase 1のブランチ作成前） | `git status`で確認し、無関係な変更ならstashしてから続行、関係する変更ならhistory.mdに記録して終了 |
| `git merge`でコンフリクトが発生する | 自動解決を試みず、作業ブランチを残したままhistory.mdに記録して終了（次回実行時に手動対応を促す） |
| `git push`が失敗する（リモートが進んでいる等） | `git pull --rebase`を試み、解決しなければhistory.mdに記録して終了 |
