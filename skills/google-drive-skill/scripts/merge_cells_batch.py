#!/usr/bin/env python3
"""
スプレッドシートの複数セル範囲を一括結合するCLI

使用方法:
    python scripts/merge_cells_batch.py <fileId> <json_ranges>

例:
    python scripts/merge_cells_batch.py 1abc...xyz '["Sheet1!A1:A5","Sheet1!B1:B3"]'

認証ファイル:
    ~/.config/google-drive-skills/client_secret.json
    ~/.config/google-drive-skills/token.json
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# 同じディレクトリのモジュールをインポート
sys.path.insert(0, str(Path(__file__).parent))
from auth import get_auth_client
from merge_cells import parse_range

from googleapiclient.discovery import build


def merge_cells_batch(creds: Any, file_id: str, ranges: list[str]) -> dict:
    """複数のセル範囲を一括結合

    Args:
        creds: 認証クライアント
        file_id: スプレッドシートのファイルID
        ranges: 結合する範囲のリスト（例: ["Sheet1!A1:A5", "Sheet1!B1:B3"]）

    Returns:
        結果を示すdict
    """
    service = build("sheets", "v4", credentials=creds)

    # 1. シート情報を取得
    try:
        spreadsheet_info = service.spreadsheets().get(
            spreadsheetId=file_id,
            fields="sheets.properties"
        ).execute()
    except Exception as e:
        return {
            "success": False,
            "fileId": file_id,
            "fileType": "sheets",
            "operation": "batch_merge",
            "error": f"スプレッドシート情報の取得に失敗しました: {e}"
        }

    sheet_id_map = {
        sheet["properties"]["title"]: sheet["properties"]["sheetId"]
        for sheet in spreadsheet_info.get("sheets", [])
    }
    available_sheets = list(sheet_id_map.keys())

    # 2. 全範囲を検証・パース
    validation_errors = []
    merge_requests = []
    parsed_ranges = []

    for range_str in ranges:
        try:
            sheet_name, cell_range = parse_range(range_str)

            if sheet_name not in sheet_id_map:
                validation_errors.append({
                    "range": range_str,
                    "error": f"シート '{sheet_name}' が見つかりません"
                })
                continue

            sheet_id = sheet_id_map[sheet_name]
            merge_requests.append({
                "mergeCells": {
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": cell_range["startRow"],
                        "endRowIndex": cell_range["endRow"],
                        "startColumnIndex": cell_range["startCol"],
                        "endColumnIndex": cell_range["endCol"]
                    },
                    "mergeType": "MERGE_ALL"
                }
            })
            parsed_ranges.append({
                "range": range_str,
                "sheetId": sheet_id,
                "mergedRange": {
                    "startRow": cell_range["startRow"] + 1,
                    "endRow": cell_range["endRow"],
                    "startCol": cell_range["startCol"] + 1,
                    "endCol": cell_range["endCol"]
                }
            })
        except ValueError as e:
            validation_errors.append({
                "range": range_str,
                "error": str(e)
            })

    # 3. 検証エラーがあれば返す
    if validation_errors:
        return {
            "success": False,
            "fileId": file_id,
            "fileType": "sheets",
            "operation": "batch_merge",
            "error": "入力検証エラー",
            "validationErrors": validation_errors,
            "availableSheets": available_sheets
        }

    # 4. 結合する範囲がない場合
    if not merge_requests:
        return {
            "success": False,
            "fileId": file_id,
            "fileType": "sheets",
            "operation": "batch_merge",
            "error": "結合する範囲がありません"
        }

    # 5. 一括結合実行
    try:
        service.spreadsheets().batchUpdate(
            spreadsheetId=file_id,
            body={"requests": merge_requests}
        ).execute()

        return {
            "success": True,
            "fileId": file_id,
            "fileType": "sheets",
            "operation": "batch_merge",
            "totalRanges": len(merge_requests),
            "mergedRanges": parsed_ranges
        }
    except Exception as e:
        return {
            "success": False,
            "fileId": file_id,
            "fileType": "sheets",
            "operation": "batch_merge",
            "error": f"セル結合の実行に失敗しました: {e}"
        }


def print_usage():
    """使用方法を表示"""
    print("""
使用方法:
    python scripts/merge_cells_batch.py <fileId> <json_ranges>

引数:
    fileId      - スプレッドシートのファイルID
    json_ranges - 結合するセル範囲のJSON配列

例:
    # 複数範囲を一括結合
    python scripts/merge_cells_batch.py 1abc...xyz '["Sheet1!A4:A10","Sheet1!B4:B8"]'

    # 日本語シート名もサポート
    python scripts/merge_cells_batch.py 1abc...xyz '["因子表!B4:B15","因子表!C4:C10"]'

注意:
    - このスクリプトはスプレッドシートのみで動作します
    - 範囲は「シート名!セル範囲」の形式で指定してください
    - セル範囲は「A1:B2」のような形式で指定してください
    - 単一範囲の結合には merge_cells.py を使用することもできます
""")


def main():
    """CLI エントリーポイント"""
    parser = argparse.ArgumentParser(
        description="スプレッドシートの複数セル範囲を一括結合",
        add_help=False
    )
    parser.add_argument("file_id", nargs="?", help="スプレッドシートのファイルID")
    parser.add_argument("ranges", nargs="?", help="結合する範囲のJSON配列")
    parser.add_argument("-h", "--help", action="store_true", help="ヘルプを表示")

    args = parser.parse_args()

    if args.help or not all([args.file_id, args.ranges]):
        print_usage()
        sys.exit(0 if args.help else 1)

    # JSON パース
    try:
        ranges = json.loads(args.ranges)
        if not isinstance(ranges, list):
            raise ValueError("配列である必要があります")
        if not all(isinstance(r, str) for r in ranges):
            raise ValueError("配列の要素はすべて文字列である必要があります")
    except (json.JSONDecodeError, ValueError) as e:
        result = {
            "success": False,
            "error": f"ranges は有効なJSON配列である必要があります: {e}"
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(1)

    # 認証
    creds = get_auth_client()
    if not creds:
        result = {"success": False, "error": "認証に失敗しました"}
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(1)

    # 実行
    result = merge_cells_batch(creds, args.file_id, ranges)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
