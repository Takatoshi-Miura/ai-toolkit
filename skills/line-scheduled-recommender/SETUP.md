# line-scheduled-recommender セットアップ

## 前提条件

- LINE Messaging API チャネルが作成済みで、channel access token を入手済みであること
- bot を通知したい LINE グループに招待済みであること

---

## セットアップ手順

### 1. スキルのアップロード（Cowork）

1. `skills/line-scheduled-recommender/` フォルダを ZIP 化する
2. Cowork の左サイドバー Customize → Skills → 「+」から ZIP をアップロード

### 2. working folder の作成

Cowork 上で任意の working folder を作成し、スキルフォルダ内の `working-folder-template/` の**中身を丸ごと**コピーする。

```
working-folder-template/ の中身
├── CONFIG.md
├── line_config.json
├── outing/
│   └── history.md
└── book/
    └── history.md
```

> **重要**: `line_config.json` はバージョン管理システムにコミットしない。

### 3. 実値の記入

#### line_config.json

```json
{
  "channel_access_token": "実際のトークンに書き換える"
}
```

#### CONFIG.md

1. スケジュール表の時刻を Cowork のスケジュールタスクの実行時刻に合わせる
2. 使用する各テーマの `groupId` を実際の LINE グループ ID に書き換える
3. 不要なテーマ行はスケジュール表から削除する（セクションも削除してよい）

### 4. スケジュールタスクの作成（Cowork）

CONFIG.md のスケジュール表に記載した時刻ごとにタスクを作成する。

| 項目 | 値 |
|------|----|
| Name | `line-recommender-07:00` など任意 |
| Prompt | `line-scheduled-recommender スキルを使って、LINE グループに通知して` |
| Frequency | 毎週金曜 07:00 など CONFIG.md に合わせた時刻 |
| Working folder | 上記で作成した working folder |
| Model | Sonnet 以上（web 検索と判断が必要） |

> **ヒント**: 複数テーマを運用する場合でも working folder は 1 つでよい。スケジュールタスクを時刻ごとに複数作成し、すべて同じ working folder を指定する。

### 5. 動作確認

一度手動で実行し、以下を確認する：
- 現在時刻が CONFIG.md のスケジュールに一致するテーマが選択されること
- LINE グループへの送信が成功すること
- `{theme}/history.md` に記録が追記されること

---

## テーマの追加方法

1. `CONFIG.md` のスケジュール表に行を追加する：

   ```
   | 20:00 | news | 夜のニュース要約 |
   ```

2. `CONFIG.md` に新しいテーマセクションを追加する：

   ```markdown
   # テーマ: news
   
   ## 宛先
   - groupId: C...
   
   ## 調査条件
   ...
   
   ## メッセージフォーマット
   ...
   ```

3. working folder に `news/history.md` を作成する（空ファイルで可）

4. Cowork に対応するスケジュールタスクを追加する

---

## LINE groupId の取得方法

1. bot を通知したい LINE グループに招待する
2. webhook ハンドラがある場合は、グループ内で誰かが発言した際のイベント JSON から `source.groupId` を取得
3. webhook 未実装の場合：
   - LINE Developers コンソールで webhook URL を requestbin などのテスト受信サービスに一時変更
   - グループで一言発言してイベントを受信
   - `source.groupId` を取得後、元の設定に戻す
4. 取得した groupId を CONFIG.md の該当テーマセクションに記入する

---

## 運用上の注意

- Cowork のローカルスケジュールタスクは PC 起動中にのみ実行される。スケジュール時刻に PC が起動している時間帯を選ぶこと
- `{theme}/history.md` が肥大化しても動作に支障はないが、気になる場合は古い記録を別ファイルに退避する
- 時刻判定の許容幅は **+0〜+15 分**（遅延のみ許容）。PC スリープ明け等で最大 15 分遅れても正常動作する

## 変更が起きたときの対応箇所

| やりたいこと | 編集するファイル |
|---|---|
| スケジュール時刻を変えたい | CONFIG.md のスケジュール表 + Cowork のタスク設定 |
| テーマの条件を変えたい | CONFIG.md の該当テーマセクション |
| 宛先グループを変えたい | CONFIG.md の該当テーマの groupId |
| メッセージの見た目を変えたい | CONFIG.md の該当テーマのメッセージフォーマット |
| テーマを追加・削除したい | CONFIG.md + `{theme}/history.md` + Cowork のタスク |
| ロジックを変えたい | SKILL.md |
| LINE 送信方法を変えたい | scripts/send_line.py |
| トークンを更新したい | line_config.json |
