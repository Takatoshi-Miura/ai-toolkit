#!/usr/bin/env python3
"""
Google Drive ファイル読み取りCLI

使用方法:
    # 単一ファイル読み取り
    python scripts/read_drive_file.py <fileId> <fileType> [partName]

    # 複数ファイル一括読み取り
    python scripts/read_drive_file.py --batch '<json>'

認証ファイル:
    ~/.config/google-drive-skills/client_secret.json
    ~/.config/google-drive-skills/token.json

引数:
    fileId   - Google DriveのファイルID
    fileType - ファイルタイプ (docs|sheets|presentations)
    partName - (オプション) 読み取る部分の名前 (シート名、タブ名、ページ番号)

例:
    python scripts/read_drive_file.py 1abc...xyz sheets          # 全体読み取り
    python scripts/read_drive_file.py 1abc...xyz sheets "売上"    # シート指定
    python scripts/read_drive_file.py 1abc...xyz sheets "因子・水準,原本"  # 複数シート一括
    python scripts/read_drive_file.py 1abc...xyz docs "概要"      # タブ指定
    python scripts/read_drive_file.py 1abc...xyz presentations 3  # ページ指定

    # 複数ファイル一括（認証1回、APIコール最適化）
    python scripts/read_drive_file.py --batch '[
      {"id": "xxx", "type": "docs", "label": "テストガイドライン"},
      {"id": "yyy", "type": "sheets", "parts": "因子・水準,原本", "label": "テスト項目書"}
    ]'
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Optional

# 同じディレクトリのauthモジュールをインポート
sys.path.insert(0, str(Path(__file__).parent))
from auth import get_auth_client

from googleapiclient.discovery import build


def get_sheet_list(service: Any, file_id: str) -> list[dict]:
    """スプレッドシートのシート一覧を取得"""
    result = service.spreadsheets().get(
        spreadsheetId=file_id,
        fields="sheets.properties"
    ).execute()

    sheets = []
    for sheet in result.get("sheets", []):
        props = sheet.get("properties", {})
        sheets.append({
            "title": props.get("title", ""),
            "sheetId": props.get("sheetId", 0)
        })
    return sheets


def get_doc_tabs(service: Any, file_id: str) -> list[dict]:
    """ドキュメントのタブ一覧を取得"""
    result = service.documents().get(
        documentId=file_id,
        includeTabsContent=True
    ).execute()

    tabs = []

    def extract_tabs(tab_list: list, level: int = 0):
        for tab in tab_list:
            tab_props = tab.get("tabProperties", {})
            if tab_props:
                tabs.append({
                    "tabId": tab_props.get("tabId", ""),
                    "title": tab_props.get("title", "無題のタブ"),
                    "level": level
                })
            child_tabs = tab.get("childTabs", [])
            if child_tabs:
                extract_tabs(child_tabs, level + 1)

    if "tabs" in result:
        extract_tabs(result["tabs"])

    return tabs


def read_sheet_full(service: Any, file_id: str) -> dict[str, list]:
    """スプレッドシートの全体を読み取り"""
    sheet_list = get_sheet_list(service, file_id)
    result = {}

    for sheet in sheet_list:
        try:
            response = service.spreadsheets().values().get(
                spreadsheetId=file_id,
                range=f"{sheet['title']}!A1:ZZ10000"
            ).execute()
            result[sheet["title"]] = response.get("values", [])
        except Exception:
            result[sheet["title"]] = []

    return result


def find_sheet_by_name(sheet_list: list[dict], sheet_name: str) -> Optional[dict]:
    """シート名で検索（完全一致 → 部分一致）"""
    # 完全一致で検索
    for s in sheet_list:
        if s["title"] == sheet_name:
            return s

    # 部分一致で検索
    for s in sheet_list:
        if sheet_name in s["title"]:
            return s

    return None


def read_sheet_by_name(service: Any, file_id: str, sheet_name: str) -> dict:
    """スプレッドシートの特定シートを読み取り"""
    sheet_list = get_sheet_list(service, file_id)

    target_sheet = find_sheet_by_name(sheet_list, sheet_name)

    if not target_sheet:
        return {
            "error": f'シート "{sheet_name}" が見つかりません',
            "availableSheets": [s["title"] for s in sheet_list]
        }

    response = service.spreadsheets().values().get(
        spreadsheetId=file_id,
        range=f"{target_sheet['title']}!A1:ZZ10000"
    ).execute()

    return {
        "sheetName": target_sheet["title"],
        "sheetId": target_sheet["sheetId"],
        "values": response.get("values", [])
    }


def read_sheets_by_names(service: Any, file_id: str, sheet_names: list[str]) -> dict:
    """スプレッドシートの複数シートを一括読み取り（batchGetで効率化）"""
    sheet_list = get_sheet_list(service, file_id)

    # 各シート名を解決
    targets = []
    not_found = []
    for name in sheet_names:
        found = find_sheet_by_name(sheet_list, name)
        if found:
            targets.append(found)
        else:
            not_found.append(name)

    if not_found:
        return {
            "error": f'シートが見つかりません: {", ".join(not_found)}',
            "availableSheets": [s["title"] for s in sheet_list]
        }

    # batchGet で一括取得
    ranges = [f"'{t['title']}'!A1:ZZ10000" for t in targets]
    response = service.spreadsheets().values().batchGet(
        spreadsheetId=file_id,
        ranges=ranges
    ).execute()

    value_ranges = response.get("valueRanges", [])

    result = {}
    for target, vr in zip(targets, value_ranges):
        result[target["title"]] = {
            "sheetId": target["sheetId"],
            "values": vr.get("values", [])
        }

    return result


def extract_text_from_content(content: list) -> str:
    """body.contentからテキストを再帰的に抽出（paragraph + table対応）"""
    text = ""
    for element in content:
        # paragraph要素
        paragraph = element.get("paragraph", {})
        if paragraph:
            for text_element in paragraph.get("elements", []):
                text_run = text_element.get("textRun", {})
                if "content" in text_run:
                    text += text_run["content"]

        # table要素
        table = element.get("table", {})
        if table:
            for row in table.get("tableRows", []):
                row_texts = []
                for cell in row.get("tableCells", []):
                    cell_content = cell.get("content", [])
                    cell_text = extract_text_from_content(cell_content).strip()
                    row_texts.append(cell_text)
                text += " | ".join(row_texts) + "\n"

    return text


def read_doc_tab(service: Any, file_id: str, tab_id: str) -> str:
    """ドキュメントの特定タブを読み取り"""
    result = service.documents().get(
        documentId=file_id,
        includeTabsContent=True
    ).execute()

    def find_tab(tabs: list) -> Optional[dict]:
        for tab in tabs:
            if tab.get("tabProperties", {}).get("tabId") == tab_id:
                return tab
            child_tabs = tab.get("childTabs", [])
            if child_tabs:
                found = find_tab(child_tabs)
                if found:
                    return found
        return None

    target_tab = find_tab(result.get("tabs", []))

    if not target_tab:
        return "タブの内容が見つかりません"

    doc_tab = target_tab.get("documentTab", {})
    body = doc_tab.get("body", {})
    content = body.get("content", [])

    return extract_text_from_content(content)


def read_doc_full(service: Any, file_id: str) -> list[dict]:
    """ドキュメントの全体を読み取り"""
    tabs = get_doc_tabs(service, file_id)
    result = []

    for tab in tabs:
        text = read_doc_tab(service, file_id, tab["tabId"])
        result.append({
            "tabId": tab["tabId"],
            "title": tab["title"],
            "text": text
        })

    return result


def read_doc_by_tab_name(service: Any, file_id: str, tab_name: str) -> dict:
    """ドキュメントのタブ名で検索して読み取り"""
    tabs = get_doc_tabs(service, file_id)

    # 完全一致 → 部分一致で検索
    target_tab = None
    for t in tabs:
        if t["title"] == tab_name:
            target_tab = t
            break

    if not target_tab:
        for t in tabs:
            if tab_name in t["title"]:
                target_tab = t
                break

    if not target_tab:
        return {
            "error": f'タブ "{tab_name}" が見つかりません',
            "availableTabs": [t["title"] for t in tabs]
        }

    text = read_doc_tab(service, file_id, target_tab["tabId"])

    return {
        "tabId": target_tab["tabId"],
        "title": target_tab["title"],
        "text": text
    }


def read_slides_full(service: Any, file_id: str) -> list[dict]:
    """スライドの全体を読み取り"""
    result = service.presentations().get(presentationId=file_id).execute()
    slides = result.get("slides", [])

    output = []
    for i, slide in enumerate(slides):
        text = ""
        for element in slide.get("pageElements", []):
            shape = element.get("shape", {})
            text_content = shape.get("text", {})
            text_elements = text_content.get("textElements", [])
            for text_element in text_elements:
                text_run = text_element.get("textRun", {})
                if "content" in text_run:
                    text += text_run["content"]

        output.append({
            "pageNumber": i + 1,
            "objectId": slide.get("objectId"),
            "text": text.strip()
        })

    return output


def read_slide_by_page(service: Any, file_id: str, page_number: int) -> dict:
    """スライドの特定ページを読み取り"""
    result = service.presentations().get(presentationId=file_id).execute()
    slides = result.get("slides", [])

    if page_number < 1 or page_number > len(slides):
        return {
            "error": f"ページ {page_number} は存在しません",
            "totalPages": len(slides)
        }

    slide = slides[page_number - 1]
    text = ""
    for element in slide.get("pageElements", []):
        shape = element.get("shape", {})
        text_content = shape.get("text", {})
        text_elements = text_content.get("textElements", [])
        for text_element in text_elements:
            text_run = text_element.get("textRun", {})
            if "content" in text_run:
                text += text_run["content"]

    return {
        "pageNumber": page_number,
        "objectId": slide.get("objectId"),
        "text": text.strip()
    }


def get_file_structure(creds, file_id: str, file_type: str) -> dict:
    """ファイル構造を取得"""
    if file_type == "sheets":
        service = build("sheets", "v4", credentials=creds)
        return {"sheets": get_sheet_list(service, file_id)}
    elif file_type == "docs":
        service = build("docs", "v1", credentials=creds)
        return {"tabs": get_doc_tabs(service, file_id)}
    elif file_type == "presentations":
        service = build("slides", "v1", credentials=creds)
        result = service.presentations().get(presentationId=file_id).execute()
        return {
            "totalPages": len(result.get("slides", [])),
            "title": result.get("title")
        }
    else:
        return {"error": "サポートされていないファイルタイプ"}


def read_drive_file(file_id: str, file_type: str, part_name: Optional[str] = None) -> dict:
    """メイン読み取り関数"""
    creds = get_auth_client()
    if not creds:
        return {
            "success": False,
            "fileId": file_id,
            "fileType": file_type,
            "error": "認証に失敗しました",
            "hint": "SETUP.md の手順に従って再認証してください",
            "setupCommand": "python3 ~/.claude/skills/generate-test-item-skill/scripts/auth.py --reauth"
        }

    try:
        # 構造を取得
        structure = get_file_structure(creds, file_id, file_type)

        # コンテンツを読み取り
        if file_type == "sheets":
            service = build("sheets", "v4", credentials=creds)
            if part_name:
                # カンマ区切りで複数シート指定に対応
                sheet_names = [n.strip() for n in part_name.split(",")]
                if len(sheet_names) > 1:
                    content = read_sheets_by_names(service, file_id, sheet_names)
                else:
                    content = read_sheet_by_name(service, file_id, sheet_names[0])
            else:
                content = read_sheet_full(service, file_id)

        elif file_type == "docs":
            service = build("docs", "v1", credentials=creds)
            if part_name:
                content = read_doc_by_tab_name(service, file_id, part_name)
            else:
                content = read_doc_full(service, file_id)

        elif file_type == "presentations":
            service = build("slides", "v1", credentials=creds)
            if part_name:
                try:
                    page_num = int(part_name)
                    content = read_slide_by_page(service, file_id, page_num)
                except ValueError:
                    content = {"error": "スライドにはページ番号を指定してください"}
            else:
                content = read_slides_full(service, file_id)

        else:
            return {
                "success": False,
                "fileId": file_id,
                "fileType": file_type,
                "error": "サポートされていないファイルタイプ"
            }

        result = {
            "success": True,
            "fileId": file_id,
            "fileType": file_type,
            "structure": structure,
            "content": content
        }
        if part_name:
            result["partName"] = part_name

        return result

    except Exception as e:
        return {
            "success": False,
            "fileId": file_id,
            "fileType": file_type,
            "partName": part_name,
            "error": str(e)
        }


def read_drive_file_with_creds(creds, file_id: str, file_type: str, part_name: Optional[str] = None) -> dict:
    """認証情報を受け取って読み取り（内部用）"""
    try:
        # 構造を取得
        structure = get_file_structure(creds, file_id, file_type)

        # コンテンツを読み取り
        if file_type == "sheets":
            service = build("sheets", "v4", credentials=creds)
            if part_name:
                sheet_names = [n.strip() for n in part_name.split(",")]
                if len(sheet_names) > 1:
                    content = read_sheets_by_names(service, file_id, sheet_names)
                else:
                    content = read_sheet_by_name(service, file_id, sheet_names[0])
            else:
                content = read_sheet_full(service, file_id)

        elif file_type == "docs":
            service = build("docs", "v1", credentials=creds)
            if part_name:
                content = read_doc_by_tab_name(service, file_id, part_name)
            else:
                content = read_doc_full(service, file_id)

        elif file_type == "presentations":
            service = build("slides", "v1", credentials=creds)
            if part_name:
                try:
                    page_num = int(part_name)
                    content = read_slide_by_page(service, file_id, page_num)
                except ValueError:
                    content = {"error": "スライドにはページ番号を指定してください"}
            else:
                content = read_slides_full(service, file_id)

        else:
            return {
                "success": False,
                "fileId": file_id,
                "fileType": file_type,
                "error": "サポートされていないファイルタイプ"
            }

        result = {
            "success": True,
            "fileId": file_id,
            "fileType": file_type,
            "structure": structure,
            "content": content
        }
        if part_name:
            result["partName"] = part_name

        return result

    except Exception as e:
        return {
            "success": False,
            "fileId": file_id,
            "fileType": file_type,
            "partName": part_name,
            "error": str(e)
        }


def read_batch(batch_config: list[dict]) -> dict:
    """
    複数ファイルを一括読み取り

    Args:
        batch_config: [{"id": "xxx", "type": "docs", "parts": "...", "label": "..."}]

    Returns:
        {"success": True, "files": {"label": {...}, ...}}
    """
    creds = get_auth_client()
    if not creds:
        return {
            "success": False,
            "error": "認証に失敗しました",
            "hint": "SETUP.md の手順に従って再認証してください",
            "setupCommand": "python3 ~/.claude/skills/generate-test-item-skill/scripts/auth.py --reauth"
        }

    results = {}
    errors = []

    for item in batch_config:
        file_id = item.get("id")
        file_type = item.get("type")
        parts = item.get("parts")
        label = item.get("label", file_id)

        if not file_id or not file_type:
            errors.append({"label": label, "error": "id と type は必須です"})
            continue

        result = read_drive_file_with_creds(creds, file_id, file_type, parts)

        if result.get("success"):
            results[label] = result
        else:
            errors.append({"label": label, "error": result.get("error")})

    return {
        "success": len(errors) == 0,
        "files": results,
        "errors": errors if errors else None,
        "summary": {
            "total": len(batch_config),
            "success": len(results),
            "failed": len(errors)
        }
    }


def print_usage():
    """使用方法を表示"""
    print("""
