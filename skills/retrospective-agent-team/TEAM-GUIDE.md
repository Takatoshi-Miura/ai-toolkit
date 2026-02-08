# チームメンバー共通ガイド

このドキュメントはエージェントチームの全メンバーが参照する共通ガイドです。

## データ取得スクリプト

### スクリプトパス

```
~/.claude/skills/retrospective/scripts/read_drive_file.py
```

### 使用方法

```bash
python3 ~/.claude/skills/retrospective/scripts/read_drive_file.py <ファイルID> <fileType> [シート名/タブ名]
```

**パラメータ:**
- `ファイルID`: Google DriveのファイルID
- `fileType`: `sheets`（スプレッドシート）または `docs`（ドキュメント）
- `シート名/タブ名`: 読み取り対象のシート名またはタブ名（省略可）

**出力:** JSON形式。`content` フィールドにデータが含まれる。

### パーソナルコンテキスト取得（全メンバー共通）

```bash
python3 ~/.claude/skills/retrospective/scripts/read_drive_file.py \
  1hDcVtQ5wEz2rPGRrJGK8CspnqSujheAjeZ1PPAj2u6E docs
```

分析の文脈付けに使用する。ユーザーの価値観・思考スタイルを理解し、分析や提案に反映すること。

## 分析リファレンス

詳細な分析観点と出力フォーマットは以下を参照：

```
~/.claude/skills/retrospective/REFERENCE.md
```

各メンバーは担当セクションを読み取り、定義されたフォーマットに**厳密に**従うこと。

## エラー対応

### 認証エラー

`Token has been expired`、`invalid_grant` などのエラーが発生した場合：

1. **リトライ1回**: 同じコマンドを再実行
2. **失敗時**: リーダーにメッセージを送信し、エラー内容を報告
   - リーダーが `~/.claude/skills/retrospective/SETUP.md` に基づいてユーザーに案内する

### スクリプト実行エラー

その他のエラーが発生した場合：

1. エラーメッセージを確認
2. リトライ1回
3. 失敗時はリーダーにエラー内容をメッセージで報告

## 完了時の報告規約

分析が完了したら、リーダーにメッセージを送信する。

**メッセージに含める内容：**
1. 完了ステータス: 「{担当名}分析が完了しました」
2. 出力ファイルパス
3. 主要な発見のサマリー（2-3行）

**メッセージ例:**
```
LifeGraph分析が完了しました。
出力: ~/Downloads/20260208-weekly-retrospective/lifegraph-analysis.md
主要な発見: 今週はパフォーマンスが平均4.2点で先週比+0.3。睡眠時間が7h以上の日にパフォーマンスが高い傾向。自己投資時間は平日平均1.5hで安定。
```

## 注意事項

- 自分の担当ファイルにのみ書き込むこと（他メンバーのファイルは読み取り専用）
- 分析はデータに基づいて行い、推測は最小限にする
- パーソナルコンテキストを踏まえて、ユーザーにとって意味のある洞察を提供する
