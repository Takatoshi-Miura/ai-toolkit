---
name: sportsnote-android-full-cycle
description: SportsNote Androidのナレッジ蓄積フロー・issue作成フロー・実装フロー（sportsnote-android-maintainerが提供する3ワークフロー）を、KNOWLEDGE→ISSUE→IMPLEMENTの順に1回ずつ直列実行するオーケストレーター。各フローは独立したサブエージェントとして起動し、doc/CLAUDE.md更新→issue起票→実装/PR作成までを一気通貫で回したい時に使う。「フルサイクル実行」「3フロー通しで」「ナレッジからissueから実装まで一気に」「sportsnote一気通貫」等の依頼で使用。
allowed-tools: Agent, TodoWrite
user-invocable: true
disable-model-invocation: true
---

# sportsnote-android-full-cycle

`sportsnote-android-maintainer`が提供する3つのワークフロー（ナレッジ蓄積・issue作成・実装）を、KNOWLEDGE→ISSUE→IMPLEMENTの順に1回ずつ直列実行する。

日本語で回答すること。

## オーケストレーション専念の原則

このスキルはdoc更新・issue作成・コード実装等の**実装ロジックを一切持たない**。3つのAgent呼び出しの発行と結果集約のみを行う薄い層である。`allowed-tools`が`Agent`と`TodoWrite`のみに絞られているのはこの原則をツール権限レベルでも担保するため。

- 新しい統合ロジックは書かない。既存の`WORKFLOW-*.md`ファイルをそのまま実行させる
- `sportsnote-android-maintainer`のSKILL.md（Phase 1のフロー判定ロジック）は経由しない。WORKFLOW-*.mdファイルパスを直接指定してAgentに渡す
- 実行記録は呼び出し先の`sportsnote-android-maintainer/references/history.md`に既に記録される仕組みがあるため、このスキル自身は独自のhistory.mdを持たず二重記録しない

## Phase 0: Todo登録

**TodoWriteツールで以下を登録：**

```json
[
  {"content": "Phase 1: KNOWLEDGEフロー実行", "activeForm": "KNOWLEDGEフローを実行中", "status": "pending"},
  {"content": "Phase 2: ISSUEフロー実行", "activeForm": "ISSUEフローを実行中", "status": "pending"},
  {"content": "Phase 3: IMPLEMENTフロー実行", "activeForm": "IMPLEMENTフローを実行中", "status": "pending"},
  {"content": "Phase 4: 結果サマリー表示", "activeForm": "結果サマリーを表示中", "status": "pending"}
]
```

---

## Phase 1: KNOWLEDGEフロー実行

下記「Agent呼び出しテンプレート」の`{ワークフローファイルの絶対パス}`を`/Users/it6210/.claude/skills/sportsnote-android-maintainer/WORKFLOW-KNOWLEDGE.md`に差し替え、Agentツールを**単独で**発行する。

**重要**: `run_in_background`は指定しない（同期実行がデフォルト）。Phase 1の完了を待ってからPhase 2に進む。同一メッセージ内で複数のAgent呼び出しを並列発行しない。

**成功確認**: Agentの応答を受け取った → Phase 2へ（Agentが失敗を報告した場合も含む。失敗時の扱いは「失敗時・一部スキップ時の扱い」を参照）

---

## Phase 2: ISSUEフロー実行

Phase 1の成否によらず実行する。下記テンプレートの`{ワークフローファイルの絶対パス}`を`/Users/it6210/.claude/skills/sportsnote-android-maintainer/WORKFLOW-ISSUE.md`に差し替え、Agentツールを単独で発行する（Phase 1と同様、同期実行・単独発行を厳守）。

**成功確認**: Agentの応答を受け取った → Phase 3へ

---

## Phase 3: IMPLEMENTフロー実行

Phase 2の成否によらず実行する。下記テンプレートの`{ワークフローファイルの絶対パス}`を`/Users/it6210/.claude/skills/sportsnote-android-maintainer/WORKFLOW-IMPLEMENT.md`に差し替え、Agentツールを単独で発行する（同期実行・単独発行を厳守）。

**成功確認**: Agentの応答を受け取った → Phase 4へ

---

## Agent呼び出しテンプレート

Phase 1〜3で共通して使う。サブエージェントは本会話の文脈を持たないため、自己完結したプロンプトにする。

```
subagent_type: "general-purpose"
description: "{フローID}フロー実行"
prompt: |
  あなたはSportsNote Androidの保守を無人実行するエージェントです。
  以下のワークフローファイルを読み、記載されたTodoWrite登録・Phase構成に従って最後まで実行してください。

  ## 実行するワークフローファイル
  {ワークフローファイルの絶対パス}

  ## 対象リポジトリ
  - プロジェクトパス: /Users/it6210/Documents/Git/SportsNote_Android
  - プロジェクト規約: /Users/it6210/Documents/Git/SportsNote_Android/CLAUDE.md
  - GitHubリポジトリ: Takatoshi-Miura/SportsNote_Android（ghコマンドでログイン済み前提）

  ## 実行上の注意
  - 承認待ちで停止せず、無人実行前提でワークフローの記載通りに完走してください（AskUserQuestionは使用しないでください）
  - ワークフローファイル内の「エラー対応」表に従ってエラーを処理してください
  - 実行記録はワークフローファイル自体の指示に従い、/Users/it6210/.claude/skills/sportsnote-android-maintainer/references/history.md に追記してください
  - 完了したら、実行結果の要約（成功/失敗、主要な成果物、history.mdに記録した内容の要点）を返答の最後に簡潔にまとめてください
```

