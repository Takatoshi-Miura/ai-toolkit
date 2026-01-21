#!/usr/bin/env python3
"""
Google Drive ファイルの要素をコピーするCLI

使用方法:
    # シートをコピー（sheetIdで指定）
    python scripts/copy_element.py <fileId> sheets <sheetId> [newName]

    # スライドをコピー（objectIdで指定）
    python scripts/copy_element.py <fileId> presentations <slideObjectId> [newName]

認証ファイル:
    ~/.config/google-drive-skills/client_secret.json
    ~/.config/google-drive-skills/token.json
"""

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any, Optional

# 同じディレクトリのauthモジュールをインポート
sys.path.insert(0, str(Path(__file__).parent))
from auth import get_auth_client

from googleapiclient.discovery import build


def copy_sheet(creds: Any, file_id: str, source_sheet_id: int, new_name: Optional[str] = None) -> dict:
    """スプレッドシートのシートをコピー

    Args:
        creds: 認証クライアント
        file_id: スプレッドシートのファイルID
        source_sheet_id: コピー元のシートID
        new_name: 新しいシート名（省略時は自動生成）

    Returns:
        結果を示すdict
    """
    service = build("sheets", "v4", credentials=creds)

    try:
        # シート名が指定されていない場合はデフォルト名
        sheet_name = new_name or f"コピー - {source_sheet_id}"

        response = service.spreadsheets().batchUpdate(
            spreadsheetId=file_id,
            body={
                "requests": [
                    {
                        "duplicateSheet": {
                            "sourceSheetId": source_sheet_id,
                            "newSheetName": sheet_name,
                            "insertSheetIndex": 0  # 先頭に挿入
                        }
                    }
                ]
            }
        ).execute()

        duplicated_sheet = response.get("replies", [{}])[0].get("duplicateSheet", {})
        sheet_properties = duplicated_sheet.get("properties", {})

        return {
            "success": True,
            "fileId": file_id,
            "fileType": "sheets",
            "operation": "copy",
            "sourceSheetId": source_sheet_id,
            "newSheetId": sheet_properties.get("sheetId"),
            "newSheetName": sheet_properties.get("title"),
            "newSheetIndex": sheet_properties.get("index")
        }
    except Exception as e:
        return {
            "success": False,
            "fileId": file_id,
            "fileType": "sheets",
            "operation": "copy",
            "sourceSheetId": source_sheet_id,
            "error": str(e)
        }


def copy_slide(creds: Any, file_id: str, source_slide_id: str, new_title: Optional[str] = None) -> dict:
    """プレゼンテーションのスライドをコピー

    Args:
        creds: 認証クライアント
        file_id: プレゼンテーションのファイルID
        source_slide_id: コピー元のスライドオブジェクトID
        new_title: 新しいスライドのタイトル（オプション）

    Returns:
        結果を示すdict
    """
    service = build("slides", "v1", credentials=creds)

    try:
        # プレゼンテーション情報を取得してスライドの存在確認
        presentation = service.presentations().get(presentationId=file_id).execute()

        if not presentation.get("slides"):
            return {
                "success": False,
                "fileId": file_id,
                "fileType": "presentations",
                "operation": "copy",
                "error": "プレゼンテーションにスライドが存在しません"
            }

        # 指定されたスライドIDを検索
        source_slide = None
        for slide in presentation["slides"]:
            if slide.get("objectId") == source_slide_id:
                source_slide = slide
                break

        if not source_slide:
            available_slides = [f"スライド{i+1}: {slide.get('objectId')}" for i, slide in enumerate(presentation["slides"])]
            return {
                "success": False,
                "fileId": file_id,
                "fileType": "presentations",
                "operation": "copy",
                "sourceSlideId": source_slide_id,
                "error": f"指定されたスライドID '{source_slide_id}' が見つかりません",
                "availableSlides": available_slides
            }

        duplicate_slide_id = f"slide_copy_{int(time.time() * 1000)}"

        # スライドを複製
        requests = [
            {
                "duplicateObject": {
                    "objectId": source_slide_id,
                    "objectIds": {
                        source_slide_id: duplicate_slide_id
                    }
                }
            }
        ]

        response = service.presentations().batchUpdate(
            presentationId=file_id,
            body={"requests": requests}
        ).execute()

        # 新しいタイトルが指定されている場合は更新
        if new_title:
            try:
                # 複製後のプレゼンテーションを取得
                updated_presentation = service.presentations().get(presentationId=file_id).execute()

                duplicated_slide = None
                for slide in updated_presentation.get("slides", []):
                    if slide.get("objectId") == duplicate_slide_id:
                        duplicated_slide = slide
                        break

                if duplicated_slide and duplicated_slide.get("pageElements"):
                    # タイトル要素を探す
                    title_element = None
                    for element in duplicated_slide["pageElements"]:
                        shape = element.get("shape", {})
                        placeholder = shape.get("placeholder", {})
                        if placeholder.get("type") in ["TITLE", "CENTERED_TITLE"]:
                            title_element = element
                            break

                    if title_element and title_element.get("objectId"):
                        # タイトルを更新
                        service.presentations().batchUpdate(
                            presentationId=file_id,
                            body={
                                "requests": [
                                    {
                                        "deleteText": {
                                            "objectId": title_element["objectId"],
                                            "textRange": {"type": "ALL"}
                                        }
                                    },
                                    {
                                        "insertText": {
                                            "objectId": title_element["objectId"],
                                            "text": new_title
                                        }
                                    }
                                ]
                            }
                        ).execute()
            except Exception:
                # タイトル更新に失敗してもスライドのコピー自体は成功
                pass

        return {
            "success": True,
            "fileId": file_id,
            "fileType": "presentations",
            "operation": "copy",
            "sourceSlideId": source_slide_id,
            "duplicatedSlideId": duplicate_slide_id,
            "newSlideTitle": new_title
        }
    except Exception as e:
        return {
            "success": False,
            "fileId": file_id,
            "fileType": "presentations",
            "operation": "copy",
            "sourceSlideId": source_slide_id,
            "error": str(e)
        }


