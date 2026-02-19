#!/usr/bin/env python3
"""
スプレッドシートのセル背景色をハイライトするCLI

使用方法:
    python scripts/highlight_cells.py <fileId> <range> [--color <color_name>]

例:
    python scripts/highlight_cells.py 1abc...xyz "Sheet1!A1:B2"
    python scripts/highlight_cells.py 1abc...xyz "Sheet1!A1:B2" --color light_green

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


# プリセット色の定義（RGB float 0.0〜1.0）
PRESET_COLORS = {
    "yellow":       {"red": 1.0, "green": 1.0, "blue": 0.0},
    "light_yellow": {"red": 1.0, "green": 1.0, "blue": 0.6},
    "green":        {"red": 0.0, "green": 1.0, "blue": 0.0},
    "light_green":  {"red": 0.85, "green": 0.95, "blue": 0.85},
    "blue":         {"red": 0.0, "green": 0.0, "blue": 1.0},
    "light_blue":   {"red": 0.85, "green": 0.92, "blue": 1.0},
    "red":          {"red": 1.0, "green": 0.0, "blue": 0.0},
    "light_red":    {"red": 1.0, "green": 0.85, "blue": 0.85},
    "orange":       {"red": 1.0, "green": 0.65, "blue": 0.0},
    "none":         {"red": 1.0, "green": 1.0, "blue": 1.0},
}

DEFAULT_COLOR = "yellow"


def highlight_cells(creds: Any, file_id: str, range_str: str, color_name: str = DEFAULT_COLOR) -> dict:
    """スプレッドシートのセル背景色を変更

    Args:
        creds: 認証クライアント
        file_id: スプレッドシートのファイルID
        range_str: 範囲文字列（例: "Sheet1!A1:B2"）
        color_name: 色名（PRESET_COLORSのキー、デフォルト: yellow）

    Returns:
        結果を示すdict
    """
    if color_name not in PRESET_COLORS:
        return {
            "success": False,
            "fileId": file_id,
            "fileType": "sheets",
            "operation": "highlight",
            "range": range_str,
            "error": f"未知の色名です: {color_name}",
            "availableColors": list(PRESET_COLORS.keys())
        }

    color = PRESET_COLORS[color_name]
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
                "operation": "highlight",
                "range": range_str,
                "error": f'シート "{sheet_name}" が見つかりません',
                "availableSheets": available_sheets
            }

        # セル背景色変更リクエスト（repeatCell を使用）
        response = service.spreadsheets().batchUpdate(
            spreadsheetId=file_id,
            body={
                "requests": [
                    {
                        "repeatCell": {
                            "range": {
                                "sheetId": sheet_id,
                                "startRowIndex": cell_range["startRow"],
                                "endRowIndex": cell_range["endRow"],
                                "startColumnIndex": cell_range["startCol"],
                                "endColumnIndex": cell_range["endCol"]
                            },
                            "cell": {
                                "userEnteredFormat": {
                                    "backgroundColor": color
                                }
                            },
                            "fields": "userEnteredFormat.backgroundColor"
                        }
                    }
                ]
            }
        ).execute()

        return {
            "success": True,
            "fileId": file_id,
            "fileType": "sheets",
            "operation": "highlight",
            "sheetName": sheet_name,
            "sheetId": sheet_id,
            "range": range_str,
            "color": color_name,
            "colorRgb": color,
            "highlightedRange": {
                "startRow": cell_range["startRow"] + 1,
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
            "operation": "highlight",
            "range": range_str,
            "error": str(e)
        }
    except Exception as e:
        return {
            "success": False,
            "fileId": file_id,
            "fileType": "sheets",
            "operation": "highlight",
            "range": range_str,
            "error": str(e)
        }


def print_usage():
    """使用方法を表示"""
    print("""
使用方法:
    python scripts/highlight_cells.py <fileId> <range> [--color <color_name>]

引数:
    fileId  - スプレッドシートのファイルID
    range   - ハイライトするセル範囲（形式: シート名!開始セル:終了セル）

オプション:
    --color - 色名（デフォルト: yellow）

利用可能な色:
    yellow（黄）, light_yellow（薄黄）, green（緑）, light_green（薄緑）,
    blue（青）, light_blue（薄青）, red（赤）, light_red（薄赤）,
    orange（橙）, none（白 = ハイライト解除）

例:
    # A1からB2までのセルを黄色でハイライト
    python scripts/highlight_cells.py 1abc...xyz "Sheet1!A1:B2"

    # 薄緑色でハイライト
    python scripts/highlight_cells.py 1abc...xyz "Sheet1!A1:B2" --color light_green

    # ハイライトを解除（白に戻す）
    python scripts/highlight_cells.py 1abc...xyz "Sheet1!A1:B2" --color none

注意:
    - このスクリプトはスプレッドシートのみで動作します
    - 範囲は「シート名!セル範囲」の形式で指定してください
    - セル範囲は「A1:B2」のような形式で指定してください
""")


def main():
    """CLI エントリーポイント"""
    parser = argparse.ArgumentParser(
        description="スプレッドシートのセル背景色をハイライト",
        add_help=False
    )
    parser.add_argument("file_id", nargs="?", help="スプレッドシートのファイルID")
    parser.add_argument("range", nargs="?", help="ハイライトするセル範囲（例: Sheet1!A1:B2）")
    parser.add_argument("--color", default=DEFAULT_COLOR, help=f"色名（デフォルト: {DEFAULT_COLOR}）")
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

    # ハイライトを実行
    result = highlight_cells(creds, args.file_id, args.range, args.color)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
