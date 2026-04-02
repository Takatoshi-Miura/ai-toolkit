# 振り返りスキル設定

リソースのURL変更時はYAMLブロック内の該当箇所を編集してください。
スクリプトがURLからファイルIDを自動抽出します。

## リソース設定

```yaml
lifegraph:
  url: "https://docs.google.com/spreadsheets/d/1WF58VNM0lGfN-YKqR2ySXU_EKQQCpyrV4da8WiVtoBo/edit?usp=sharing"
  sheet_name: "Googleカレンダー集計"
  columns: "A:P"

daily:
  url: "https://docs.google.com/document/d/1iVeZ1EB5dahEZukuQQB4gSa5jIw3By-Gz8JaAysiAoA/edit?usp=sharing"
  goals_tab: "今年の目標"
  month_tab: "202603"

money:
  url: "https://docs.google.com/spreadsheets/d/1P519LiN0Tiu-NvWuYgek9jc4IfvXTzIukkVkuokAqY0/edit?usp=sharing"
  sheets:
    - name: "予算_給与負担"
      columns: "A:G"
    - name: "マネープラン"
      columns: "A:AN"

summary:
  url: "https://docs.google.com/document/d/1hDcVtQ5wEz2rPGRrJGK8CspnqSujheAjeZ1PPAj2u6E/edit?usp=sharing"

calendar:
  calendar_id: "primary"
  timezone: "Asia/Tokyo"
  tag_mapping:
    "#work": "仕事"
    "#life": "生活"
    "#sleep": "睡眠"
    "#undo": "運動"
    "#idea": "思考整理"
    "#ref": "リフレッシュ"
    "#douga": "YouTube活動"
    "#skill": "自己研鑽"
    "#book": "読書"
    "#code": "プログラミング"
    "#chi": "パートナー"
```
