#!/usr/bin/env python3
"""
テスト項目を一括でスプレッドシートに書き込むCLI

機能:
1. 原本シートを複製
2. 因子名をヘッダーに書き込み
3. 全組み合わせ + テスト項目を一括書き込み
4. 同一内容のセルを自動結合

使用方法:
    python3 write_test_items.py <spreadsheet_id> <source_sheet_id> <sheet_name> --input-file <json_file>

入力JSON形式:
    {
        "factors": ["因子1", "因子2"],
        "items": [
            {
                "combination": ["水準1", "水準2"],
                "precondition": "・前提条件",
                "procedure": "・操作手順",
                "expected": "・期待結果"
            }
        ],
        "onepass_items": [
            {
                "label": "ワンパス項目名",
                "precondition": "・前提条件",
                "procedure": "・操作手順",
                "expected": "・期待結果"
            }
        ]
    }

認証ファイル:
    ~/.config/google-drive-skills/client_secret.json
    ~/.config/google-drive-skills/token.json
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Optional

# 同じディレクトリのモジュールをインポート
sys.path.insert(0, str(Path(__file__).parent))
from auth import get_auth_client

from googleapiclient.discovery import build


def col_to_letter(col_index: int) -> str:
    """列インデックス（0ベース）を列文字に変換

    Args:
        col_index: 列インデックス（0 = A, 1 = B, ...）

    Returns:
        列文字（A, B, ..., Z, AA, AB, ...）
    """
    result = ""
    col_index += 1  # 1ベースに変換
    while col_index > 0:
        col_index, remainder = divmod(col_index - 1, 26)
        result = chr(65 + remainder) + result
    return result


def find_merge_ranges(values: list[list[str]], col_index: int, start_row: int) -> list[tuple[int, int]]:
    """同一値が連続する範囲を検出

    Args:
        values: 2次元配列のデータ
        col_index: 対象列のインデックス
        start_row: 開始行（1ベース、ヘッダー行の次）

    Returns:
        結合範囲のリスト [(開始行, 終了行), ...]（1ベース）
    """
    if not values:
        return []

    ranges = []
    current_value = None
    current_start = None

    for i, row in enumerate(values):
        value = row[col_index] if col_index < len(row) else ""

        if value != current_value:
            # 前の範囲を確定
            if current_start is not None and i - current_start > 0:
                # 2行以上連続している場合のみ結合対象
                ranges.append((current_start + start_row, i - 1 + start_row))
            current_value = value
            current_start = i

    # 最後の範囲を確定
    if current_start is not None and len(values) - current_start > 1:
        ranges.append((current_start + start_row, len(values) - 1 + start_row))

    return ranges


def detect_column_structure(service: Any, spreadsheet_id: str, sheet_name: str) -> dict:
    """原本シートの列構造を検出する

    行1のヘッダーから「前提条件」「入力値」を含む列を探し、
    因子水準列の範囲と各列の位置を特定する。

    Args:
        service: Sheets APIサービス
        spreadsheet_id: スプレッドシートID
        sheet_name: シート名

    Returns:
        列構造情報のdict:
        - factor_start_col: 因子水準列の開始インデックス（通常1=B列）
        - factor_columns_count: 因子水準列の数
        - precondition_col: 前提条件列のインデックス
        - procedure_col: 操作手順列のインデックス
        - expected_col: 期待結果列のインデックス
    """
    # 行1（ヘッダー行）を読み取り
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=f"'{sheet_name}'!1:1"
    ).execute()

    header_row = result.get("values", [[]])[0]

    # 「前提条件」または「入力値」を含む列を検索
    precondition_col = None
    procedure_col = None
    expected_col = None

    for i, cell in enumerate(header_row):
        cell_lower = str(cell).lower()
        if precondition_col is None and ("前提条件" in cell or "入力値" in cell):
            precondition_col = i
        elif procedure_col is None and "操作" in cell:
            procedure_col = i
        elif expected_col is None and ("結果" in cell or "期待" in cell):
            expected_col = i

    # デフォルト値（検出できなかった場合）
    if precondition_col is None:
        precondition_col = 4  # E列
    if procedure_col is None:
        procedure_col = precondition_col + 1
    if expected_col is None:
        expected_col = procedure_col + 1

    # 因子水準列はB列（インデックス1）から前提条件列の手前まで
    factor_start_col = 1  # B列
    factor_columns_count = precondition_col - factor_start_col

    return {
        "factor_start_col": factor_start_col,
        "factor_columns_count": factor_columns_count,
        "precondition_col": precondition_col,
        "procedure_col": procedure_col,
        "expected_col": expected_col
    }


def write_test_items(
    creds: Any,
    spreadsheet_id: str,
    source_sheet_id: int,
    sheet_name: str,
    test_items: dict
) -> dict:
    """テスト項目を一括でスプレッドシートに書き込む

    Args:
        creds: 認証クライアント
        spreadsheet_id: スプレッドシートのファイルID
        source_sheet_id: コピー元のシートID
        sheet_name: 新しいシート名
        test_items: テスト項目データ

    Returns:
        結果を示すdict
    """
    service = build("sheets", "v4", credentials=creds)

    try:
        # 1. 原本シートを複製
        duplicate_response = service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={
                "requests": [
                    {
                        "duplicateSheet": {
                            "sourceSheetId": source_sheet_id,
                            "newSheetName": sheet_name,
                            "insertSheetIndex": 0
                        }
                    }
                ]
            }
        ).execute()

        new_sheet_id = duplicate_response["replies"][0]["duplicateSheet"]["properties"]["sheetId"]

        # 1.5. B1セルに「テスト項目 - AI Generated」を書き込み
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=f"'{sheet_name}'!B1",
            valueInputOption="USER_ENTERED",
            body={"values": [["テスト項目 - AI Generated"]]}
        ).execute()

        # 2. 複製したシートの列構造を検出
        col_structure = detect_column_structure(service, spreadsheet_id, sheet_name)
        factor_columns_count = col_structure["factor_columns_count"]
        precondition_col = col_structure["precondition_col"]
        procedure_col = col_structure["procedure_col"]
        expected_col = col_structure["expected_col"]

        # 3. データを準備
        factors = test_items.get("factors", [])
        items = test_items.get("items", [])
        onepass_items = test_items.get("onepass_items", [])

        factor_count = len(factors)
        header_row = 3  # ヘッダー行（1ベース）
        data_start_row = 4  # データ開始行（1ベース）

        # 4. 因子名をヘッダーに書き込み（B3, C3, D3, ...）
        if factors:
            factor_range = f"'{sheet_name}'!B{header_row}:{col_to_letter(1 + factor_count - 1)}{header_row}"
            service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=factor_range,
                valueInputOption="USER_ENTERED",
                body={"values": [factors]}
            ).execute()

        # 5. テスト項目データを構築（原本シートの列構造に合わせる）
        all_rows = []

        # 通常の組み合わせアイテム
        for item in items:
            combination = item.get("combination", [])
            # 原本シートの因子水準列数に合わせてパディング
            padded_combination = list(combination)
            while len(padded_combination) < factor_columns_count:
                padded_combination.append("")

            # 行データを構築（B列から期待結果列まで）
            # B列〜因子水準列: 組み合わせ（パディング済み）
            # 前提条件列: 前提条件
            # 操作手順列: 操作手順
            # 期待結果列: 期待結果
            row = padded_combination + [
                item.get("precondition", ""),
                item.get("procedure", ""),
                item.get("expected", "")
            ]
            all_rows.append(row)

        # ワンパスアイテム
        for onepass in onepass_items:
            label = onepass.get("label", "")
            # 因子列はワンパスラベルを最初の列に、残りは空（原本の列数に合わせる）
            padded_label = [label] + [""] * (factor_columns_count - 1)
            row = padded_label + [
                onepass.get("precondition", ""),
                onepass.get("procedure", ""),
                onepass.get("expected", "")
            ]
            all_rows.append(row)

        # 6. データを一括書き込み
        if all_rows:
            # 列数を計算（因子水準列 + 前提条件 + 操作手順 + 期待結果）
            total_cols = factor_columns_count + 3
            data_range = f"'{sheet_name}'!B{data_start_row}:{col_to_letter(1 + total_cols - 1)}{data_start_row + len(all_rows) - 1}"

            service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=data_range,
                valueInputOption="USER_ENTERED",
                body={"values": all_rows}
            ).execute()

        # 6. 同一内容のセルを結合
        merge_requests = []
        merged_ranges_info = []

        # 因子列ごとに結合範囲を検出
        for col_idx in range(factor_count):
            # 組み合わせデータのみを対象（ワンパスは除外）
            combination_rows = [item.get("combination", []) for item in items]
            ranges = find_merge_ranges(combination_rows, col_idx, data_start_row)

            col_letter = col_to_letter(1 + col_idx)  # B, C, D, ...
            for start_row, end_row in ranges:
                merge_requests.append({
                    "mergeCells": {
                        "range": {
                            "sheetId": new_sheet_id,
                            "startRowIndex": start_row - 1,  # 0ベース
                            "endRowIndex": end_row,  # 排他的
                            "startColumnIndex": 1 + col_idx,  # B列 = 1
                            "endColumnIndex": 2 + col_idx  # 排他的
                        },
                        "mergeType": "MERGE_ALL"
                    }
                })
                merged_ranges_info.append(f"{sheet_name}!{col_letter}{start_row}:{col_letter}{end_row}")

        # 前提条件列も結合（原本シートの列構造に従う）
        if items:
            # 前提条件列のインデックス（B列からの相対位置）
            precondition_col_rel = factor_columns_count  # B列基準での相対インデックス
            precondition_data = [[item.get("precondition", "")] for item in items]
            precondition_flat = [row[0] for row in precondition_data]
            ranges = find_merge_ranges([[v] for v in precondition_flat], 0, data_start_row)

            col_letter = col_to_letter(1 + precondition_col_rel)  # 前提条件列
            for start_row, end_row in ranges:
                merge_requests.append({
                    "mergeCells": {
                        "range": {
                            "sheetId": new_sheet_id,
                            "startRowIndex": start_row - 1,
                            "endRowIndex": end_row,
                            "startColumnIndex": 1 + precondition_col_rel,
                            "endColumnIndex": 2 + precondition_col_rel
                        },
                        "mergeType": "MERGE_ALL"
                    }
                })
                merged_ranges_info.append(f"{sheet_name}!{col_letter}{start_row}:{col_letter}{end_row}")

        # 7. 結合を実行
        if merge_requests:
            service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body={"requests": merge_requests}
            ).execute()

        return {
            "success": True,
            "spreadsheetId": spreadsheet_id,
            "newSheetId": new_sheet_id,
            "newSheetName": sheet_name,
            "factorCount": factor_count,
            "factorColumnsCount": factor_columns_count,
            "columnStructure": col_structure,
            "itemCount": len(items),
            "onepassCount": len(onepass_items),
            "totalRows": len(all_rows),
            "mergedRanges": len(merge_requests),
            "mergedRangesDetail": merged_ranges_info[:10],  # 最初の10件のみ表示
            "url": f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit#gid={new_sheet_id}"
        }

    except Exception as e:
        return {
            "success": False,
            "spreadsheetId": spreadsheet_id,
            "error": str(e)
        }


def print_usage():
    """使用方法を表示"""
    print("""
