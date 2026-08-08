# sportsnote-ios-full-cycle（sportsnote-ios-full-cycle）

## 1. 概要

- **何をするスキルか**: `sportsnote-ios-maintainer`が提供するKNOWLEDGE（ナレッジ蓄積）/ISSUE（issue作成）/IMPLEMENT（実装）の3ワークフローを、この順で1回ずつ直列実行するオーケストレーター。各フローは独立したサブエージェント（Agentツール）として起動され、doc/CLAUDE.md更新→issue起票→実装・PR作成までを一気通貫で回す。
- **発動条件**:
  - 自動発動キーワード: なし（`disable-model-invocation: true`のため明示呼び出しのみ）
  - スラッシュ呼び出し: `/sportsnote-ios-full-cycle` で可能
  - 自動発動: なし（明示呼び出しのみ）
- **依存の有無**: `sportsnote-ios-maintainer`スキル一式（`~/.claude/skills/sportsnote-ios-maintainer/`のWORKFLOW-*.mdファイル・`references/history.md`等）がローカルに存在すること。間接的に`gh` CLIログイン・SportsNote_iOSリポジトリのローカルクローンも必須（各WORKFLOWファイルが要求するため）
- **想定する利用シーン**: ナレッジ蓄積→issue起票→実装という一連の流れを、ローカルルーチンや手動操作で1回にまとめて回したい時

## 2. 事前準備（セットアップ）

`sportsnote-ios-maintainer`スキルの事前準備（`gh auth status`ログイン済み、SportsNote_iOSリポジトリのローカルクローン）が満たされていることが前提。本スキル自体に追加の準備は不要です。

## 3. 使い方

- **呼び出し方法**: `/sportsnote-ios-full-cycle` での明示呼び出し、または「フルサイクル実行して」「3フロー通しで回して」のような依頼で自動発動（自動発動は無効化されているため、実際にはスラッシュコマンドでの明示呼び出しのみ）
- **入力例**: 特になし。各WORKFLOWファイルが必要とする`input/requests.md`・`input/feedback.md`は`sportsnote-ios-maintainer`側のものをそのまま使う
- **出力例**: `sportsnote-ios-maintainer/references/history.md`への3エントリ追記（KNOWLEDGE/ISSUE/IMPLEMENT）、doc/CLAUDE.mdのmain反映、GitHub issue作成、実装PRの作成。詳細な出力形式は`sportsnote-ios-maintainer`側のREADMEを参照
- **手順**: Phase 0でTodo登録 → Phase 1でKNOWLEDGEフローをAgent経由で同期実行 → Phase 2でISSUEフローを同期実行 → Phase 3でIMPLEMENTフローを同期実行 → Phase 4で3フロー分の結果をサマリー表示
- **使う際のテクニック・コツ**:
  - 3フロー合計で実行時間が長くなる（コード調査・ビルド・PR作成を含むため）。対話セッションが長時間になることを踏まえて使うこと
  - 途中のフローが失敗・早期終了しても後続フローは必ず実行される設計（リトライはしない）

## 4. 保守・拡張ガイド

### ファイル構成

| ファイル | 役割 |
|---------|------|
| SKILL.md | 本体。Phase構成・Agent呼び出しテンプレート・失敗時挙動・サマリー仕様をすべて含む単一ファイル |
| README.md | 本ファイル |

### 修正時の手順と注意点

- 本スキルは`WORKFLOW-*.md`の内容を一切コピーしない設計。`sportsnote-ios-maintainer`側でPhase構成やファイル名が変わった場合、本SKILL.md内のファイルパス・Agent呼び出しテンプレートを追従修正する必要がある（他スキルのファイルパスを"参照"する設計ゆえの結合点）
- 実行順序（KNOWLEDGE→ISSUE→IMPLEMENT）を変更する場合は、SKILL.md冒頭の依存関係の説明（doc反映→issue作成→実装という順序依存の理由）を再確認してから変更する
- Phase 1〜3のAgent呼び出しは同期・単独発行が設計上の核心的制約。並列化（同一メッセージ内での複数Agent発行）は行わないこと

### 依存

- ツール: `Agent, TodoWrite`のみ。外部コマンドは直接使わない（すべてサブエージェント内で完結）
- MCP / 外部: なし（間接的に`sportsnote-ios-maintainer`側が`gh` CLI等に依存）

### 動作確認・テスト方法

`/sportsnote-ios-full-cycle`を呼び出し、以下を確認する。
- Phase 1〜3が同期的に順番に実行されること（並列発行されていないこと）
- `sportsnote-ios-maintainer/references/history.md`に3エントリ（KNOWLEDGE/ISSUE/IMPLEMENT）が追記されること
- Phase 4でサマリーが表示されること

## sportsnote-ios-maintainerとの関係性

- `sportsnote-ios-maintainer`は3フローを**個別に**（呼び出し文言に応じて1つだけ）実行するディスパッチャ型スキルであり、本スキルはその3フローを**まとめて1回ずつ順番に**実行するラッパー型スキルである
- 本スキルは`sportsnote-ios-maintainer`のSKILL.md（Phase 1のフロー判定ロジック）を経由せず、WORKFLOW-*.mdファイルを直接Agent経由で起動する
- 実装ロジック・doc/issue/PR生成ロジックは`sportsnote-ios-maintainer`側にのみ存在し、本スキルは一切保持しない。「他スキルのファイルを直接参照・importしない」という規約上の原則との関係については、本スキルはWORKFLOW-*.mdの内容を一切コピーせず、Agentツールへの起動パラメータとして絶対パスを渡すのみ（コンテンツは呼び出された側が自分でReadする）。これは「参照」ではなく「起動委譲」であり、規約が避けようとしている内容の二重管理には当たらないと整理している