def print_usage():
    """使用方法を表示"""
    print("""
使用方法:
    python scripts/copy_element.py <fileId> <fileType> <sourceId> [newName]

引数:
    fileId    - Google DriveのファイルID
    fileType  - ファイルタイプ (sheets|presentations)
    sourceId  - コピー元の要素ID
                sheets: シートID（数値）
                presentations: スライドオブジェクトID（文字列）
    newName   - 新しい要素の名前（オプション）

例:
    # シートをコピー
    python scripts/copy_element.py 1abc...xyz sheets 0
    python scripts/copy_element.py 1abc...xyz sheets 123456 "コピーシート"

    # スライドをコピー
    python scripts/copy_element.py 1abc...xyz presentations "g12345"
    python scripts/copy_element.py 1abc...xyz presentations "g12345" "新しいスライド"

注意:
    - シートのコピーでは、sourceId は数値のシートIDを指定します
    - スライドのコピーでは、sourceId はスライドのオブジェクトIDを指定します
    - ドキュメント (docs) の部分コピーはサポートされていません
""")


def main():
    """CLI エントリーポイント"""
    parser = argparse.ArgumentParser(
        description="Google Drive ファイルの要素をコピー",
        add_help=False
    )
    parser.add_argument("file_id", nargs="?", help="ファイルID")
    parser.add_argument("file_type", nargs="?", choices=["sheets", "presentations", "docs"], help="ファイルタイプ")
    parser.add_argument("source_id", nargs="?", help="コピー元の要素ID")
    parser.add_argument("new_name", nargs="?", help="新しい要素の名前（オプション）")
    parser.add_argument("-h", "--help", action="store_true", help="ヘルプを表示")

    args = parser.parse_args()

    if args.help or not all([args.file_id, args.file_type, args.source_id]):
        print_usage()
        sys.exit(0 if args.help else 1)

    # ドキュメントの場合はエラー
    if args.file_type == "docs":
        result = {
            "success": False,
            "fileId": args.file_id,
            "fileType": "docs",
            "operation": "copy",
            "error": "ドキュメントの部分コピー機能はサポートされていません"
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
        try:
            source_sheet_id = int(args.source_id)
        except ValueError:
            result = {
                "success": False,
                "error": "sheets の場合、sourceId は数値（シートID）である必要があります"
            }
            print(json.dumps(result, ensure_ascii=False, indent=2))
            sys.exit(1)

        result = copy_sheet(creds, args.file_id, source_sheet_id, args.new_name)

    elif args.file_type == "presentations":
        result = copy_slide(creds, args.file_id, args.source_id, args.new_name)

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
