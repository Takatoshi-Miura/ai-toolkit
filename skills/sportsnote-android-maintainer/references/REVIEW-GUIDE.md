# クロスレビューサブエージェント起動ガイド

WORKFLOW-IMPLEMENT.mdのPhase 5から参照する。

## 起動方法

Agentツールで`subagent_type: general-purpose`を、実装を行ったメインの流れとは別コンテキストで起動する（実装者の自己申告を信用せず、独立した視点でレビューする）。

## プロンプト設計

エージェントは本会話の文脈を持たないため、以下を自己完結させて渡す。

```
subagent_type: "general-purpose"
prompt: |
  SportsNote Androidの実装をクロスレビューしてください。あなたは実装者ではなく、独立したレビュアーです。

  ## 対象issue
  #{issue番号}: {issueタイトル}
  {issue本文}

  ## 変更差分
  {git diff main --stat の出力}

  {git diff main の実差分}

  ## 参照情報
  - コーディング規約: /Users/it6210/Documents/Git/SportsNote_Android/CLAUDE.md
  - 過去の指摘パターン: /Users/it6210/.claude/skills/sportsnote-android-maintainer/references/review-insights.md
    （このファイルを読み、過去に繰り返し指摘されている観点があれば重点的に確認してください）

  ## 出力形式
  指摘の有無を報告してください。指摘がある場合は、以下の形式で列挙してください:
  - ファイルパス:行番号 - 指摘内容 - 深刻度（must-fix / should-fix / nit）

  must-fix: issue本文の完了条件を満たさない、CLAUDE.mdの規約に違反する、明確なバグを含む
  should-fix: 望ましいが必須ではない改善
  nit: 些細な指摘（命名・コメント等）
```

## 判定基準

- **must-fix指摘がある** → 再実装ラウンドへ（修正後、再度クロスレビュー）
- **should-fix/nitのみ** → 合格扱い。指摘内容はPR本文に残す（3ラウンド上限を無駄に消費しない）
- **3ラウンド経過してもmust-fix指摘が残る** → 実装は放棄せず、残指摘をPR本文に明記してPR作成する

## review-insights.md への蓄積

各レビューラウンド終了後、以下の形式で`references/review-insights.md`に追記する。

```markdown
## {日付} issue #{issue番号}
- カテゴリ: {例: Realmアクセス, エラーハンドリング, テスト網羅性}
- 指摘: {指摘内容の要約}
```

同ファイルは次回以降のレビュー起動プロンプトにパスとして渡し、レビュアーが過去の指摘観点を踏まえて重点的に確認できるようにする（内容を要約せずファイルパスをそのまま渡す）。

**肥大化対策**: `references/review-insights.md`が100行を超えたら、直近30件程度を残し、それより古いものは「{期間}: {カテゴリ}の指摘が{件数}件」のような1行要約に圧縮する。
