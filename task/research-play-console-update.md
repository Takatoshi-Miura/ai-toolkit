# GooglePlayConsole関連の更新情報を取得するタスク

# 指示

1. 以下のリンクを読み取り、**今日の日付を基準に過去30日間**に追加された新しい情報がないか調査
    - [PlayConsole お知らせページ](https://support.google.com/googleplay/android-developer/announcements/13412212?sjid=17300191523255210031-NC)
    - [Android Studio リリースノート](https://developer.android.com/studio/releases?hl=ja)
    - [Android Developers Blog](https://android-developers.googleblog.com/search/label/Google%20Play)
    - [Google Play ニュースレター](https://play.google.com/intl/ja/console/about/newsletter/#read-the-latest-issue)

2. 以下の判断基準に従って情報の取捨選択を行う
    - 以下のプロジェクトをリリースしているので、これらのアプリに影響があるアップデートであれば重要情報。影響がないのであれば重要情報なしと判定する。
        - [automata-android](~/Documents/Git/automata-android) - 経費精算アプリ（BtoB、日本向け）
        - [automata-android-ic](~/Documents/Git/automata-android-ic)- ICカード読み取りアプリ（BtoB、日本向け）

3. 出力形式に従って結果を返却

# 出力形式

## GooglePlayConsole関連の更新情報の調査結果

### 重要な情報の有無
- 「有」「無」かを記入

### 上記の理由
- 理由を簡潔に記載
- 表形式で「更新内容」「対象」「影響判定」を整理
- 「更新内容」を押下するとリンク先URLに飛べること