使用方法:
    python scripts/read_drive_file.py <fileId> <fileType> [partName]
    python scripts/read_drive_file.py --batch '<json>'

引数:
    fileId   - Google DriveのファイルID
    fileType - ファイルタイプ (docs|sheets|presentations)
    partName - (オプション) 読み取る部分の名前

例:
    # 単一ファイル
    python scripts/read_drive_file.py 1abc...xyz sheets          # 全体読み取り
    python scripts/read_drive_file.py 1abc...xyz sheets "売上"    # シート指定
    python scripts/read_drive_file.py 1abc...xyz sheets "因子・水準,原本"  # 複数シート一括
    python scripts/read_drive_file.py 1abc...xyz docs "概要"      # タブ指定
    python scripts/read_drive_file.py 1abc...xyz presentations 3  # ページ指定

    # 複数ファイル一括
    python scripts/read_drive_file.py --batch '[
      {"id": "xxx", "type": "docs", "label": "テストガイドライン"},
      {"id": "yyy", "type": "sheets", "parts": "因子・水準,原本", "label": "テスト項目書"}
    ]'
""")


def main():
    """CLI エントリーポイント"""
    args = sys.argv[1:]

    if len(args) < 1:
        print_usage()
        sys.exit(1)

    # --batch モード（常にファイル出力）
    if args[0] == "--batch":
        if len(args) < 2:
            print("--batch にはJSON設定が必要です", file=sys.stderr)
            sys.exit(1)

        try:
            batch_config = json.loads(args[1])
        except json.JSONDecodeError as e:
            print(f"JSONパースエラー: {e}", file=sys.stderr)
            sys.exit(1)

        result = read_batch(batch_config)

        # 常にファイル出力（大きなデータ対応）
        output_path = "/tmp/drive_batch_result.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        # ファイルパスとサマリーのみ出力
        print(json.dumps({
            "output_file": output_path,
            "summary": result.get("summary", {}),
            "success": result.get("success", False),
            "errors": result.get("errors"),
            "hint": f"Readツールで {output_path} を読み込んでください"
        }, ensure_ascii=False, indent=2))
        return

    # 通常モード
    if len(args) < 2:
        print_usage()
        sys.exit(1)

    file_id = args[0]
    file_type = args[1]
    part_name = args[2] if len(args) > 2 else None

    if file_type not in ["docs", "sheets", "presentations"]:
        print("fileType は docs, sheets, presentations のいずれかを指定してください", file=sys.stderr)
        sys.exit(1)

    result = read_drive_file(file_id, file_type, part_name)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
