#!/usr/bin/env python3
"""
Googleドキュメント読み取りCLI（daily-notebooklm-research専用）

使用方法:
    python scripts/read_doc.py <fileId>

引数:
    fileId - Google DriveのドキュメントID（URLの /d/{fileId}/edit 部分）
"""

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


def read_doc_full(file_id: str) -> dict:
    """メイン読み取り関数（タブなしの単一ドキュメントを想定）"""
    creds = get_auth_client()
    if not creds:
        return {"success": False, "fileId": file_id, "error": "認証に失敗しました"}

    try:
        service = build("docs", "v1", credentials=creds)
        result = service.documents().get(documentId=file_id).execute()
        content = result.get("body", {}).get("content", [])
        text = extract_text_from_content(content)

        return {
            "success": True,
            "fileId": file_id,
            "title": result.get("title", ""),
            "text": text,
        }
    except Exception as e:
        return {"success": False, "fileId": file_id, "error": str(e)}


def main():
    args = sys.argv[1:]
    if len(args) < 1:
        print("使用方法: python scripts/read_doc.py <fileId>", file=sys.stderr)
        sys.exit(1)

    result = read_doc_full(args[0])
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
