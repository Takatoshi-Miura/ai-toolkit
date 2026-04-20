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

任意の場所に working folder を作成し、以下の 3 ファイルを配置する。

#### CONFIG.md

```markdown
# 設定

## 宛先
- groupId: C1234567890abcdef...

## 調査条件

- エリア: 蓮田駅(埼玉県)から片道 1 時間以内
- 移動手段: 車で行ける場所を優先。車アクセスが良いスポットを上位に扱う
- ジャンル: 屋内外どちらも可。美術館・公園・カフェ巡り・自然散策が好み
- 避けたいもの: 強い混雑、行列必須の人気スポット、派手なテーマパーク、駐車場が確保できない場所
- 同行者: 2 人(自分を含む)
- 対象日: 次の土曜日。雨天なら屋内中心に切り替える
- 除外: history.md に含まれる場所はすべて選ばない

## メッセージフォーマット

以下のテンプレートに沿って本文を組み立てる。各行は必須。絵文字は 1 行目のみ可。

🗓 {対象日(YYYY/MM/DD (曜))}
📍 {スポット名}({市町村名 / 蓮田から車で約 X 分})
⏱ 片道目安 {所要時間}
💡 {おすすめ理由を 2〜3 行}
🚗 車: {所要時間・駐車場の有無や料金}
🔗 公式: {公式 URL}
🗺 地図: {Google Maps URL}
```

#### history.md

```markdown
# 提案履歴

<!-- 各実行後、SKILL.md の手順に従って 1 行追記される -->
<!-- 形式: YYYY-MM-DD | スポット名 -->
```

#### line_config.json

```json
{
  "channel_access_token": "<LINE Messaging API のチャネルアクセストークン>"
}
```

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
