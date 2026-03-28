#!/usr/bin/env python3
"""
Google Drive 共通ユーティリティ

各リソース専用スクリプトから共有される関数群。
- 認証（失敗時は再認証を試行）
- テキスト抽出（Docs用）
- スプレッドシート読み取り
- JSON出力
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Optional

sys.path.insert(0, str(Path(__file__).parent))
from auth import get_auth_client, get_config_paths


def get_credentials():
    """認証情報を取得。失敗時はトークン削除して再認証を試行"""
    creds = get_auth_client()
    if creds:
        return creds

    # token.jsonが原因の可能性があるため削除して再試行
    _, token_path = get_config_paths()
    if os.path.exists(token_path):
        print("トークンを削除して再認証を試みます...")
        os.remove(token_path)
        creds = get_auth_client()
        if creds:
            return creds

    output_json(error_result("認証に失敗しました。SETUP.mdを参照してください。"))
    sys.exit(1)


def extract_text_from_content(content: list) -> str:
    """Docsのbody.contentからテキストを再帰的に抽出（paragraph + table対応）"""
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


def read_all_doc_tabs(service: Any, file_id: str) -> list[dict]:
    """ドキュメントの全タブを1回のAPI呼び出しで取得し、タブ情報のリストを返す

    Returns:
        [{"tabId": "...", "title": "...", "text": "..."}, ...]
    """
    result = service.documents().get(
        documentId=file_id,
        includeTabsContent=True
    ).execute()

    tabs = []

    def process_tabs(tab_list: list):
        for tab in tab_list:
            tab_props = tab.get("tabProperties", {})
            doc_tab = tab.get("documentTab", {})
            body = doc_tab.get("body", {})
            content = body.get("content", [])
            text = extract_text_from_content(content)

            tabs.append({
                "tabId": tab_props.get("tabId", ""),
                "title": tab_props.get("title", "無題のタブ"),
                "text": text
            })

            child_tabs = tab.get("childTabs", [])
            if child_tabs:
                process_tabs(child_tabs)

    process_tabs(result.get("tabs", []))
    return tabs


def find_tab_by_name(tabs: list[dict], tab_name: str) -> Optional[dict]:
    """タブリストから名前で検索（完全一致のみ）"""
    for tab in tabs:
        if tab["title"] == tab_name:
            return tab
    return None


def read_sheet_range(service: Any, file_id: str, sheet_name: str, columns: str) -> list:
    """スプレッドシートの指定列範囲を読み取り

    Args:
        columns: 列範囲（例: "A:P", "A:AN"）
    """
    range_str = f"{sheet_name}!{columns}"
    response = service.spreadsheets().values().get(
        spreadsheetId=file_id,
        range=range_str
    ).execute()
    return response.get("values", [])


def read_sheet_ranges_batch(
    service: Any,
    file_id: str,
    sheets: list[dict]
) -> dict[str, list]:
    """複数シートをbatchGetで一括読み取り

    Args:
        sheets: [{"name": "シート名", "columns": "A:G"}, ...]

    Returns:
        {"シート名": [[...], ...], ...}
    """
    ranges = [f"{s['name']}!{s['columns']}" for s in sheets]
    response = service.spreadsheets().values().batchGet(
        spreadsheetId=file_id,
        ranges=ranges
    ).execute()

    result = {}
    for i, value_range in enumerate(response.get("valueRanges", [])):
        result[sheets[i]["name"]] = value_range.get("values", [])
    return result


def output_json(data: dict):
    """JSONを標準出力に整形出力"""
    print(json.dumps(data, ensure_ascii=False, indent=2))


def error_result(message: str) -> dict:
    """エラーレスポンスを生成"""
    return {"success": False, "error": message}