使用方法:
    python3 write_test_items.py <spreadsheet_id> <source_sheet_id> <sheet_name> --input-file <json_file>

引数:
    spreadsheet_id   - スプレッドシートのファイルID
    source_sheet_id  - コピー元のシートID（数値）
    sheet_name       - 新しいシート名
    --input-file, -f - テスト項目データのJSONファイルパス

入力JSON形式:
    {
        "factors": ["因子1", "因子2"],
        "items": [
            {
                "combination": ["水準1", "水準2"],
                "precondition": "・前提条件",
                "procedure": "・操作手順",
                "expected": "・期待結果"
            }
        ],
        "onepass_items": [
            {
                "label": "ワンパス項目名",
                "precondition": "・前提条件",
                "procedure": "・操作手順",
                "expected": "・期待結果"
            }
        ]
    }

例:
    python3 write_test_items.py 1abc...xyz 838159045 "合計金額表示" --input-file items.json
""")


def main():
    """CLI エントリーポイント"""
    parser = argparse.ArgumentParser(
        description="テスト項目を一括でスプレッドシートに書き込む",
        add_help=False
    )
    parser.add_argument("spreadsheet_id", nargs="?", help="スプレッドシートのファイルID")
    parser.add_argument("source_sheet_id", nargs="?", help="コピー元のシートID")
    parser.add_argument("sheet_name", nargs="?", help="新しいシート名")
    parser.add_argument("--input-file", "-f", help="テスト項目データのJSONファイルパス")
    parser.add_argument("-h", "--help", action="store_true", help="ヘルプを表示")

    args = parser.parse_args()

    if args.help or not all([args.spreadsheet_id, args.source_sheet_id, args.sheet_name, args.input_file]):
        print_usage()
        sys.exit(0 if args.help else 1)

    # source_sheet_id を数値に変換
    try:
        source_sheet_id = int(args.source_sheet_id)
    except ValueError:
        result = {
            "success": False,
            "error": "source_sheet_id は数値である必要があります"
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(1)

    # JSONファイル読み込み
    try:
        input_path = Path(args.input_file).expanduser()
        if not input_path.exists():
            raise FileNotFoundError(f"ファイルが見つかりません: {input_path}")
        with open(input_path, "r", encoding="utf-8") as f:
            test_items = json.load(f)
        if not isinstance(test_items, dict):
            raise ValueError("JSONオブジェクトである必要があります")
    except (json.JSONDecodeError, ValueError, FileNotFoundError) as e:
        result = {
            "success": False,
            "error": f"JSONファイル読み込みエラー: {e}"
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(1)

    # 認証
    creds = get_auth_client()
    if not creds:
        result = {
            "success": False,
            "error": "認証に失敗しました",
            "hint": "SETUP.md の手順に従って再認証してください",
            "setupCommand": "python3 ~/.claude/skills/generate-test-item-skill/scripts/auth.py --reauth"
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(1)

    # 実行
    result = write_test_items(
        creds,
        args.spreadsheet_id,
        source_sheet_id,
        args.sheet_name,
        test_items
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))

    if not result.get("success"):
        sys.exit(1)


if __name__ == "__main__":
    main()
