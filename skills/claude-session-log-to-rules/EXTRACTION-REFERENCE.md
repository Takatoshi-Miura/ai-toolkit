# 候補抽出スクリプト リファレンス

候補抽出は2段構成。`scripts/jsonl_to_markdown.py`（Stage 1）でJSONLをMarkdown化し、`scripts/extract_feedback_candidates.py`（Stage 2）でそのMarkdownから候補を抽出する。JSONLは生データが大きくトークン消費が大きいため、Stage 1でMarkdown化してから軽量な候補リストに絞り込む。

## Stage 1: jsonl_to_markdown.py

```bash
python3 scripts/jsonl_to_markdown.py convert \
  --output <path.md> \
  [--since-days <N>] [--since YYYY-MM-DD] \
  [--include-worktrees] [--projects-root ~/.claude/projects]
```

`~/.claude/projects/`配下を全プロジェクト横断で走査し、Question/Answer形式のMarkdownに変換する。`--since-days`/`--since`を省略すると全期間が対象になる。

出力JSON: `success`, `output_path`, `unchanged`, `scanned_dirs`, `excluded_dirs`, `sessions[]`, `skipped_lines`, `warnings`。

出力Markdownの構造:
```
# Session Log: <タイトル>
- Session ID: `<id>`
- Project: `<cwd>`
...
## <timestamp> | Q1
### Question
> ユーザー発言（複数行は複数の引用行）
### Answer
（assistantのtextとツール呼び出し要約）
---
```

スキル定義文の混入（`Base directory for this skill:`で始まる発言）は`(スキル定義文の混入のため省略)`に置換され、Stage 2では自動的に候補から除外される。

## Stage 2: extract_feedback_candidates.py

```bash
python3 scripts/extract_feedback_candidates.py scan --input <Stage1のoutput_path>
```

Stage 1が生成したMarkdownを読み、`### Question`配下の引用行（ユーザー発言）のみを対象に正規表現マッチする。`### Answer`配下（アシスタントの応答・ツール呼び出し）は対象外。

### 出力JSON構造

```json
{
  "success": true,
  "source_markdown": "/Users/.../all_xxx.md",
  "total_questions_scanned": 85,
  "candidates": [
    {
      "text": "候補となったユーザー発言（300字で切り詰め済み）",
      "matched_categories": ["mandate", "approval"],
      "project_dir_name": "SportsNote_iOS",
      "timestamp": "2026-06-10T12:34:56.789Z",
      "sessionId": "xxxx-xxxx",
      "context_excerpt": "前後のuser発言（200字×最大2件で切り詰め済み）"
    }
  ],
  "warnings": []
}
```

- `text`/`context_excerpt`は文字数制限（それぞれ300字/200字）で切り詰められる。これによりJSON出力全体のサイズと、Phase 2でClaudeが読む際のトークン消費を抑える
- `project_dir_name`はMarkdown内の`- Project:`行（cwdのフルパス）からファイル名相当の末尾部分のみを抜いたもの。ヒントであり確定ではない
- `candidates`が多すぎる場合（200件超）は`warnings`に出力される。その場合はStage 1の`--since-days`で対象期間を絞って再実行する

## 正規表現カテゴリ

| カテゴリ | 意味 | マッチ例 |
|---|---|---|
| `prohibition` | 禁止・やめてほしい指示 | 「しないで」「やめて」「禁止」 |
| `mandate` | 強制・指示・要望 | 「必ず」「〜してほしい」「〜したい」「〜べき」「〜すること」 |
| `approval` | 承認・確定 | 「これでいい」「OK」「完璧」「そうそう」 |
| `standardize` | 統一・標準化の要望 | 「統一して」「標準化」「揺れがある」 |
| `correction` | 訂正・認識合わせ | 「違う」「そうじゃなくて」「〜であってる？」 |

1メッセージが複数カテゴリにマッチすることがある（候補をテーマ別に集約する際の参考情報として使う）。

## 既知のノイズと対処

- **XMLタグ系ノイズ**（`<ide_opened_file>`等）: Stage 1の`strip_noise()`で除去済み
- **スキル定義文の混入**: `Base directory for this skill:`形式はStage 1で自動除外済み。`# XXX Skill`のようなMarkdown見出しで始まるスキル本文は正規表現での網羅的な除去が難しいため自動除外していない。**Phase 2でClaudeが候補を読む際、文章が自然なユーザー発言ではなく明らかにスキルのドキュメント文章であれば、ルール化候補から除外すること**
- **開発と無関係な雑談**（住宅ローン相談、旅行先提案等）: スクリプトは内容の意味を判断しないため候補に含まれる。Phase 2でルール化対象外として除外する

## 件数が想定より少ない/多い場合

- 全期間でスキャンしても候補が極端に少ない場合、ログの蓄積量自体が少ないことが原因である可能性が高い（運用初期は数十セッション程度）。正規表現を疑う前にまず`total_questions_scanned`を確認する
- 候補が多すぎる場合はStage 1の`--since-days`で直近の期間に絞ってから再実行する
