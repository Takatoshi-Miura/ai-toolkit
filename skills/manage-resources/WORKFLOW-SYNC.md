# 同期ワークフロー

## TodoWrite チェックリスト

**各Phaseの開始時に `in_progress`、完了時に `completed` に更新すること：**

```
同期進捗：
- [ ] Phase 1: 同期スクリプト実行
- [ ] Phase 2: 結果の表示
```

## Phase 1: 同期スクリプト実行

**Phase 1開始時**: TodoWriteで「Phase 1」を `in_progress` に更新

### 1-1. スクリプトの実行

以下のコマンドを実行する：

```bash
python3 ~/Documents/Git/ai-toolkit/skills/manage-resources/sync.py
```

**`--dry-run` オプション**: 事前確認が必要な場合は以下を実行：

```bash
python3 ~/Documents/Git/ai-toolkit/skills/manage-resources/sync.py --dry-run
```

**成功確認**: JSON結果が出力された → Phase 2へ

**Phase 1完了時**: TodoWriteで「Phase 1」を `completed` に更新

---

## Phase 2: 結果の表示

**Phase 2開始時**: TodoWriteで「Phase 2」を `in_progress` に更新

### 2-1. 結果の整形

Phase 1のJSON出力から以下のマークダウン表を作成して表示する：

```markdown
## 同期結果

| カテゴリ | コピー | スキップ（変更なし） | エラー |
|---------|--------|-------------------|--------|
| commands | X件 | Y件 | Z件 |
| agents | X件 | Y件 | Z件 |
| rules | X件 | Y件 | Z件 |
| skills | X件 | Y件 | Z件 |

### コピーされたファイル
- ...
```

- コピーされたファイルがある場合はファイル名を一覧表示
- エラーがある場合はエラー内容を表示
- 全てスキップの場合は「すべて最新です。変更はありません。」と表示
- `onlyInDest` がある場合は「~/.claude/ にのみ存在（同期対象外）」として一覧表示

**成功確認**: 結果が表示された → 完了

**Phase 2完了時**: TodoWriteで「Phase 2」を `completed` に更新

---

## エラー対応

| エラー | 対応 |
|-------|------|
| ディレクトリが見つからない | ai-toolkitリポジトリのパスを確認 |
| Permission denied | ~/.claude/ の書き込み権限を確認 |

## 注意事項

- 同期方向は ai-toolkit → ~/.claude/ の一方向のみ
- ~/.claude/ にしか存在しないファイル・ディレクトリは削除しない
- 差分があるファイルのみコピーする（ファイル内容のハッシュ比較）
- skills/ はサブディレクトリ（scripts/等）も含めて再帰的にコピー
