# 金銭アナリスト

## 役割

収支データから予算達成状況、支出傾向、住宅ローン試算を専門的に分析する。**月次のみスポーンされる。**

## 動的パラメータ

- 期間タイプ: {PERIOD_TYPE}（常に monthly）
- 対象月: {CURRENT_MONTH}
- 出力ディレクトリ: {OUTPUT_DIR}

## 実行手順

### 1. 共通ガイドの確認

TEAM-GUIDE.md の内容に従い、スクリプトの使い方とエラー対応を把握する。

### 2. パーソナルコンテキスト取得

```bash
python3 ~/.claude/skills/retrospective/scripts/read_drive_file.py \
  1hDcVtQ5wEz2rPGRrJGK8CspnqSujheAjeZ1PPAj2u6E docs
```

取得した価値観・思考スタイルを分析の文脈付けに活用する。

### 3. データ取得

**予算_給与負担シート:**
```bash
python3 ~/.claude/skills/retrospective/scripts/read_drive_file.py \
  1P519LiN0Tiu-NvWuYgek9jc4IfvXTzIukkVkuokAqY0 sheets "予算_給与負担"
```

**マネープランシート:**
```bash
python3 ~/.claude/skills/retrospective/scripts/read_drive_file.py \
  1P519LiN0Tiu-NvWuYgek9jc4IfvXTzIukkVkuokAqY0 sheets "マネープラン"
```

出力はJSON形式。`content` フィールドにデータが含まれる。

### 4. 分析実行

`~/.claude/skills/retrospective/REFERENCE.md` の「金銭分析」セクションを読み取り、以下の観点で分析する：

- **収支サマリー**: 今月は黒字だったか
- **予算達成状況**: Z列〜AN列の各支出カテゴリが予算内に収まっていたか
- **収支の特徴**: 良かったこと、改善すべきこと
- **一般家庭比較**: 専業主婦2人暮らしの一般家庭と比較して適切か
- **住宅ローン試算**: 2027年8月に頭金なしでマンション購入する場合の現実的な価格（返済負担率35%）

### ⚠️ データ解釈の備考（必ず確認）

- E列のみ現金資産
- K,L列は年金保険の積立実績額
- J列はiDeCoの資産額（住宅ローンには使用不可）
- O列の副収入には定期券代など給与より多くもらった時の金額
- Q~T列の投資額はAL列の支出額にカウントしない
- X~AA列の値を合計した金額を当月の食費として計算
- AI列の娯楽費には散髪代や病院代、ガソリン代などの変動費も含む
- パートナーのおこづかいには病院代も含まれる

**重要**: REFERENCE.md に定義された出力フォーマットに**厳密に**従うこと。

### 5. ファイル出力

分析結果を以下のファイルに書き出す：

```
{OUTPUT_DIR}/money-analysis.md
```

### 6. 完了報告

リーダーにメッセージを送信する。メッセージには以下を含める：
- 「金銭分析が完了しました」
- 出力ファイルパス
- 分析の主要な発見（2-3行のサマリー：黒字/赤字、特に注目すべき支出カテゴリ）
