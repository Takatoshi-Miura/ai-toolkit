#!/usr/bin/env python3
"""LifeGraph データ読み取りスクリプト（引数なし）"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from config_parser import get_resource_config
from drive_utils import get_credentials, output_json, error_result, read_sheet_range

from googleapiclient.discovery import build


def main():
    config = get_resource_config("lifegraph")
    creds = get_credentials()
    service = build("sheets", "v4", credentials=creds)

    try:
        values = read_sheet_range(
            service,
            config["file_id"],
            config["sheet_name"],
            config["columns"]
        )
        output_json({
            "success": True,
            "resource": "lifegraph",
            "sheetName": config["sheet_name"],
            "values": values
        })
    except Exception as e:
        output_json(error_result(str(e)))
        sys.exit(1)


if __name__ == "__main__":
    main()
