# 振り返りスキル設定

リソースのURL変更時はYAMLブロック内の該当箇所を編集してください。
スクリプトがURLからファイルIDを自動抽出します。

## リソース設定

```yaml
lifegraph:
  url: "https://docs.google.com/spreadsheets/d/1f3U95xxzoSuIJpdKVL3SQMIEqkDYT_INvmaYCnqPZzU/edit?usp=drive_link"
  sheet_name: "Googleカレンダー集計"
  columns: "A:P"

daily:
  url: "https://docs.google.com/document/d/1xWbRWz_hdwf1HLq3JbiwRCqVXTYUYhQ83KUbYSk7XWI/edit?usp=drive_link"
  goals_tab: "今年の目標"
  month_tab: "202603"

money:
  url: "https://docs.google.com/spreadsheets/d/1G68GW1v_Dt6XHNLIYq0rau6iUKjskdzSfs_42HPAVHo/edit?usp=drive_link"
  sheets:
    - name: "予算_給与負担"
      columns: "A:G"
    - name: "マネープラン"
      columns: "A:AN"

summary:
  url: "https://docs.google.com/document/d/1B1kGaDmM80-vzpBtDqe6Ibl12aWM80Zk-Wjvhi68oYA/edit?usp=drive_link"
```
