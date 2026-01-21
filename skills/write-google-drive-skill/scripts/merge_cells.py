#!/usr/bin/env python3
"""
スプレッドシートのセルを結合するCLI

使用方法:
    python scripts/merge_cells.py <fileId> <range>

例:
    python scripts/merge_cells.py 1abc...xyz "Sheet1!A1:B2"

認証ファイル:
    ~/.config/google-drive-skills/client_secret.json
    ~/.config/google-drive-skills/token.json
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

# 同じディレクトリのauthモジュールをインポート
sys.path.insert(0, str(Path(__file__).parent))
from auth import get_auth_client

from googleapiclient.discovery import build


def parse_range(range_str: str) -> tuple[str, dict]:
    """範囲文字列を解析してシート名とセル範囲を取得

    Args:
        range_str: 範囲文字列（例: "Sheet1!A1:B2"）

    Returns:
        tuple: (シート名, {"startRow": 0, "endRow": 2, "startCol": 0, "endCol": 2})
    """
    # シート名とセル範囲を分離
    parts = range_str.split("!")
    if len(parts) != 2:
        raise ValueError(f"無効な範囲形式です。正しい形式: シート名!A1:B2 (入力: {range_str})")

    sheet_name = parts[0]
    cell_range = parts[1]

    # セル範囲を解析（例: A1:B2）
    match = re.match(r"([A-Z]+)(\d+):([A-Z]+)(\d+)", cell_range)
    if not match:
        raise ValueError(f"無効なセル範囲形式です: {cell_range}")

    start_col_str, start_row_str, end_col_str, end_row_str = match.groups()

    # 列文字を数値に変換
    def col_to_index(col_str: str) -> int:
        index = 0
        for char in col_str:
            index = index * 26 + (ord(char) - ord('A') + 1)
        return index - 1  # 0ベース

    start_col = col_to_index(start_col_str)
    end_col = col_to_index(end_col_str)
    start_row = int(start_row_str) - 1  # 0ベース
    end_row = int(end_row_str)  # endは排他的なのでそのまま

    return sheet_name, {
        "startRow": start_row,
        "endRow": end_row,
        "startCol": start_col,
        "endCol": end_col + 1  # endは排他的
    }


def merge_cells(creds: Any, file_id: str, range_str: str) -> dict:
    """スプレッドシートのセルを結合

    Args:
        creds: 認証クライアント
        file_id: スプレッドシートのファイルID
        range_str: 範囲文字列（例: "Sheet1!A1:B2"）

    Returns:
        結果を示すdict
    """
    service = build("sheets", "v4", credentials=creds)

    try:
        # 範囲を解析
        sheet_name, cell_range = parse_range(range_str)

        # シート情報を取得してsheetIdを取得
        spreadsheet_info = service.spreadsheets().get(
            spreadsheetId=file_id,
            fields="sheets.properties"
        ).execute()

        sheet_id = None
        for sheet in spreadsheet_info.get("sheets", []):
            if sheet.get("properties", {}).get("title") == sheet_name:
                sheet_id = sheet["properties"]["sheetId"]
                break

        if sheet_id is None:
            available_sheets = [s.get("properties", {}).get("title") for s in spreadsheet_info.get("sheets", [])]
            return {
                "success": False,
                "fileId": file_id,
                "fileType": "sheets",
                "operation": "merge",
                "range": range_str,
                "error": f'シート "{sheet_name}" が見つかりません',
                "availableSheets": available_sheets
            }

        # セル結合リクエスト
        response = service.spreadsheets().batchUpdate(
            spreadsheetId=file_id,
            body={
                "requests": [
                    {
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
                    }
                ]
            }
        ).execute()

        return {
            "success": True,
            "fileId": file_id,
            "fileType": "sheets",
            "operation": "merge",
            "sheetName": sheet_name,
            "sheetId": sheet_id,
            "range": range_str,
            "mergedRange": {
                "startRow": cell_range["startRow"] + 1,  # 1ベースに戻す
                "endRow": cell_range["endRow"],
                "startCol": cell_range["startCol"] + 1,
                "endCol": cell_range["endCol"]
            }
        }
    except ValueError as e:
        return {
            "success": False,
            "fileId": file_id,
            "fileType": "sheets",
            "operation": "merge",
            "range": range_str,
            "error": str(e)
        }
    except Exception as e:
        return {
            "success": False,
            "fileId": file_id,
            "fileType": "sheets",
            "operation": "merge",
            "range": range_str,
            "error": str(e)
        }


def print_usage():
    """使用方法を表示"""
    print("""
使用方法:
    python scripts/merge_cells.py <fileId> <range>

引数:
    fileId  - スプレッドシートのファイルID
    range   - 結合するセル範囲（形式: シート名!開始セル:終了セル）

例:
    # A1からB2までのセルを結合
    python scripts/merge_cells.py 1abc...xyz "Sheet1!A1:B2"

    # 「売上」シートのC3からE5までのセルを結合
    python scripts/merge_cells.py 1abc...xyz "売上!C3:E5"

注意:
    - このスクリプトはスプレッドシートのみで動作します
    - 範囲は「シート名!セル範囲」の形式で指定してください
    - セル範囲は「A1:B2」のような形式で指定してください
""")


def main():
    """CLI エントリーポイント"""
    parser = argparse.ArgumentParser(
        description="スプレッドシートのセルを結合",
        add_help=False
    )
    parser.add_argument("file_id", nargs="?", help="スプレッドシートのファイルID")
    parser.add_argument("range", nargs="?", help="結合するセル範囲（例: Sheet1!A1:B2）")
    parser.add_argument("-h", "--help", action="store_true", help="ヘルプを表示")

    args = parser.parse_args()

    if args.help or not all([args.file_id, args.range]):
        print_usage()
        sys.exit(0 if args.help else 1)

    # 認証
    creds = get_auth_client()
    if not creds:
        result = {
            "success": False,
            "error": "認証に失敗しました"
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(1)

    # セル結合を実行
    result = merge_cells(creds, args.file_id, args.range)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