**注意点**: `WORKFLOW-ISSUE.md`・`WORKFLOW-IMPLEMENT.md`は`gh`コマンドの引数等にリポジトリ名（`Takatoshi-Miura/SportsNote_Android`）やCLAUDE.mdパスを一部ハードコードしているが、`WORKFLOW-KNOWLEDGE.md`はプロジェクトパス自体を明記していない。「対象リポジトリ」節は`sportsnote-android-maintainer/SKILL.md`側にまとまって記載されており、サブエージェントはそのSKILL.mdを経由しないためこの情報を体系的には読まない。このテンプレートで毎回明示的に補うのは、WORKFLOWファイルごとの記載有無に依存せず自己完結性を担保するため（単にファイルパスを渡すだけでは自己完結しない可能性がある）。IMPLEMENTフロー（Phase 3）がissue 0件で即終了する分岐は`WORKFLOW-IMPLEMENT.md`自体に既に含まれているため、このスキル側で追加の分岐は書かない。

---

## Phase 4: 結果サマリー表示

Phase 1〜3で得た各Agentの応答から、以下の形式でチャット上にまとめて提示する。

```markdown
## sportsnote-android-full-cycle 実行結果

| フロー | 結果 |
|--------|------|
| KNOWLEDGE | {成功（更新あり）/成功（対象なし）/呼び出し失敗} |
| ISSUE | {成功（N件作成）/成功（対象なし）/呼び出し失敗} |
| IMPLEMENT | {成功（PR作成）/成功（issueなしで終了）/失敗（ビルド3回失敗等）/呼び出し失敗} |

### 各フローの要点
- KNOWLEDGE: {該当Agent応答の要約1〜2行}
- ISSUE: {該当Agent応答の要約1〜2行}
- IMPLEMENT: {該当Agent応答の要約1〜2行}

詳細な実行ログは references/history.md（sportsnote-android-maintainer側）を参照してください（本フロー実行分は「{今回の日付}」の3エントリ）。
```

- 「各フローの要点」は各Agentが返した最終応答の要約テキストをそのまま短く転記する程度に留め、新規に内容を分析・脚色しない
- IMPLEMENTでPRが作成された場合はPR URLをAgent応答から抜き出してサマリーに含める（`gh`コマンド等での再検証はしない。このスキルは`Agent`と`TodoWrite`以外のツールを持たないため検証もできない）

**成功確認**: サマリーを提示した → 完了

---

## 失敗時・一部スキップ時の扱い

**方針: 途中のフローが失敗しても後続フローの実行は止めない。3つとも必ず1回ずつ呼び出す。リトライはしない。**

- KNOWLEDGE→ISSUE→IMPLEMENTは「順序」の依存であり「前段が成功しないと後段が無意味」という強い依存ではない。ISSUE・IMPLEMENTは各々が自己完結しており独立して着手できる
- 各WORKFLOWファイル自体が既に自分のエラー対応表を持っており、下流フローが不整合な状態を引き継ぐことはない
- Agentツールの応答自体がエラーで返ってくる（サブエージェントがクラッシュする等）場合のみ「呼び出し失敗」としてサマリーに記録し、次のフローに進む
- ワークフロー内部の判断でスキップ・早期終了した場合（IMPLEMENTでissue 0件、KNOWLEDGEで差分0件等）は「失敗」ではなく「正常完了（対象なし）」としてサマリーに記録する（ワークフロー自身が返す要約文から判定する）
- 3フロー全てが呼び出し失敗した場合でも、Phase 4のサマリー表示までは必ず到達する

## ループ設計に関する補足

3回の直列Agent呼び出しは固定シーケンス（Turn-basedの単純な逐次実行）であり、反復ループではない。停止条件は「3フロー完了、またはいずれかのAgent呼び出しが異常終了してもスキップして先に進む」。リトライ上限は意図的に設けない。

## エラー対応

| エラー | 対応 |
|-------|------|
| Agentツールの呼び出し自体が失敗する（サブエージェントのクラッシュ等） | そのフローを「呼び出し失敗」としてサマリーに記録し、次のフローに進む（リトライしない） |
| Agent応答から結果（成功/失敗/対象なし）を判定できない | 応答をそのまま「詳細不明」としてサマリーに記録し、次のフローに進む |
| `sportsnote-android-maintainer`のWORKFLOW-*.mdファイルが見つからない | パスを確認し、該当フローを「呼び出し失敗」としてサマリーに記録し、次のフローに進む |
