# FE開発ワークフロー

FE（React/TypeScript）の機能追加・修正・改善を、要件ヒアリングからセルフチェックまで一連のPhaseで進行する。

プロジェクト情報:
- **プロジェクトパス**: `/Users/takatoshi.miura/Documents/Git/sazabi/src/main/webapp/frontend`
- **プロジェクト規約**: `/Users/takatoshi.miura/Documents/Git/sazabi/src/main/webapp/frontend/CLAUDE.md`
- **コーディング規約**: `/Users/takatoshi.miura/Documents/Git/sazabi/src/main/webapp/frontend/docs/guides/coding-standards.md`

**最初のアクション**: Bashツールで作業ディレクトリを移動する:

```bash
cd /Users/takatoshi.miura/Documents/Git/sazabi/src/main/webapp/frontend
```

以降、すべての操作（Git操作含む）はこのディレクトリから実行する。

## TodoWrite登録

```json
[
  {"content": "Phase 1: 要件ヒアリング", "activeForm": "要件をヒアリング中", "status": "pending"},
  {"content": "Phase 2: Git準備（ブランチ・空コミット・ドラフトPR）", "activeForm": "Git準備中", "status": "pending"},
  {"content": "Phase 3: 実装計画", "activeForm": "実装計画を策定中", "status": "pending"},
  {"content": "Phase 4: 実装", "activeForm": "コードを実装中", "status": "pending"},
  {"content": "Phase 5: セルフチェック", "activeForm": "セルフチェックを実行中", "status": "pending"}
]
```

---

## Phase 1: 要件ヒアリング

### 1-1. ユーザーへの質問

AskUserQuestionツールで以下を収集:

| 項目 | 必須 | 例 |
|------|------|-----|
| 対応したいこと | ✅ | 新機能追加、バグ修正、UI改善など |
| チケット情報 | ❌ | チケット番号、URL、または概要 |
| ブランチ名 | ✅ | feature/12345/add-bulk-upload-validation |
| PRタイトル | ✅ | bulkUpload画面にバリデーション追加 |
| ベースブランチ | ❌ | デフォルト: master |
| 優先度・制約 | ❌ | パフォーマンス要件、既存機能への影響など |

**注意**: ブランチ名とPRタイトルはPhase 2で使用するため、必ずこのPhaseで確定させること。ユーザーが未指定の場合はチケット情報や対応内容から提案して確認を取る。

### 1-2. 情報の整理

収集した情報を整理し、ユーザーに確認:
- 対応内容の要約
- ブランチ名とPRタイトルの確認

**成功確認**: 必要な情報がすべて揃い、ユーザーが要件・ブランチ名・PRタイトルを確認 → Phase 2へ

---

## Phase 2: Git準備（ブランチ・空コミット・ドラフトPR）

### 2-1. ブランチ作成

```bash
git fetch origin
git checkout -b {ブランチ名} origin/{ベースブランチ}
```

### 2-2. 空コミットの作成

```bash
git commit --allow-empty -m "{PRタイトル}"
git push -u origin {ブランチ名}
```

### 2-3. ドラフトPR作成

ghコマンドでドラフトPRを作成:

```bash
gh pr create --draft --title "{PRタイトル}" --body "WIP" --base {ベースブランチ}
```

### 2-4. ai-code-tracker の確認

以下のコマンドを実行して `aict` が利用可能か確認する:

```bash
aict --version
```

**利用可能な場合**（バージョンが表示された場合）:
- リポジトリで初期化済みか確認し、未初期化なら以下を実行:

```bash
aict init
aict setup-hooks
```

**利用不可の場合**（コマンドが見つからない等）:
- ユーザーに「aict が見つかりません。セットアップを実行します。」と報告
- 以下の手順でセットアップ:

1. Go の確認・インストール（未インストールなら `brew install go`）
2. PATH 設定の確認（`$(go env GOPATH)/bin` が含まれているか）
3. aict のインストール: `go install github.com/y-hirakaw/ai-code-tracker/cmd/aict@latest`
4. リポジトリでの初期化: `aict init && aict setup-hooks`

