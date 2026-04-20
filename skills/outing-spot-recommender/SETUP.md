# outing-spot-recommender セットアップ

## 前提条件

- LINE Messaging API チャネルが作成済みで、channel access token を入手済みであること
- bot を通知したい LINE グループに招待済みであること

---

## セットアップ手順

### 1. スキルのアップロード(Cowork)

1. このフォルダ(`outing-spot-recommender/`)を ZIP 化する
2. Cowork の左サイドバー Customize → Skills → 「+」から ZIP をアップロード

### 2. working folder の作成

任意の場所に working folder を作成し、スキルフォルダ内の以下の 3 ファイルをコピーする。

| コピー元(スキルフォルダ内) | コピー先(working folder) |
|---|---|
| `CONFIG.md` | `<working folder>/CONFIG.md` |
| `history.md` | `<working folder>/history.md` |
| `line_config.json` | `<working folder>/line_config.json` |

> **重要**: line_config.json はバージョン管理システムにコミットしない。

### 3. 実値の記入

- CONFIG.md の `groupId` を実際の LINE グループ ID に書き換える
- line_config.json の `channel_access_token` を実際のトークンに書き換える

### 4. スケジュールタスクの作成(Cowork)

| 項目 | 値 |
|------|----|
| Name | `weekly-outing-suggestion` など任意 |
| Prompt | `outing-spot-recommender` スキルを使って、今週土曜のお出かけ先を 1 つ提案し LINE グループに送って |
| Frequency | 毎週金曜 19:00 など任意 |
| Working folder | 上記で作成した working folder |
| Model | Sonnet 以上(web 検索と判断が必要) |

### 5. 動作確認

一度手動で実行し、以下を確認する：
- LINE グループへの送信が成功すること
- history.md にスポット名が追記されること

---

## LINE groupId の取得方法

1. bot を通知したい LINE グループに招待する
2. webhook ハンドラがある場合は、グループ内で誰かが発言した際のイベント JSON から `source.groupId` を取得
3. webhook 未実装の場合：
   - LINE Developers コンソールで webhook URL を requestbin などのテスト受信サービスに一時変更
   - グループで一言発言してイベントを受信
   - `source.groupId` を取得後、元の設定に戻す
4. 取得した groupId を CONFIG.md の「宛先」に記入する

---

## 運用上の注意

- Cowork のローカルスケジュールタスクは PC 起動中にのみ実行される。スケジュール時刻に PC が起動している時間帯を選ぶこと
- history.md が肥大化しても動作に支障はないが、気になる場合は古い記録を別ファイルに退避する

## 変更が起きたときの対応箇所

| やりたいこと | 編集するファイル |
|---|---|
| 条件を変えたい(エリア・ジャンル・避けたいもの等) | CONFIG.md の「調査条件」 |
| 宛先を別グループにしたい | CONFIG.md の「宛先」 |
| メッセージの見た目を変えたい | CONFIG.md の「メッセージフォーマット」 |
| 実行時刻・頻度を変えたい | Cowork のスケジュールタスク設定 |
| ロジックを変えたい(手順・除外ルール等) | SKILL.md |
| LINE 送信方法を変えたい(broadcast 等) | scripts/send_line.py |
| トークンを更新したい | line_config.json |
