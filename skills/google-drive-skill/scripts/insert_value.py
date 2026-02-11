#!/usr/bin/env python3
"""
Google Drive ファイルに値を挿入するCLI

使用方法:
    # スプレッドシート: 範囲指定で値挿入
    python scripts/insert_value.py <fileId> sheets "Sheet1!A1" '[["値1","値2"]]'

    # スプレッドシート: 末尾に行追加
    python scripts/insert_value.py <fileId> sheets "Sheet1" '[["新しい行"]]' --append

    # ドキュメント: テキスト挿入（末尾）
    python scripts/insert_value.py <fileId> docs -1 "追加テキスト"

    # ドキュメント: 特定位置にテキスト挿入
    python scripts/insert_value.py <fileId> docs 100 "挿入テキスト"

    # スライド: テキストボックス追加
    python scripts/insert_value.py <fileId> presentations 0 "テキスト" --bounds '{"x":100,"y":100,"width":400,"height":100}'

認証ファイル:
    ~/.config/google-drive-skills/client_secret.json
    ~/.config/google-drive-skills/token.json
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Optional

# 同じディレクトリのauthモジュールをインポート
sys.path.insert(0, str(Path(__file__).parent))
from auth import get_auth_client

from googleapiclient.discovery import build
import re


def parse_markdown_table(text: str) -> Optional[list[list[str]]]:
    """Markdownテーブル形式のテキストをパースして2次元配列に変換

    Args:
        text: Markdownテーブル形式のテキスト

    Returns:
        2次元配列（テーブルでない場合はNone）
    """
    lines = text.strip().split('\n')
    if len(lines) < 2:
        return None

    # 最初の行がパイプで区切られているか確認
    if '|' not in lines[0]:
        return None

    rows = []
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue

        # セパレータ行（|---|---|）をスキップ
        if re.match(r'^[\s|:-]+$', line):
            continue

        # パイプで分割してセルを抽出
        cells = [cell.strip() for cell in line.split('|')]
        # 先頭と末尾の空要素を除去（| col1 | col2 | の形式対応）
        if cells and cells[0] == '':
            cells = cells[1:]
        if cells and cells[-1] == '':
            cells = cells[:-1]

        if cells:
            rows.append(cells)

    return rows if len(rows) >= 1 else None


def insert_to_sheets(
    creds: Any,
    file_id: str,
    target: str,
    values: list[list[Any]],
    append: bool = False
) -> dict:
    """スプレッドシートに値を挿入

    Args:
        creds: 認証クライアント
        file_id: スプレッドシートのファイルID
        target: 範囲指定（例: "Sheet1!A1" または "Sheet1"）
        values: 挿入する2次元配列
        append: Trueの場合、末尾に追加

    Returns:
        結果を示すdict
    """
    service = build("sheets", "v4", credentials=creds)

    try:
        if append:
            # 末尾に追加
            response = service.spreadsheets().values().append(
                spreadsheetId=file_id,
                range=target,
                valueInputOption="USER_ENTERED",
                body={"values": values}
            ).execute()
        else:
            # 指定位置に更新
            response = service.spreadsheets().values().update(
                spreadsheetId=file_id,
                range=target,
                valueInputOption="USER_ENTERED",
                body={"values": values}
            ).execute()

        return {
            "success": True,
            "fileId": file_id,
            "fileType": "sheets",
            "target": target,
            "updatedCells": response.get("updatedCells", len(values) * len(values[0]) if values and values[0] else 0),
            "updatedRange": response.get("updatedRange", target),
            "append": append
        }
    except Exception as e:
        return {
            "success": False,
            "fileId": file_id,
            "fileType": "sheets",
            "target": target,
            "error": str(e)
        }


def insert_to_docs(
    creds: Any,
    file_id: str,
    location: int,
    text: str,
    tab_id: Optional[str] = None
) -> dict:
    """ドキュメントにテキストを挿入

    Markdownテーブル形式の場合は自動的にネイティブテーブルに変換して挿入する。

    Args:
        creds: 認証クライアント
        file_id: ドキュメントのファイルID
        location: 挿入位置（-1で末尾）
        text: 挿入するテキスト（Markdownテーブル形式も可）
        tab_id: タブID（オプション）

    Returns:
        結果を示すdict
    """
    service = build("docs", "v1", credentials=creds)

    try:
        # ドキュメント情報を取得
        doc = service.documents().get(
            documentId=file_id,
            includeTabsContent=True
        ).execute()

        # 末尾に挿入する場合、ドキュメントの長さを取得
        actual_location = location
        if location == -1:
            # タブがある場合
            if doc.get("tabs") and len(doc["tabs"]) > 0:
                if tab_id:
                    # 指定されたタブを検索
                    target_tab = None
                    for tab in doc["tabs"]:
                        if tab.get("tabProperties", {}).get("tabId") == tab_id:
                            target_tab = tab
                            break
                    if target_tab and target_tab.get("documentTab", {}).get("body", {}).get("content"):
                        content = target_tab["documentTab"]["body"]["content"]
                        actual_location = max(el.get("endIndex", 1) for el in content) - 1
                    else:
                        actual_location = 1
                else:
                    # 最初のタブを使用
                    first_tab = doc["tabs"][0]
                    if first_tab.get("documentTab", {}).get("body", {}).get("content"):
                        content = first_tab["documentTab"]["body"]["content"]
                        actual_location = max(el.get("endIndex", 1) for el in content) - 1
                    else:
                        actual_location = 1
            elif doc.get("body", {}).get("content"):
                content = doc["body"]["content"]
                actual_location = max(el.get("endIndex", 1) for el in content) - 1
            else:
                actual_location = 1

        # Markdownテーブルかどうかチェック
        table_data = parse_markdown_table(text)

        if table_data:
            # ネイティブテーブルとして挿入
            return insert_native_table(service, file_id, actual_location, table_data, tab_id)
        else:
            # 通常のテキストとして挿入
            insert_request = {
                "insertText": {
                    "location": {"index": actual_location},
                    "text": text
                }
            }

            # タブIDが指定されている場合
            if tab_id:
                insert_request["insertText"]["location"]["tabId"] = tab_id

            response = service.documents().batchUpdate(
                documentId=file_id,
                body={"requests": [insert_request]}
            ).execute()

            return {
                "success": True,
                "fileId": file_id,
                "fileType": "docs",
                "location": actual_location,
                "originalLocation": location,
                "textLength": len(text),
                "tabId": tab_id,
                "insertedAs": "text"
            }
    except Exception as e:
        return {
            "success": False,
            "fileId": file_id,
            "fileType": "docs",
            "location": location,
            "error": str(e)
        }


def insert_native_table(
    service: Any,
    file_id: str,
    location: int,
    table_data: list[list[str]],
    tab_id: Optional[str] = None
) -> dict:
    """Google Docsにネイティブテーブルを挿入

    Args:
        service: Google Docs APIサービス
        file_id: ドキュメントのファイルID
        location: 挿入位置
        table_data: テーブルデータ（2次元配列）
        tab_id: タブID（オプション）

    Returns:
        結果を示すdict
    """
    rows = len(table_data)
    cols = max(len(row) for row in table_data) if table_data else 0

    if rows == 0 or cols == 0:
        return {
            "success": False,
            "fileId": file_id,
            "fileType": "docs",
            "error": "テーブルデータが空です"
        }

    # リクエストを構築（逆順で実行されるため、テーブル作成→セル入力の順）
    requests = []

    # 1. テーブルを挿入
    insert_table_request = {
        "insertTable": {
            "rows": rows,
            "columns": cols,
            "location": {"index": location}
        }
    }
    if tab_id:
        insert_table_request["insertTable"]["location"]["tabId"] = tab_id

    requests.append(insert_table_request)

    # テーブル挿入を実行
    try:
        service.documents().batchUpdate(
            documentId=file_id,
            body={"requests": requests}
        ).execute()
    except Exception as e:
        return {
            "success": False,
            "fileId": file_id,
            "fileType": "docs",
            "error": f"テーブル挿入に失敗しました: {str(e)}"
        }

    # 2. ドキュメントを再取得してテーブルのセルインデックスを取得
    doc = service.documents().get(
        documentId=file_id,
        includeTabsContent=True
    ).execute()

    # テーブル要素を見つける
    table_element = None
    if doc.get("tabs") and len(doc["tabs"]) > 0:
        first_tab = doc["tabs"][0]
        if tab_id:
            for tab in doc["tabs"]:
                if tab.get("tabProperties", {}).get("tabId") == tab_id:
                    first_tab = tab
                    break
        content = first_tab.get("documentTab", {}).get("body", {}).get("content", [])
    else:
        content = doc.get("body", {}).get("content", [])

    # location以降で最初に見つかるテーブルを取得
    for element in content:
        if element.get("startIndex", 0) >= location and "table" in element:
            table_element = element["table"]
            break

    if not table_element:
        return {
            "success": False,
            "fileId": file_id,
            "fileType": "docs",
            "error": "挿入したテーブルが見つかりません"
        }

    # 3. セルにテキストを挿入（逆順で処理）
    cell_requests = []
    for row_idx, row in enumerate(table_data):
        for col_idx, cell_text in enumerate(row):
            if col_idx >= cols:
                continue
            # テーブルセルのインデックスを取得
            try:
                table_row = table_element["tableRows"][row_idx]
                table_cell = table_row["tableCells"][col_idx]
                cell_content = table_cell["content"]
                if cell_content and len(cell_content) > 0:
                    # セル内の段落の開始位置を取得
                    cell_start_index = cell_content[0].get("startIndex", 0)
                    if cell_text:  # 空でない場合のみ挿入
                        cell_requests.append({
                            "insertText": {
                                "location": {"index": cell_start_index},
                                "text": cell_text
                            }
                        })
            except (KeyError, IndexError):
                continue

    # セルへのテキスト挿入を逆順で実行（後ろから挿入することでインデックスのずれを防ぐ）
    if cell_requests:
        cell_requests.reverse()
        try:
            service.documents().batchUpdate(
                documentId=file_id,
                body={"requests": cell_requests}
            ).execute()
        except Exception as e:
            return {
                "success": False,
                "fileId": file_id,
                "fileType": "docs",
                "error": f"セルへのテキスト挿入に失敗しました: {str(e)}"
            }

    return {
        "success": True,
        "fileId": file_id,
        "fileType": "docs",
        "location": location,
        "rows": rows,
        "columns": cols,
        "tabId": tab_id,
        "insertedAs": "native_table"
    }


def insert_to_slides(
    creds: Any,
    file_id: str,
    slide_index: int,
    text: str,
    bounds: Optional[dict] = None
) -> dict:
    """スライドにテキストボックスを追加

    Args:
        creds: 認証クライアント
        file_id: プレゼンテーションのファイルID
        slide_index: スライドのインデックス（0始まり）
        text: 挿入するテキスト
        bounds: テキストボックスの位置とサイズ {"x": 100, "y": 100, "width": 400, "height": 100}

    Returns:
        結果を示すdict
    """
    service = build("slides", "v1", credentials=creds)

    try:
        # プレゼンテーション情報を取得
        presentation = service.presentations().get(presentationId=file_id).execute()

        if not presentation.get("slides") or slide_index >= len(presentation["slides"]):
            return {
                "success": False,
                "fileId": file_id,
                "fileType": "presentations",
                "slideIndex": slide_index,
                "error": f"スライドインデックス {slide_index} は範囲外です（全 {len(presentation.get('slides', []))} スライド）"
            }

        slide_id = presentation["slides"][slide_index]["objectId"]
        text_box_id = f"textbox_{int(__import__('time').time() * 1000)}"

        # デフォルトの位置とサイズ
        default_bounds = {
            "x": bounds.get("x", 100) if bounds else 100,
            "y": bounds.get("y", 100) if bounds else 100,
            "width": bounds.get("width", 400) if bounds else 400,
            "height": bounds.get("height", 100) if bounds else 100
        }

        # テキストボックスを作成してテキストを挿入
        requests = [
            {
                "createShape": {
                    "objectId": text_box_id,
                    "shapeType": "TEXT_BOX",
                    "elementProperties": {
                        "pageObjectId": slide_id,
                        "size": {
                            "width": {"magnitude": default_bounds["width"], "unit": "PT"},
                            "height": {"magnitude": default_bounds["height"], "unit": "PT"}
                        },
                        "transform": {
                            "scaleX": 1,
                            "scaleY": 1,
                            "translateX": default_bounds["x"],
                            "translateY": default_bounds["y"],
                            "unit": "PT"
                        }
                    }
                }
            },
            {
                "insertText": {
                    "objectId": text_box_id,
                    "text": text
                }
            }
        ]

        response = service.presentations().batchUpdate(
            presentationId=file_id,
            body={"requests": requests}
        ).execute()

        return {
            "success": True,
            "fileId": file_id,
            "fileType": "presentations",
            "slideIndex": slide_index,
            "slideId": slide_id,
            "textBoxId": text_box_id,
            "bounds": default_bounds,
            "textLength": len(text)
        }
    except Exception as e:
        return {
            "success": False,
            "fileId": file_id,
            "fileType": "presentations",
            "slideIndex": slide_index,
            "error": str(e)
        }


def print_usage():
    """使用方法を表示"""
    print("""
