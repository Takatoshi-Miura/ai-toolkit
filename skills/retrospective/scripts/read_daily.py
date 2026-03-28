#!/usr/bin/env python3
"""日次記録データ読み取りスクリプト（引数なし、月タブはCONFIG.mdから取得）"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from config_parser import get_resource_config
from drive_utils import (
    get_credentials, output_json, error_result,
    read_all_doc_tabs, find_tab_by_name
)

from googleapiclient.discovery import build


def main():
    config = get_resource_config("daily")
    goals_tab_name = config["goals_tab"]
    month_tab_name = config["month_tab"]

    creds = get_credentials()
    service = build("docs", "v1", credentials=creds)

    try:
        all_tabs = read_all_doc_tabs(service, config["file_id"])

        goals_tab = find_tab_by_name(all_tabs, goals_tab_name)
        if not goals_tab:
            available = [t["title"] for t in all_tabs]
            output_json(error_result(
                f'タブ "{goals_tab_name}" が見つかりません。利用可能: {available}'
            ))
            sys.exit(1)

        month_tab = find_tab_by_name(all_tabs, month_tab_name)
        if not month_tab:
            available = [t["title"] for t in all_tabs]
            output_json(error_result(
                f'タブ "{month_tab_name}" が見つかりません。'
                f"CONFIG.mdのmonth_tabを確認してください。利用可能: {available}"
            ))
            sys.exit(1)

        output_json({
            "success": True,
            "resource": "daily",
            "goalsTab": {
                "title": goals_tab["title"],
                "text": goals_tab["text"]
            },
            "monthTab": {
                "title": month_tab["title"],
                "text": month_tab["text"]
            }
        })
    except Exception as e:
        output_json(error_result(str(e)))
        sys.exit(1)


if __name__ == "__main__":
    main()