**注意**: `aict setup-hooks` により `.claude/settings.json` に hooks 設定が追加される。必要に応じてユーザーに設定の確認を促す。

**成功確認**: ドラフトPRのURLが取得でき、aictが利用可能な状態でユーザーに報告 → Phase 3へ

---

## Phase 3: 実装計画

### 3-1. CLAUDE.md の読み取り

`/Users/takatoshi.miura/Documents/Git/sazabi/src/main/webapp/frontend/CLAUDE.md` を読み取り、以下を把握:
- プロジェクト構成・技術スタック
- ビルド・テスト・Lintコマンド
- コーディングルール
- ディレクトリ構造

### 3-2. Plan サブエージェントの呼び出し

Taskツールで `Plan` サブエージェントを起動:

```
subagent_type: "Plan"
prompt: |
  以下の情報に基づいて実装計画を立ててください。

  ## 実装内容
  {Phase 1でヒアリングした要件}

  ## 参照情報
  - CLAUDE.md: /Users/takatoshi.miura/Documents/Git/sazabi/src/main/webapp/frontend/CLAUDE.md
  - コーディング規約: /Users/takatoshi.miura/Documents/Git/sazabi/src/main/webapp/frontend/docs/guides/coding-standards.md

  ## 作成してほしいもの
  1. 不明点があればユーザーに質問（解消するまで繰り返し）
  2. 既存の類似実装パターン調査（/Users/takatoshi.miura/Documents/Git/sazabi/src/main/webapp/frontend/src/ 内）
  3. 修正対象ファイルの特定
  4. 実装方針の策定
```

### 3-3. 実装計画の出力フォーマット

Planサブエージェントは以下の形式で出力:

```markdown
## 実装計画

### 1. 概要
- **目的**: （1-2文）
- **スコープ**: （対象範囲）
- **除外事項**: （今回対象外）

### 2. 前提条件
- （React 19, TypeScript 5.8, TanStack Router/Query, MUI 7 等）

### 3. 修正対象ファイル
| ファイルパス | 変更種別 | 変更概要 |
|-------------|---------|---------|

### 4. 実装ステップ
#### Step N: （ステップ名）
- **対象ファイル**: path/to/file.tsx
- **変更内容**: （箇条書き）
- **依存関係**: （他ステップとの依存）

### 5. 類似実装の参照
### 6. リスク・注意点
```

### 3-4. ユーザー承認

1. 実装計画をユーザーに提示
2. スコープ・修正対象・実装ステップ・リスクの観点で承認を求める
3. 承認されない場合 → 3-2に戻り計画を修正
4. 承認された場合 → Phase 4へ

**成功確認**: ユーザーが実装計画を承認 → Phase 4へ

---

## Phase 4: 実装

### 4-1. コード実装

承認された実装計画に従い、直接コードを実装する:

1. CLAUDE.mdのコーディングルールに従う
2. Edit/Writeツールでコードを変更・作成
3. 既存コードのスタイルを尊重する
4. コーディング規約（coding-standards.md）を遵守する

### 4-2. Lint の実行

```bash
npm run lint
```

- Lintエラーがあれば修正（`npm run lint:fix` を活用）
- エラーがなくなるまで繰り返す

### 4-3. ビルド実行

```bash
npm run build
```

- ビルドエラーがあれば修正し、再ビルド
- 成功するまで繰り返す

### 4-4. テスト（条件付き）

**テスト不要**: 既存共通コンポーネントの呼び出しのみ / 既存テストで十分カバー / UIの軽微な変更のみ

**テスト必要**: 新規ビジネスロジック / 複雑な条件分岐 / カスタムHooksの追加・変更 / ユーティリティ関数の追加・変更

テストが必要な場合:
- テストフレームワーク: Vitest + Testing Library
- テストファイルは対象ファイルと同じディレクトリに配置
- テスト記述は日本語で
- テスト実行: `npm test`

**完了条件（すべて満たすこと）**:
- [ ] Lint が正常に完了（`npm run lint`）
- [ ] ビルドが成功（`npm run build`）
- [ ] テスト実行が必要な場合、テストが成功（`npm test`）

