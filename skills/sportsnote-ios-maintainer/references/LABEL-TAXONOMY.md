# ラベル体系定義

`Takatoshi-Miura/SportsNote_iOS`リポジトリで使用するissueラベルの定義。既存のGitHubデフォルトラベル（`bug`, `documentation`, `enhancement`等）に加え、以下3つを新規作成する。

## 新規作成ラベル

WORKFLOW-ISSUE.mdのPhase 1で、`gh label list`に存在しなければ`gh label create`で作成する。

| ラベル名 | 色 | 説明 |
|---------|-----|------|
| `refactor` | `#fbca04` | Code refactoring without behavior change |
| `test` | `#c2e0c6` | Missing or insufficient test coverage |
| `needs-manual-follow-up` | `#e11d21` | Auto-implementation skipped twice; needs manual attention |

作成コマンド例:
```bash
gh label create refactor --repo Takatoshi-Miura/SportsNote_iOS --color fbca04 --description "Code refactoring without behavior change"
gh label create test --repo Takatoshi-Miura/SportsNote_iOS --color c2e0c6 --description "Missing or insufficient test coverage"
gh label create needs-manual-follow-up --repo Takatoshi-Miura/SportsNote_iOS --color e11d21 --description "Auto-implementation skipped twice; needs manual attention"
```

## issue種別 → ラベル対応表

WORKFLOW-ISSUE.mdの各観点で使用する。

| issue種別 | ラベル |
|-----------|--------|
| 不具合 | `bug`（既存） |
| ユーザー要望 | `enhancement`（既存） |
| リファクタリング候補 | `refactor`（新規） |
| ドキュメント不足 | `documentation`（既存） |
| テスト不足 | `test`（新規） |

`needs-manual-follow-up`はissue作成時には付与しない。WORKFLOW-IMPLEMENT.mdが実行時（連続スキップ検知時）に事後付与する専用ラベル。
