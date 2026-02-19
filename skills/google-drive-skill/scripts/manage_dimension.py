#!/usr/bin/env python3
"""
スプレッドシートの行/列を挿入・削除するCLI

使用方法:
    python scripts/manage_dimension.py <fileId> <action> <sheetName> <dimension> <start> [end] [--no-inherit]

例:
    # 3行目の前に2行挿入
    python scripts/manage_dimension.py 1abc...xyz insert "Sheet1" rows 3 4

    # B列の前に1列挿入
    python scripts/manage_dimension.py 1abc...xyz insert "Sheet1" columns 2

    # 3行目から5行目を削除
    python scripts/manage_dimension.py 1abc...xyz delete "Sheet1" rows 3 5

    # C列を削除
    python scripts/manage_dimension.py 1abc...xyz delete "Sheet1" columns 3

認証ファイル:
    ~/.config/google-drive-skills/client_secret.json
    ~/.config/google-drive-skills/token.json
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, List, Optional, Tuple

# 同じディレクトリのauthモジュールをインポート
sys.path.insert(0, str(Path(__file__).parent))
from auth import get_auth_client

from googleapiclient.discovery import build


def resolve_sheet_id(service: Any, file_id: str, sheet_name: str) -> Tuple[Optional[int], List[str]]:
    """シート名からsheetIdを解決する

    Args:
        service: Google Sheets APIサービス
        file_id: スプレッドシートのファイルID
        sheet_name: シート名

    Returns:
        tuple: (sheetId or None, available_sheet_names)
    """
    spreadsheet_info = service.spreadsheets().get(
        spreadsheetId=file_id,
        fields="sheets.properties"
    ).execute()

    available = []
    for sheet in spreadsheet_info.get("sheets", []):
        props = sheet.get("properties", {})
        available.append(props.get("title"))
        if props.get("title") == sheet_name:
            return props["sheetId"], available

    return None, available


def manage_dimension(
    creds: Any,
    file_id: str,
    action: str,
    sheet_name: str,
    dimension: str,
    start: int,
    end: int,
    inherit_before: bool = True,
) -> dict:
    """スプレッドシートの行/列を挿入・削除

    Args:
        creds: 認証クライアント
        file_id: スプレッドシートのファイルID
        action: "insert" または "delete"
        sheet_name: シート名
        dimension: "rows" または "columns"
        start: 開始位置（1ベース、包括的）
        end: 終了位置（1ベース、包括的）
        inherit_before: 挿入時に前の行/列の書式を継承するか

    Returns:
        結果を示すdict
    """
    service = build("sheets", "v4", credentials=creds)

    try:
        # シートIDを取得
        sheet_id, available_sheets = resolve_sheet_id(service, file_id, sheet_name)

        if sheet_id is None:
            return {
                "success": False,
                "fileId": file_id,
                "fileType": "sheets",
                "operation": f"{action}_dimension",
                "error": f'シート "{sheet_name}" が見つかりません',
                "availableSheets": available_sheets,
            }

        # 入力バリデーション
        if start < 1:
            raise ValueError(f"start は1以上である必要があります（入力: {start}）")
        if end < start:
            raise ValueError(f"end は start 以上である必要があります（start: {start}, end: {end}）")

        # 1ベース包括的 → 0ベース排他的に変換
        start_index = start - 1
        end_index = end  # 1ベース包括 → 0ベース排他で値が一致

        # リクエスト構築
        dimension_upper = dimension.upper()

        if action == "insert":
            request = {
                "insertDimension": {
                    "range": {
                        "sheetId": sheet_id,
                        "dimension": dimension_upper,
                        "startIndex": start_index,
                        "endIndex": end_index,
                    },
                    "inheritFromBefore": inherit_before,
                }
            }
        else:
            request = {
                "deleteDimension": {
                    "range": {
                        "sheetId": sheet_id,
                        "dimension": dimension_upper,
                        "startIndex": start_index,
                        "endIndex": end_index,
                    }
                }
            }

        # batchUpdate 実行
        service.spreadsheets().batchUpdate(
            spreadsheetId=file_id,
            body={"requests": [request]},
        ).execute()

        count = end - start + 1
        result = {
            "success": True,
            "fileId": file_id,
            "fileType": "sheets",
            "operation": f"{action}_dimension",
            "action": action,
            "sheetName": sheet_name,
            "sheetId": sheet_id,
            "dimension": dimension,
            "start": start,
            "end": end,
            "count": count,
        }

        if action == "insert":
            result["inheritFromBefore"] = inherit_before

        return result

    except ValueError as e:
        return {
            "success": False,
            "fileId": file_id,
            "fileType": "sheets",
            "operation": f"{action}_dimension",
            "error": str(e),
        }
    except Exception as e:
        return {
            "success": False,
            "fileId": file_id,
            "fileType": "sheets",
            "operation": f"{action}_dimension",
            "error": str(e),
        }


def print_usage():
    """使用方法を表示"""
    print("""