使用方法:
    python scripts/insert_value.py <fileId> <fileType> <target> <content> [options]

引数:
    fileId    - Google DriveのファイルID
    fileType  - ファイルタイプ (docs|sheets|presentations)
    target    - 挿入位置
                sheets: 範囲（例: "Sheet1!A1"）
                docs: 文字位置（-1で末尾）
                presentations: スライドインデックス（0始まり）
    content   - 挿入内容
                sheets: JSON形式の2次元配列（例: '[["値1","値2"]]'）
                docs: テキスト
                presentations: テキスト

オプション:
    --append  - sheets: 末尾に追加
    --bounds  - presentations: テキストボックスの位置とサイズ（JSON形式）
    --tab-id  - docs: タブID

例:
    # スプレッドシート
    python scripts/insert_value.py 1abc...xyz sheets "Sheet1!A1" '[["値1","値2"]]'
    python scripts/insert_value.py 1abc...xyz sheets "Sheet1" '[["行データ"]]' --append

    # ドキュメント
    python scripts/insert_value.py 1abc...xyz docs -1 "追加テキスト"
    python scripts/insert_value.py 1abc...xyz docs 100 "挿入テキスト"

    # スライド
    python scripts/insert_value.py 1abc...xyz presentations 0 "テキスト"
    python scripts/insert_value.py 1abc...xyz presentations 0 "テキスト" --bounds '{"x":100,"y":100,"width":400,"height":100}'
