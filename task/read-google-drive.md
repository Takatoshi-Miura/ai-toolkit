# スプレッドシートやGoogleドキュメントを読み取るタスク

# 手順
1. 以下の情報が提供されていなければユーザーに質問して提供してもらう
    - スプレッドシートまたはGoogleドキュメントのURL（必須）
    - 読み込みたいシート名またはドキュメントタブ名（任意）
2. mcp-google-drive__g_drive_get_file_structure を使い、ファイル構造を把握する
3. 読み込みたいシート名やドキュメントタブがある場合は手順4、指定がない場合は手順5を実行
4. mcp-google-drive__g_drive_read_file_part を使い、読み込みたいシートやドキュメントタブを読む
5. mcp-google-drive__g_drive_read_file を使い、全てを読む
6. 読み込みが成功したら終了