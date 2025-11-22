# 指定したリポジトリの指定した期間のコード差分を取得するタスク

# 手順
1. 以下の情報が提供されていないければ、ユーザーに質問して提供してもらう
    - コード差分を取得したいリポジトリ
    - 期間（開始日・終了日、例: `2025-10-01` ～ `2025-11-18`）

2. 以下のコマンドを使用し、コミット情報や変更ファイル情報を取得する
```bash
# コミット一覧（マージコミットを除外）
git log --author="takatoshi.miura" --since="<開始日>" --until="<終了日>" --no-merges --pretty=format:"%H|%h|%s|%ai" --all

# コミット数（マージコミットを除外）
git log --author="takatoshi.miura" --since="<開始日>" --until="<終了日>" --no-merges --all --oneline | wc -l

# 全ファイル（マージコミットを除外）
git log --author="takatoshi.miura" --since="<開始日>" --until="<終了日>" --no-merges --name-only --pretty=format: --all | grep -v '^$' | sort -u

# 本番用Kotlinのみ（マージコミットを除外）
git log --author="takatoshi.miura" --since="<開始日>" --until="<終了日>" --no-merges --name-only --pretty=format: --all | grep -v '^$' | sort -u | grep -E '\.kt$' | grep 'src/main/java'

# ファイル数（マージコミットを除外）
git log --author="takatoshi.miura" --since="<開始日>" --until="<終了日>" --no-merges --name-only --pretty=format: --all | grep -v '^$' | sort -u | wc -l
```

3. 以下の情報をユーザーに返却する
    - リポジトリ名
    - 期間
    - ユーザー名
    - コミット数
    - コミット一覧
    - 変更ファイル数
    - 変更ファイル名のリスト