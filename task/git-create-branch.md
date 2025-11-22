# ブランチを作成するタスク

# 指示
1. 以下の情報が提供されていないければ、ユーザーに質問して提供してもらう
    - ブランチ名
2. `git checkout -b <branch_name>`コマンドで、指定されたブランチ名でブランチを作成し、そのブランチにチェックアウトしてください

# ブランチ名の形式
[prefix]/[チケット番号]/[実装内容に適した命名]

# 命名規則
- prefix: ユーザーから提供されたprefix（例: currency_selection, continuous_capture）
- チケット番号: Redmineチケットから抽出した番号（#を除く）
- 実装内容: 実装内容を端的に表す英語の命名（例: fix_amount_clear_display, add_user_validation）
- 例
    - continuous_capture/12345/fix_close_button_position
    - currency_selection/116621/fix_amount_clear_display