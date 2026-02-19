#!/usr/bin/env python3
"""
スプレッドシートの複数操作を一括実行するCLI（バッチリクエスト）

使用方法:
    python scripts/batch_sheets.py <fileId> '<json_operations>'

例:
    python scripts/batch_sheets.py 1abc...xyz '[
      {"type": "merge", "range": "Sheet1!A1:B2"},
      {"type": "highlight", "range": "Sheet1!A1:B2", "color": "light_green"},
      {"type": "insert_dimension", "sheet": "Sheet1", "dimension": "rows", "start": 5, "end": 6}
    ]'

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
from highlight_cells import PRESET_COLORS, DEFAULT_COLOR

from googleapiclient.discovery import build


# サポートする操作タイプ
SUPPORTED_TYPES = {"merge", "highlight", "insert_dimension", "delete_dimension", "add_sheet", "duplicate_sheet"}


def build_merge_request(op: dict, sheet_id_map: dict) -> dict:
    """merge操作をbatchUpdateリクエストに変換"""
    sheet_name, cell_range = parse_range(op["range"])
    sheet_id = sheet_id_map[sheet_name]
    return {
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


def build_highlight_request(op: dict, sheet_id_map: dict) -> dict:
    """highlight操作をbatchUpdateリクエストに変換"""
    color_name = op.get("color", DEFAULT_COLOR)
    color = PRESET_COLORS[color_name]
    sheet_name, cell_range = parse_range(op["range"])
    sheet_id = sheet_id_map[sheet_name]
    return {
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


def build_insert_dimension_request(op: dict, sheet_id_map: dict) -> dict:
    """insert_dimension操作をbatchUpdateリクエストに変換"""
    sheet_id = sheet_id_map[op["sheet"]]
    start = op["start"]
    end = op.get("end", start)
    inherit = op.get("inheritFromBefore", True)
    dimension = op["dimension"].upper()
    return {
        "insertDimension": {
            "range": {
                "sheetId": sheet_id,
                "dimension": dimension,
                "startIndex": start - 1,
                "endIndex": end,
            },
            "inheritFromBefore": inherit,
        }
    }


def build_delete_dimension_request(op: dict, sheet_id_map: dict) -> dict:
    """delete_dimension操作をbatchUpdateリクエストに変換"""
    sheet_id = sheet_id_map[op["sheet"]]
    start = op["start"]
    end = op.get("end", start)
    dimension = op["dimension"].upper()
    return {
        "deleteDimension": {
            "range": {
                "sheetId": sheet_id,
                "dimension": dimension,
                "startIndex": start - 1,
                "endIndex": end,
            }
        }
    }


def build_add_sheet_request(op: dict, sheet_id_map: dict) -> dict:
    """add_sheet操作をbatchUpdateリクエストに変換"""
    return {
        "addSheet": {
            "properties": {
                "title": op["title"],
                "gridProperties": {
                    "rowCount": 1000,
                    "columnCount": 26
                }
            }
        }
    }


def build_duplicate_sheet_request(op: dict, sheet_id_map: dict) -> dict:
    """duplicate_sheet操作をbatchUpdateリクエストに変換"""
    request = {
        "duplicateSheet": {
            "sourceSheetId": op["sourceSheetId"],
            "insertSheetIndex": 0,
        }
    }
    if "newSheetName" in op:
        request["duplicateSheet"]["newSheetName"] = op["newSheetName"]
    return request


# ディスパッチテーブル
REQUEST_BUILDERS = {
    "merge": build_merge_request,
    "highlight": build_highlight_request,
    "insert_dimension": build_insert_dimension_request,
    "delete_dimension": build_delete_dimension_request,
    "add_sheet": build_add_sheet_request,
    "duplicate_sheet": build_duplicate_sheet_request,
}

# 操作タイプごとの必須フィールド
REQUIRED_FIELDS = {
    "merge": ["range"],
    "highlight": ["range"],
    "insert_dimension": ["sheet", "dimension", "start"],
    "delete_dimension": ["sheet", "dimension", "start"],
    "add_sheet": ["title"],
    "duplicate_sheet": ["sourceSheetId"],
}


def validate_operation(index: int, op: dict, sheet_id_map: dict) -> str | None:
    """操作を検証し、エラーメッセージを返す（問題なければNone）"""
    if not isinstance(op, dict):
        return "操作はオブジェクトである必要があります"

    op_type = op.get("type")
    if not op_type:
        return '"type" フィールドが必要です'
    if op_type not in SUPPORTED_TYPES:
        return f'未知の操作タイプです: {op_type}（利用可能: {", ".join(sorted(SUPPORTED_TYPES))}）'

    # 必須フィールドチェック
    for field in REQUIRED_FIELDS[op_type]:
        if field not in op:
            return f'"{field}" フィールドが必要です（type: {op_type}）'

    # タイプ固有のバリデーション
    if op_type in ("merge", "highlight"):
        try:
            sheet_name, _ = parse_range(op["range"])
            if sheet_name not in sheet_id_map:
                return f'シート "{sheet_name}" が見つかりません'
        except ValueError as e:
            return str(e)

    if op_type == "highlight":
        color_name = op.get("color", DEFAULT_COLOR)
        if color_name not in PRESET_COLORS:
            return f'未知の色名です: {color_name}（利用可能: {", ".join(PRESET_COLORS.keys())}）'

    if op_type in ("insert_dimension", "delete_dimension"):
        if op["sheet"] not in sheet_id_map:
            return f'シート "{op["sheet"]}" が見つかりません'
        if op["dimension"] not in ("rows", "columns"):
            return f'dimension は "rows" または "columns" である必要があります（入力: {op["dimension"]}）'
        start = op["start"]
        end = op.get("end", start)
        if not isinstance(start, int) or start < 1:
            return f"start は1以上の整数である必要があります（入力: {start}）"
        if not isinstance(end, int) or end < start:
            return f"end は start 以上の整数である必要があります（start: {start}, end: {end}）"

    return None


def batch_sheets(creds: Any, file_id: str, operations: list[dict]) -> dict:
    """複数操作を一括実行

    Args:
        creds: 認証クライアント
        file_id: スプレッドシートのファイルID
        operations: 操作のリスト

    Returns:
        結果を示すdict
    """
    service = build("sheets", "v4", credentials=creds)

    # 1. シート情報を取得（1回のみ）
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
            "operation": "batch_sheets",
            "error": f"スプレッドシート情報の取得に失敗しました: {e}"
        }

    sheet_id_map = {
        sheet["properties"]["title"]: sheet["properties"]["sheetId"]
        for sheet in spreadsheet_info.get("sheets", [])
    }
    available_sheets = list(sheet_id_map.keys())

    # 2. 全操作を検証
    validation_errors = []
    for i, op in enumerate(operations):
        error = validate_operation(i, op, sheet_id_map)
        if error:
            validation_errors.append({
                "index": i,
                "type": op.get("type", "unknown"),
                "error": error
            })

    if validation_errors:
        return {
            "success": False,
            "fileId": file_id,
            "fileType": "sheets",
            "operation": "batch_sheets",
            "error": "入力検証エラー",
            "validationErrors": validation_errors,
            "availableSheets": available_sheets
        }

    # 3. 操作がない場合
    if not operations:
        return {
            "success": False,
            "fileId": file_id,
            "fileType": "sheets",
            "operation": "batch_sheets",
            "error": "操作が指定されていません"
        }

    # 4. batchUpdateリクエストを構築
    requests = []
    operation_summaries = []
    for i, op in enumerate(operations):
        op_type = op["type"]
        builder = REQUEST_BUILDERS[op_type]
        requests.append(builder(op, sheet_id_map))

        summary = {"index": i, "type": op_type, "status": "included"}
        if op_type in ("merge", "highlight"):
            summary["range"] = op["range"]
        if op_type == "highlight":
            summary["color"] = op.get("color", DEFAULT_COLOR)
        if op_type in ("insert_dimension", "delete_dimension"):
            summary["sheet"] = op["sheet"]
            summary["dimension"] = op["dimension"]
            summary["start"] = op["start"]
            summary["end"] = op.get("end", op["start"])
        if op_type == "add_sheet":
            summary["title"] = op["title"]
        if op_type == "duplicate_sheet":
            summary["sourceSheetId"] = op["sourceSheetId"]
        operation_summaries.append(summary)

    # 5. 一括実行（1回のAPI呼び出し）
    try:
        service.spreadsheets().batchUpdate(
            spreadsheetId=file_id,
            body={"requests": requests}
        ).execute()

        return {
            "success": True,
            "fileId": file_id,
            "fileType": "sheets",
            "operation": "batch_sheets",
            "totalOperations": len(requests),
            "operations": operation_summaries
        }
    except Exception as e:
        return {
            "success": False,
            "fileId": file_id,
            "fileType": "sheets",
            "operation": "batch_sheets",
            "error": f"バッチ実行に失敗しました: {e}",
            "totalOperations": len(requests),
            "operations": operation_summaries
        }


def print_usage():
    """使用方法を表示"""
    print("""
