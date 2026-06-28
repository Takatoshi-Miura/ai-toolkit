#!/usr/bin/env python3
"""
Googleドキュメント読み取りCLI（daily-notebooklm-research専用）

使用方法:
    python scripts/read_doc.py <fileId>                  - 今月タブ（YYYYMM）を自動選択して読み取る。タブがなければ本文全体を読む
    python scripts/read_doc.py <fileId> <tabTitle>        - タイトルを指定してタブを読み取る
    python scripts/read_doc.py <fileId> --list-tabs        - タブ一覧（タイトル・ID）を取得する

引数:
    fileId   - Google DriveのドキュメントID（URLの /d/{fileId}/edit 部分）
    tabTitle - 読み取りたいタブのタイトル（例: "202606"）。省略時は当月タブを自動選択
"""

import datetime
import json
import sys

from googleapiclient.discovery import build

from auth import get_auth_client


def extract_text_from_content(content: list) -> str:
    """body.contentからテキストを再帰的に抽出（paragraph + table対応）"""
    text = ""
    for element in content:
        paragraph = element.get("paragraph", {})
        if paragraph:
            for text_element in paragraph.get("elements", []):
                text_run = text_element.get("textRun", {})
                if "content" in text_run:
                    text += text_run["content"]

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


def flatten_tabs(tabs: list) -> list:
    """tabsをネスト構造（childTabs）含めて1次元のリストに展開する"""
    flat = []
    for tab in tabs:
        flat.append(tab)
        flat.extend(flatten_tabs(tab.get("childTabs", [])))
    return flat


def list_tabs(file_id: str) -> dict:
    """ドキュメント内の全タブ（タイトル・ID）を取得する"""
    creds = get_auth_client()
    if not creds:
        return {"success": False, "fileId": file_id, "error": "認証に失敗しました"}

    try:
        service = build("docs", "v1", credentials=creds)
        result = service.documents().get(documentId=file_id, includeTabsContent=True).execute()
        tabs = flatten_tabs(result.get("tabs", []))

        tab_list = [
            {"id": t.get("tabProperties", {}).get("tabId"), "title": t.get("tabProperties", {}).get("title")}
            for t in tabs
        ]

        return {
            "success": True,
            "fileId": file_id,
            "title": result.get("title", ""),
            "tabs": tab_list,
        }
    except Exception as e:
        return {"success": False, "fileId": file_id, "error": str(e)}


def read_doc_full(file_id: str, tab_title: str = None) -> dict:
    """タブ対応の読み取り関数。

    tab_titleが指定された場合はそのタブを読む。
    未指定の場合は当月タブ（YYYYMM形式）を自動選択し、見つからなければ本文全体を読む。
    """
    creds = get_auth_client()
    if not creds:
        return {"success": False, "fileId": file_id, "error": "認証に失敗しました"}

    try:
        service = build("docs", "v1", credentials=creds)
        result = service.documents().get(documentId=file_id, includeTabsContent=True).execute()
        tabs = flatten_tabs(result.get("tabs", []))

        target_title = tab_title or datetime.date.today().strftime("%Y%m")

        if tabs:
            matched_tab = next(
                (t for t in tabs if t.get("tabProperties", {}).get("title") == target_title),
                None,
            )

            if matched_tab:
                content = matched_tab.get("documentTab", {}).get("body", {}).get("content", [])
                return {
                    "success": True,
                    "fileId": file_id,
                    "title": result.get("title", ""),
                    "tabTitle": target_title,
                    "text": extract_text_from_content(content),
                }

            if tab_title:
                available = [t.get("tabProperties", {}).get("title") for t in tabs]
                return {
                    "success": False,
                    "fileId": file_id,
                    "error": f"タブ '{tab_title}' が見つかりません。利用可能なタブ: {available}",
                }

            # 当月タブの自動選択に失敗した場合は最初のタブ（デフォルトタブ）にフォールバック
            content = tabs[0].get("documentTab", {}).get("body", {}).get("content", [])
            return {
                "success": True,
                "fileId": file_id,
                "title": result.get("title", ""),
                "tabTitle": tabs[0].get("tabProperties", {}).get("title"),
                "text": extract_text_from_content(content),
            }

        # タブを持たない単一ドキュメントの場合
        content = result.get("body", {}).get("content", [])
        return {
            "success": True,
            "fileId": file_id,
            "title": result.get("title", ""),
            "text": extract_text_from_content(content),
        }
    except Exception as e:
        return {"success": False, "fileId": file_id, "error": str(e)}


def main():
    args = sys.argv[1:]
    if len(args) < 1:
        print("使用方法: python scripts/read_doc.py <fileId> [tabTitle|--list-tabs]", file=sys.stderr)
        sys.exit(1)

    file_id = args[0]

    if len(args) >= 2 and args[1] == "--list-tabs":
        result = list_tabs(file_id)
    else:
        tab_title = args[1] if len(args) >= 2 else None
        result = read_doc_full(file_id, tab_title)

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