使用方法:
    python scripts/manage_dimension.py <fileId> <action> <sheetName> <dimension> <start> [end] [--no-inherit]

引数:
    fileId     - スプレッドシートのファイルID
    action     - 操作（insert: 挿入, delete: 削除）
    sheetName  - シート名
    dimension  - 対象（rows: 行, columns: 列）
    start      - 開始位置（1ベース）
    end        - 終了位置（1ベース、省略時: startと同じ = 1行/1列のみ）

オプション:
    --no-inherit  挿入時に前の行/列の書式を継承しない（デフォルト: 継承する）

例:
    # 3行目の前に2行挿入（3行目と4行目に空行が入る）
    python scripts/manage_dimension.py 1abc...xyz insert "Sheet1" rows 3 4

    # B列の前に1列挿入
    python scripts/manage_dimension.py 1abc...xyz insert "Sheet1" columns 2

    # 3行目から5行目を削除
    python scripts/manage_dimension.py 1abc...xyz delete "Sheet1" rows 3 5

    # C列を削除
    python scripts/manage_dimension.py 1abc...xyz delete "Sheet1" columns 3

    # 書式を継承せずに挿入
    python scripts/manage_dimension.py 1abc...xyz insert "Sheet1" rows 3 4 --no-inherit

注意:
    - このスクリプトはスプレッドシートのみで動作します
    - start / end は1ベース（スプレッドシート上の行番号・列番号と一致）
    - 列番号: A=1, B=2, C=3, D=4, ...
""")


def main():
    """CLI エントリーポイント"""
    parser = argparse.ArgumentParser(
        description="スプレッドシートの行/列を挿入・削除",
        add_help=False,
    )
    parser.add_argument("file_id", nargs="?", help="スプレッドシートのファイルID")
    parser.add_argument(
        "action", nargs="?", choices=["insert", "delete"],
        help="操作（insert: 挿入, delete: 削除）",
    )
    parser.add_argument("sheet_name", nargs="?", help="シート名")
    parser.add_argument(
        "dimension", nargs="?", choices=["rows", "columns"],
        help="対象（rows: 行, columns: 列）",
    )
    parser.add_argument("start", nargs="?", type=int, help="開始位置（1ベース）")
    parser.add_argument("end", nargs="?", type=int, help="終了位置（1ベース、省略時: startと同じ）")
    parser.add_argument("--no-inherit", action="store_true", help="挿入時に前の行/列の書式を継承しない")
    parser.add_argument("-h", "--help", action="store_true", help="ヘルプを表示")

    args = parser.parse_args()

    if args.help or not all([args.file_id, args.action, args.sheet_name, args.dimension, args.start]):
        print_usage()
        sys.exit(0 if args.help else 1)

    # end が省略された場合は start と同じ（1行/1列のみ操作）
    if args.end is None:
        args.end = args.start

    # 認証
    creds = get_auth_client()
    if not creds:
        result = {
            "success": False,
            "error": "認証に失敗しました",
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(1)

    # 行列操作を実行
    result = manage_dimension(
        creds,
        args.file_id,
        args.action,
        args.sheet_name,
        args.dimension,
        args.start,
        args.end,
        inherit_before=not args.no_inherit,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
