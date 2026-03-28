#!/usr/bin/env python3
"""サマリー（パーソナルコンテキスト）読み取りスクリプト（引数なし）"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from config_parser import get_resource_config
from drive_utils import get_credentials, output_json, error_result, read_all_doc_tabs

from googleapiclient.discovery import build


def main():
    config = get_resource_config("summary")
    creds = get_credentials()
    service = build("docs", "v1", credentials=creds)

    try:
        all_tabs = read_all_doc_tabs(service, config["file_id"])
        output_json({
            "success": True,
            "resource": "summary",
            "tabs": [
                {"title": tab["title"], "text": tab["text"]}
                for tab in all_tabs
            ]
        })
    except Exception as e:
        output_json(error_result(str(e)))
        sys.exit(1)


if __name__ == "__main__":
    main()
