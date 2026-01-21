---
name: retrospective
description: 振り返りスペシャリストとして週次/月次のレトロスペクティブを実行。「振り返り」「レトロスペクティブ」「今週どうだった」「月次レビュー」「1週間まとめ」「反省会」などの表現を含む依頼で自動的に発動します。LifeGraph、日次記録、金銭データをスクリプトで取得・分析してレポートを作成。
allowed-tools: Bash, AskUserQuestion, Write, Read
user-invocable: true
disable-model-invocation: true
---

# 振り返りスキル

週次または月次の振り返りを効率的にサポートし、スクリプトでデータを取得してレポートを作成します。

## 発動条件

このスキルは以下の状況で自動的に適用されます：

- 「振り返り」「レトロスペクティブ」「retrospective」を含む依頼
- 「今週どうだった」「先週の振り返り」などの表現
- 「月次レビュー」「1ヶ月まとめ」などの表現
- 「反省会」「週報」「月報」などの表現

## 前提条件

### ユーザープロフィール
- ITエンジニア（iOS/Android モバイルアプリ開発）、スペシャリスト思考
- 4カテゴリ（仕事、人間関係、金銭、健康・メンタル）で人生を管理
- 専業主婦との2人暮らし世帯

### データソース
| データ | ファイルID | fileType | 用途 |
|--------|-----------|----------|------|
| LifeGraph | `1WF58VNM0lGfN-YKqR2ySXU_EKQQCpyrV4da8WiVtoBo` | sheets | 時間・パフォーマンス分析 |
| ノート | `1iVeZ1EB5dahEZukuQQB4gSa5jIw3By-Gz8JaAysiAoA` | docs | 日次記録・目標 |
| 金銭管理 | `1P519LiN0Tiu-NvWuYgek9jc4IfvXTzIukkVkuokAqY0` | sheets | 収支分析（月次のみ） |

## 実行手順

### Phase 1: 期間選択

AskUserQuestionツールで期間を質問：

| 選択肢 | 内容 |
|--------|------|
| 週次 | LifeGraph + 日次記録 |
| 月次 | LifeGraph + 金銭 + 日次記録 |

### Phase 2: 出力ファイル作成

`~/Downloads/yyyyMMdd-{weekly|monthly}-retrospective.md` を作成（タイトルと目次のみ）

### Phase 3: データ取得

**スクリプトでGoogle Driveからデータを取得する:**

```bash
# スクリプトパス
SCRIPT_PATH="skills/read-google-drive-skill/scripts/read_drive_file.py"

# LifeGraph（スプレッドシート）
python $SCRIPT_PATH 1WF58VNM0lGfN-YKqR2ySXU_EKQQCpyrV4da8WiVtoBo sheets "Googleカレンダー集計"

# ノート（ドキュメント）- 今年の目標タブ
python $SCRIPT_PATH 1iVeZ1EB5dahEZukuQQB4gSa5jIw3By-Gz8JaAysiAoA docs "今年の目標"

# ノート（ドキュメント）- 今月タブ（yyyyMM形式、例: 202601）
python $SCRIPT_PATH 1iVeZ1EB5dahEZukuQQB4gSa5jIw3By-Gz8JaAysiAoA docs "202601"

# 金銭管理（月次のみ）
python $SCRIPT_PATH 1P519LiN0Tiu-NvWuYgek9jc4IfvXTzIukkVkuokAqY0 sheets "予算_給与負担"
python $SCRIPT_PATH 1P519LiN0Tiu-NvWuYgek9jc4IfvXTzIukkVkuokAqY0 sheets "マネープラン"
```

**出力形式:** JSON。`content` フィールドにデータが含まれる。

### Phase 4: 分析とレポート作成

取得したデータを分析し、レポートに追記する。
詳細な分析観点とフォーマットは [REFERENCE.md](REFERENCE.md) を参照。

### Phase 5: 目標提案・総評

全分析結果を踏まえて、各カテゴリの目標提案と総評を追記。

### Phase 6: 完了報告

レポートファイルのパスを報告。

## 注意事項

- スクリプトがエラーを返した場合は `~/Documents/Git/MCP-GoogleDrive/README.md` の認証手順を案内
- 今月のタブ名は `yyyyMM` 形式（例: 202601）