使用方法:
    python scripts/batch_sheets.py <fileId> '<json_operations>'

引数:
    fileId          - スプレッドシートのファイルID
    json_operations - 操作リストのJSON配列

操作タイプ:
    merge              セル結合         {"type": "merge", "range": "Sheet1!A1:B2"}
    highlight          セルハイライト   {"type": "highlight", "range": "Sheet1!A1:B2", "color": "yellow"}
    insert_dimension   行/列挿入       {"type": "insert_dimension", "sheet": "Sheet1", "dimension": "rows", "start": 3, "end": 4}
    delete_dimension   行/列削除       {"type": "delete_dimension", "sheet": "Sheet1", "dimension": "columns", "start": 3}
    add_sheet          シート作成       {"type": "add_sheet", "title": "新規シート"}
    duplicate_sheet    シートコピー     {"type": "duplicate_sheet", "sourceSheetId": 0, "newSheetName": "コピー"}

例:
    # セル結合＋ハイライトを一括実行
    python scripts/batch_sheets.py 1abc...xyz '[
      {"type": "merge", "range": "Sheet1!A1:B2"},
      {"type": "highlight", "range": "Sheet1!A1:B2", "color": "light_green"}
    ]'

    # 行挿入＋セル結合＋ハイライトを一括実行
    python scripts/batch_sheets.py 1abc...xyz '[
      {"type": "insert_dimension", "sheet": "Sheet1", "dimension": "rows", "start": 5, "end": 6},
      {"type": "merge", "range": "Sheet1!A1:B2"},
      {"type": "highlight", "range": "Sheet1!C1:C5", "color": "light_red"}
    ]'

注意:
    - このスクリプトはスプレッドシートのみで動作します
    - 操作は指定した順序通りに実行されます
    - 値の挿入（insert_value.py）は別APIのためバッチに含められません
    - add_sheetで作成した新規シートへの同バッチ内での後続操作は不可です
""")


def main():
    """CLI エントリーポイント"""
    parser = argparse.ArgumentParser(
        description="スプレッドシートの複数操作を一括実行",
        add_help=False
    )
    parser.add_argument("file_id", nargs="?", help="スプレッドシートのファイルID")
    parser.add_argument("operations", nargs="?", help="操作リストのJSON配列")
    parser.add_argument("-h", "--help", action="store_true", help="ヘルプを表示")

    args = parser.parse_args()

    if args.help or not all([args.file_id, args.operations]):
        print_usage()
        sys.exit(0 if args.help else 1)

    # JSON パース
    try:
        operations = json.loads(args.operations)
        if not isinstance(operations, list):
            raise ValueError("配列である必要があります")
    except (json.JSONDecodeError, ValueError) as e:
        result = {
            "success": False,
            "error": f"operations は有効なJSON配列である必要があります: {e}"
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
    result = batch_sheets(creds, args.file_id, operations)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
