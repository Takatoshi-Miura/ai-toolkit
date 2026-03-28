#!/usr/bin/env python3
"""金銭管理データ読み取りスクリプト（引数なし、batchGetで一括取得）"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from config_parser import get_resource_config
from drive_utils import get_credentials, output_json, error_result, read_sheet_ranges_batch

from googleapiclient.discovery import build


def main():
    config = get_resource_config("money")
    creds = get_credentials()
    service = build("sheets", "v4", credentials=creds)

    try:
        sheets_config = config["sheets"]
        batch_result = read_sheet_ranges_batch(
            service, config["file_id"], sheets_config
        )

        budget_name = sheets_config[0]["name"]
        money_plan_name = sheets_config[1]["name"]

        output_json({
            "success": True,
            "resource": "money",
            "budget": {
                "sheetName": budget_name,
                "values": batch_result[budget_name]
            },
            "moneyPlan": {
                "sheetName": money_plan_name,
                "values": batch_result[money_plan_name]
            }
        })
    except Exception as e:
        output_json(error_result(str(e)))
        sys.exit(1)


if __name__ == "__main__":
    main()
