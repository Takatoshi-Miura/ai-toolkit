# GitHub Issue TODOテンプレート

開発中に思いついたTODOをIssueとして登録する際のテンプレートです。

## テンプレート

```markdown
## 概要
{description}

## 背景
{background}

## 期待する結果
{expected_outcome}

## 関連箇所
{related_files_or_features}

## 追加情報
- **優先度**: {priority}
- **種別**: {type}
```

## 変数の説明

| 変数名 | 必須 | 説明 | 例 |
|--------|------|------|-----|
| `{description}` | 必須 | 何をしたいか、何が必要か | ユーザー一覧画面にページネーションを実装する |
| `{background}` | 任意 | このTODOが必要な理由・経緯 | 100件以上表示時にパフォーマンスが低下するため |
| `{expected_outcome}` | 任意 | 完了時に期待する状態 | 1ページ20件で表示、ページ切替可能 |
| `{related_files_or_features}` | 任意 | 関連するコード・機能・画面 | `src/pages/users/UserList.tsx` |
| `{priority}` | 任意 | 高/中/低（デフォルト: 中） | 高 |
| `{type}` | 任意 | feature/bug/refactor/docs/other（デフォルト: feature） | feature |

## セクション省略ルール

- `{background}` が未指定の場合: 「## 背景」セクションを省略
- `{expected_outcome}` が未指定の場合: 「## 期待する結果」セクションを省略
- `{related_files_or_features}` が未指定の場合: 「## 関連箇所」セクションを省略
- 「## 追加情報」セクションは常に出力（デフォルト値を使用）