""")


def main():
    """CLI エントリーポイント"""
    parser = argparse.ArgumentParser(
        description="Google Drive ファイルに値を挿入",
        add_help=False
    )
    parser.add_argument("file_id", nargs="?", help="ファイルID")
    parser.add_argument("file_type", nargs="?", choices=["docs", "sheets", "presentations"], help="ファイルタイプ")
    parser.add_argument("target", nargs="?", help="挿入位置")
    parser.add_argument("content", nargs="?", help="挿入内容")
    parser.add_argument("--append", action="store_true", help="sheets: 末尾に追加")
    parser.add_argument("--bounds", help="presentations: テキストボックスの位置とサイズ（JSON）")
    parser.add_argument("--tab-id", help="docs: タブID")
    parser.add_argument("-h", "--help", action="store_true", help="ヘルプを表示")

    args = parser.parse_args()

    if args.help or not all([args.file_id, args.file_type, args.target, args.content]):
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

    # ファイルタイプに応じて処理
    if args.file_type == "sheets":
        try:
            values = json.loads(args.content)
            if not isinstance(values, list) or not all(isinstance(row, list) for row in values):
                raise ValueError("2次元配列である必要があります")
        except json.JSONDecodeError as e:
            result = {
                "success": False,
                "error": f"content は有効なJSON配列である必要があります: {e}"
            }
            print(json.dumps(result, ensure_ascii=False, indent=2))
            sys.exit(1)

        result = insert_to_sheets(creds, args.file_id, args.target, values, args.append)

    elif args.file_type == "docs":
        try:
            location = int(args.target)
        except ValueError:
            result = {
                "success": False,
                "error": "docs の場合、target は数値（挿入位置）である必要があります（-1で末尾）"
            }
            print(json.dumps(result, ensure_ascii=False, indent=2))
            sys.exit(1)

        result = insert_to_docs(creds, args.file_id, location, args.content, args.tab_id)

    elif args.file_type == "presentations":
        try:
            slide_index = int(args.target)
        except ValueError:
            result = {
                "success": False,
                "error": "presentations の場合、target は数値（スライドインデックス）である必要があります"
            }
            print(json.dumps(result, ensure_ascii=False, indent=2))
            sys.exit(1)

        bounds = None
        if args.bounds:
            try:
                bounds = json.loads(args.bounds)
            except json.JSONDecodeError as e:
                result = {
                    "success": False,
                    "error": f"bounds は有効なJSONである必要があります: {e}"
                }
                print(json.dumps(result, ensure_ascii=False, indent=2))
                sys.exit(1)

        result = insert_to_slides(creds, args.file_id, slide_index, args.content, bounds)

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
