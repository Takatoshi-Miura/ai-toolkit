#!/usr/bin/env python3
"""
Google Drive ファイル読み取りCLI

環境変数で認証ファイルパスを指定可能。配布対応。

使用方法:
    python scripts/read_drive_file.py <fileId> <fileType> [partName]

環境変数:
    GOOGLE_DRIVE_CONFIG_DIR  - 認証ファイルのディレクトリ（デフォルト: ~/.config/read-google-drive/）
    GOOGLE_CREDENTIALS_PATH  - client_secret.jsonのパス
    GOOGLE_TOKEN_PATH        - token.jsonのパス

引数:
    fileId   - Google DriveのファイルID
    fileType - ファイルタイプ (docs|sheets|presentations)
    partName - (オプション) 読み取る部分の名前 (シート名、タブ名、ページ番号)

例:
    python scripts/read_drive_file.py 1abc...xyz sheets          # 全体読み取り
    python scripts/read_drive_file.py 1abc...xyz sheets "売上"    # シート指定
    python scripts/read_drive_file.py 1abc...xyz docs "概要"      # タブ指定
    python scripts/read_drive_file.py 1abc...xyz presentations 3  # ページ指定
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Optional

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build


# パス設定（環境変数対応）
def get_config_paths() -> tuple[str, str]:
    """認証ファイルのパスを取得"""
    config_dir = os.environ.get(
        "GOOGLE_DRIVE_CONFIG_DIR",
        os.path.join(os.path.expanduser("~"), ".config", "read-google-drive")
    )

    credentials_path = os.environ.get(
        "GOOGLE_CREDENTIALS_PATH",
        os.path.join(config_dir, "client_secret.json")
    )

    token_path = os.environ.get(
        "GOOGLE_TOKEN_PATH",
        os.path.join(config_dir, "token.json")
    )

    return credentials_path, token_path


def get_auth_client() -> Optional[Credentials]:
    """認証クライアントを取得"""
    credentials_path, token_path = get_config_paths()

    if not os.path.exists(credentials_path):
        print(f"認証情報ファイルが見つかりません: {credentials_path}", file=sys.stderr)
        print("\n以下のいずれかの方法で認証ファイルを設定してください：", file=sys.stderr)
        print("  1. GOOGLE_CREDENTIALS_PATH環境変数でclient_secret.jsonのパスを指定", file=sys.stderr)
        print(f"  2. {os.path.dirname(credentials_path)}/client_secret.json にファイルを配置", file=sys.stderr)
        return None

    if not os.path.exists(token_path):
        print(f"トークンファイルが見つかりません: {token_path}", file=sys.stderr)
        print("\n以下のいずれかの方法でトークンファイルを設定してください：", file=sys.stderr)
        print("  1. GOOGLE_TOKEN_PATH環境変数でtoken.jsonのパスを指定", file=sys.stderr)
        print(f"  2. {os.path.dirname(token_path)}/token.json にファイルを配置", file=sys.stderr)
        return None

    try:
        with open(token_path, "r") as f:
            token_data = json.load(f)

        creds = Credentials(
            token=token_data.get("access_token"),
            refresh_token=token_data.get("refresh_token"),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=token_data.get("client_id"),
            client_secret=token_data.get("client_secret"),
        )

        # client_id/client_secretがtoken.jsonにない場合、credentials.jsonから取得
        if not creds.client_id or not creds.client_secret:
            with open(credentials_path, "r") as f:
                cred_data = json.load(f)
            installed = cred_data.get("installed") or cred_data.get("web", {})
            creds = Credentials(
                token=token_data.get("access_token"),
                refresh_token=token_data.get("refresh_token"),
                token_uri="https://oauth2.googleapis.com/token",
                client_id=installed.get("client_id"),
                client_secret=installed.get("client_secret"),
            )

        # トークンの有効期限チェックとリフレッシュ
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            # 更新されたトークンを保存
            new_token_data = {
                "access_token": creds.token,
                "refresh_token": creds.refresh_token,
                "token_uri": creds.token_uri,
                "client_id": creds.client_id,
                "client_secret": creds.client_secret,
            }
            with open(token_path, "w") as f:
                json.dump(new_token_data, f)

        return creds
    except Exception as e:
        print(f"認証エラー: {e}", file=sys.stderr)
        return None


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


def read_sheet_by_name(service: Any, file_id: str, sheet_name: str) -> dict:
    """スプレッドシートの特定シートを読み取り"""
    sheet_list = get_sheet_list(service, file_id)

    # 完全一致 → 部分一致で検索
    target_sheet = None
    for s in sheet_list:
        if s["title"] == sheet_name:
            target_sheet = s
            break

    if not target_sheet:
        for s in sheet_list:
            if sheet_name in s["title"]:
                target_sheet = s
                break

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
        "values": response.get("values", [])
    }


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

    text = ""
    for element in content:
        paragraph = element.get("paragraph", {})
        elements = paragraph.get("elements", [])
        for text_element in elements:
            text_run = text_element.get("textRun", {})
            if "content" in text_run:
                text += text_run["content"]

    return text


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


def get_file_structure(creds: Credentials, file_id: str, file_type: str) -> dict:
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
            "error": "認証に失敗しました"
        }

    try:
        # 構造を取得
        structure = get_file_structure(creds, file_id, file_type)

        # コンテンツを読み取り
        if file_type == "sheets":
            service = build("sheets", "v4", credentials=creds)
            if part_name:
                content = read_sheet_by_name(service, file_id, part_name)
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


def print_usage():
    """使用方法を表示"""
    print("""
使用方法:
    python scripts/read_drive_file.py <fileId> <fileType> [partName]

環境変数:
    GOOGLE_DRIVE_CONFIG_DIR  - 認証ファイルのディレクトリ
                               (デフォルト: ~/.config/read-google-drive/)
    GOOGLE_CREDENTIALS_PATH  - client_secret.jsonのパス
    GOOGLE_TOKEN_PATH        - token.jsonのパス

引数:
    fileId   - Google DriveのファイルID
    fileType - ファイルタイプ (docs|sheets|presentations)
    partName - (オプション) 読み取る部分の名前

例:
    python scripts/read_drive_file.py 1abc...xyz sheets          # 全体読み取り
    python scripts/read_drive_file.py 1abc...xyz sheets "売上"    # シート指定
    python scripts/read_drive_file.py 1abc...xyz docs "概要"      # タブ指定
    python scripts/read_drive_file.py 1abc...xyz presentations 3  # ページ指定
""")


def main():
    """CLI エントリーポイント"""
    args = sys.argv[1:]

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
