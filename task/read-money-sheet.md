# 金銭管理のスプレッドシートを読み取るタスク

# スプレッドシートのリンク
https://docs.google.com/spreadsheets/d/1P519LiN0Tiu-NvWuYgek9jc4IfvXTzIukkVkuokAqY0/edit?usp=sharing

# 「マネープラン」シートの構造
・E列のみ現金資産です
・K,L列には年金保険の積立実績額が入力してあります
・J列はiDeCoの資産額のため、住宅ローンにはあてられません
・O列の副収入には、定期券代など普段の給与より多くもらった時の金額を入力しています
・Q〜T列の投資額はAL列の支出額としてカウントしていません
・X~AA列の値を合計した金額を当月の食費として計算してください
・AI列の娯楽費には散髪代や病院代、ガソリン代などの変動費も含んでいます。
・パートナーのおこづかいには病院代も含まれているため、一般家庭よりは高額になります

# 手順
1. mcp-google-driveのg_drive_get_file_structure ツールを使い、シート構造を把握してください
2. mcp-google-driveのg_drive_read_file_part ツールを使い、「予算：給与負担」シートのA~G列を全て読んでください
3. mcp-google-driveのg_drive_read_file_part ツールを使い、「マネープラン」シートのA~AN列を全て読んでください
