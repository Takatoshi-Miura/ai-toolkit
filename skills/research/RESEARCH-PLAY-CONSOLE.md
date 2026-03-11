# Google Play Console 更新情報収集ワークフロー

情報収集のエキスパートとしてGooglePlayConsole関連の更新情報を収集する。

日本語で回答すること。

## TodoWrite チェックリスト

```json
[
  {"content": "Phase 1: 公式ソースからの情報収集", "activeForm": "公式ソースから情報を収集中", "status": "pending"},
  {"content": "Phase 2: 情報の取捨選択", "activeForm": "情報を取捨選択中", "status": "pending"},
  {"content": "Phase 3: 結果報告", "activeForm": "結果を報告中", "status": "pending"},
  {"content": "Phase 4: フォローアップ", "activeForm": "フォローアップ中", "status": "pending"}
]
```

---

## Phase 1: 情報収集

**Phase 1開始時**: TodoWriteで「Phase 1」を `in_progress` に更新

以下の公式ソースをWebFetchで読み取り、**今日の日付を基準に過去30日間**に追加された新しい情報がないか調査する：

| # | ソース | URL |
|---|--------|-----|
| 1 | PlayConsole お知らせページ | https://support.google.com/googleplay/android-developer/announcements/13412212?sjid=17300191523255210031-NC |
| 2 | Android Studio リリースノート | https://developer.android.com/studio/releases?hl=ja |
| 3 | Android Developers Blog | https://android-developers.googleblog.com/search/label/Google%20Play |
| 4 | Google Play ニュースレター | https://play.google.com/intl/ja/console/about/newsletter/#read-the-latest-issue |

**成功確認**: 全4ソースの情報収集が完了した → Phase 2へ

**Phase 1完了時**: TodoWriteで「Phase 1」を `completed` に更新

---

## Phase 2: 情報の取捨選択

**Phase 2開始時**: TodoWriteで「Phase 2」を `in_progress` に更新

以下の判断基準に従って情報の取捨選択を行う：

### 対象プロジェクト

- `automata-android`（~/Documents/Git/automata-android）- 経費精算アプリ（BtoB、日本向け）
- `automata-android-ic`（~/Documents/Git/automata-android-ic）- ICカード読み取りアプリ（BtoB、日本向け）

### 判定基準

- 対象アプリに影響あり → 重要情報「有」
- 対象アプリに影響なし → 重要情報「無」

**成功確認**: 全情報の重要度判定が完了した → Phase 3へ

**Phase 2完了時**: TodoWriteで「Phase 2」を `completed` に更新

---

## Phase 3: 結果報告

**Phase 3開始時**: TodoWriteで「Phase 3」を `in_progress` に更新

以下の出力形式に従って結果を返却する：

```
## GooglePlayConsole関連の更新情報の調査結果

### 重要な情報の有無
- 「有」または「無」

### 上記の理由

| 更新内容 | 対象 | 影響判定 |
|---------|------|---------|
| [更新内容へのリンク](URL) | android / android-ic | 影響あり / 影響なし |
```

**Phase 3完了時**: TodoWriteで「Phase 3」を `completed` に更新

---

## Phase 4: フォローアップ

**Phase 4開始時**: TodoWriteで「Phase 4」を `in_progress` に更新

調査結果をユーザーに共有し、追加調査や疑問点などがないか質問する。

不明点がなくなるまでフォローアップを繰り返す。

**Phase 4完了時**: TodoWriteで「Phase 4」を `completed` に更新

---

## エラー対応

| エラー | 対応 |
|-------|------|
| WebFetchでページが取得できない | URLを確認し、別のソースで代替 |
| ネットワークエラー | ネットワーク接続を確認し、再実行を案内 |
| ページ構造が変わっていた | 手動での内容確認をユーザーに提案 |
