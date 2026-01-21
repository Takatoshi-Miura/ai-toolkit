#!/usr/bin/env python3
"""
Google Drive ファイルに新規要素を作成するCLI

使用方法:
    # 新規シート作成
    python scripts/create_element.py <fileId> sheets "新規シート名"

    # 新規スライド作成
    python scripts/create_element.py <fileId> presentations "スライドタイトル"

注意:
    ドキュメントへの新規タブ作成はGoogle Docs APIの制限により未サポート

認証ファイル:
    ~/.config/google-drive-skills/client_secret.json
    ~/.config/google-drive-skills/token.json
"""

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

# 同じディレクトリのauthモジュールをインポート
sys.path.insert(0, str(Path(__file__).parent))
from auth import get_auth_client

from googleapiclient.discovery import build


def create_sheet(creds: Any, file_id: str, title: str) -> dict:
    """スプレッドシートに新規シートを作成

    Args:
        creds: 認証クライアント
        file_id: スプレッドシートのファイルID
        title: 新規シートの名前

    Returns:
        結果を示すdict
    """
    service = build("sheets", "v4", credentials=creds)

    try:
        response = service.spreadsheets().batchUpdate(
            spreadsheetId=file_id,
            body={
                "requests": [
                    {
                        "addSheet": {
                            "properties": {
                                "title": title,
                                "gridProperties": {
                                    "rowCount": 1000,
                                    "columnCount": 26
                                }
                            }
                        }
                    }
                ]
            }
        ).execute()

        new_sheet = response.get("replies", [{}])[0].get("addSheet", {})
        sheet_properties = new_sheet.get("properties", {})

        return {
            "success": True,
            "fileId": file_id,
            "fileType": "sheets",
            "operation": "create",
            "sheetTitle": title,
            "sheetId": sheet_properties.get("sheetId"),
            "sheetIndex": sheet_properties.get("index")
        }
    except Exception as e:
        return {
            "success": False,
            "fileId": file_id,
            "fileType": "sheets",
            "operation": "create",
            "sheetTitle": title,
            "error": str(e)
        }


def create_slide(creds: Any, file_id: str, title: str) -> dict:
    """プレゼンテーションに新規スライドを作成

    Args:
        creds: 認証クライアント
        file_id: プレゼンテーションのファイルID
        title: 新規スライドのタイトル

    Returns:
        結果を示すdict
    """
    service = build("slides", "v1", credentials=creds)

    try:
        slide_object_id = f"slide_{int(time.time() * 1000)}"
        title_object_id = f"title_{int(time.time() * 1000)}"

        requests = [
            {
                "createSlide": {
                    "objectId": slide_object_id,
                    "slideLayoutReference": {
                        "predefinedLayout": "TITLE_AND_BODY"
                    },
                    "placeholderIdMappings": [
                        {
                            "layoutPlaceholder": {
                                "type": "TITLE"
                            },
                            "objectId": title_object_id
                        }
                    ]
                }
            }
        ]

        # タイトルが指定されている場合はテキストを挿入
        if title:
            requests.append({
                "insertText": {
                    "objectId": title_object_id,
                    "text": title
                }
            })

        response = service.presentations().batchUpdate(
            presentationId=file_id,
            body={"requests": requests}
        ).execute()

        return {
            "success": True,
            "fileId": file_id,
            "fileType": "presentations",
            "operation": "create",
            "slideTitle": title,
            "slideObjectId": slide_object_id,
            "titleObjectId": title_object_id
        }
    except Exception as e:
        return {
            "success": False,
            "fileId": file_id,
            "fileType": "presentations",
            "operation": "create",
            "slideTitle": title,
            "error": str(e)
        }


def print_usage():
    """使用方法を表示"""
    print("""
使用方法:
    python scripts/create_element.py <fileId> <fileType> <name>

引数:
    fileId    - Google DriveのファイルID
    fileType  - ファイルタイプ (sheets|presentations)
    name      - 新規要素の名前（シート名/スライドタイトル）

例:
    # 新規シート作成
    python scripts/create_element.py 1abc...xyz sheets "新規シート"

    # 新規スライド作成
    python scripts/create_element.py 1abc...xyz presentations "スライドタイトル"

注意:
    ドキュメント (docs) への新規タブ作成は Google Docs API の制限により
    サポートされていません。
""")


def main():
    """CLI エントリーポイント"""
    parser = argparse.ArgumentParser(
        description="Google Drive ファイルに新規要素を作成",
        add_help=False
    )
    parser.add_argument("file_id", nargs="?", help="ファイルID")
    parser.add_argument("file_type", nargs="?", choices=["sheets", "presentations", "docs"], help="ファイルタイプ")
    parser.add_argument("name", nargs="?", help="新規要素の名前")
    parser.add_argument("-h", "--help", action="store_true", help="ヘルプを表示")

    args = parser.parse_args()

    if args.help or not all([args.file_id, args.file_type, args.name]):
        print_usage()
        sys.exit(0 if args.help else 1)

    # ドキュメントの場合はエラー
    if args.file_type == "docs":
        result = {
            "success": False,
            "fileId": args.file_id,
            "fileType": "docs",
            "operation": "create",
            "error": "Google Docs API の制限により、ドキュメントへの新規タブ作成はサポートされていません",
            "note": "代替案として、手動でセクション見出しを追加することを検討してください"
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(1)

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
        result = create_sheet(creds, args.file_id, args.name)
    elif args.file_type == "presentations":
        result = create_slide(creds, args.file_id, args.name)

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