**成功確認**: Lint成功・ビルド成功・テスト成功（必要な場合） → Phase 5へ

---

## Phase 5: セルフチェック

### 5-1. 変更差分の取得

```bash
git diff origin/{ベースブランチ}...HEAD
```

### 5-2. コーディング規約準拠チェック

`/Users/takatoshi.miura/Documents/Git/sazabi/src/main/webapp/frontend/docs/guides/coding-standards.md` を読み取り、変更差分に対して以下の観点でチェック:

| チェック項目 | 確認内容 |
|-------------|---------|
| ファイル名規約 | PascalCase.tsx (コンポーネント)、camelCase.ts (ユーティリティ)、useXxx.ts (Hooks) |
| エクスポート規約 | Named Exportのみ、Default Export不使用 |
| バレルファイル | index.tsによるバレルエクスポートがないこと |
| 型定義 | any型不使用、type推奨（interfaceでなく）、API型にHTTPメソッド名プレフィックス |
| React パターン | useMemo/useCallback不使用（React Compiler環境） |
| コメント規約 | 行末コメント不使用、日本語で簡潔に |
| インポート | 直接インポートのみ、バレルインポート不使用 |

違反箇所があれば修正を実施する。

### 5-3. セルフレビュー（自由観点）

変更差分に対して、コーディング規約以外の以下の観点で自由にレビュー:

| 観点 | 確認内容 |
|------|---------|
| コード品質 | 可読性、保守性、重複コード |
| バグリスク | 潜在的なバグ、エッジケース、null/undefinedハンドリング |
| パフォーマンス | 不要な再レンダリング、重い計算 |
| セキュリティ | XSS、インジェクション、機密情報の露出 |
| アクセシビリティ | セマンティックHTML、aria属性 |
| 型安全性 | 型アサーション(as)の乱用、unknown活用 |

### 5-4. セルフチェック結果の報告

以下の形式でユーザーに報告:

```markdown
## セルフチェック結果

### コーディング規約準拠チェック
| チェック項目 | 結果 | 備考 |
|-------------|------|------|
| ファイル名規約 | ✅ / ❌ | |
| エクスポート規約 | ✅ / ❌ | |
| ... | | |

### セルフレビュー指摘事項
- **[重要度: 高/中/低]** 指摘内容と修正提案
- ...

### 修正済み項目
- （セルフチェック中に自動修正した内容）

### 変更ファイル一覧
| ファイルパス | 変更種別 | 変更概要 |
|-------------|---------|---------|
```

### 5-5. 最終確認

指摘事項のうち修正が必要なものがあれば修正を実施し、再度Lint・ビルド・テストを実行して成功を確認する。

**成功確認**: セルフチェック完了・全指摘対応済み → 完了

---

## エラーハンドリング

| エラー | 対応 |
|-------|------|
| 情報不足 | AskUserQuestionで追加情報を収集 |
| サブエージェント失敗 | エラーメッセージを分析し再試行（最大3回） |
| npm install 失敗 | node_modules削除後に再インストール |
| Lint失敗 | `npm run lint:fix` で自動修正を試み、残りは手動修正 |
| ビルド失敗 | TypeScriptエラーを分析し修正 |
| テスト失敗 | 失敗テストを特定し修正 |
| PR作成失敗 | ghコマンドの認証状態を確認、ブランチのpush状態を確認 |
| ブランチ名重複 | ユーザーに代替ブランチ名を確認 |

## 注意事項

- 作業ディレクトリは `/Users/takatoshi.miura/Documents/Git/sazabi/src/main/webapp/frontend` を基本とする
- ビルド・テスト・Lintコマンドは必ずCLAUDE.mdに記載のものを使用する
- 過剰な改善提案は避け、要求されたスコープに集中する
- 既存コードのスタイルを尊重する（CLAUDE.mdおよびcoding-standards.mdの規約に従う）
- React Compiler環境のため、useMemo/useCallbackは使用しない
- バレルファイル（index.ts）は作成しない
- Default Exportは使用しない
- 作成・変更前に必ずユーザーの承認を得る
