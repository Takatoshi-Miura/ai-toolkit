#!/usr/bin/env python3
"""
ブランチ作成スクリプト

使用方法:
    python3 create_branch.py <prefix> <ticket_number> <description>

例:
    python3 create_branch.py continuous_capture 12345 fix_close_button_position

出力:
    JSON形式でブランチ名を出力
    {"branch_name": "continuous_capture/12345/fix_close_button_position", "success": true}
"""

import subprocess
import sys
import json


def create_branch(prefix: str, ticket_number: str, description: str) -> dict:
    """ブランチを作成する

    Args:
        prefix: ブランチ名のprefix
        ticket_number: チケット番号
        description: 実装説明（英語スネークケース）

    Returns:
        dict: {"branch_name": str, "success": bool} または {"error": str, "success": false}
    """
    branch_name = f"{prefix}/{ticket_number}/{description}"

    result = subprocess.run(
        ["git", "checkout", "-b", branch_name],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        return {"branch_name": branch_name, "success": True}
    else:
        return {"error": result.stderr.strip(), "success": False}


def main():
    if len(sys.argv) != 4:
        print(json.dumps({
            "error": "引数が不足しています。使用方法: create_branch.py <prefix> <ticket_number> <description>",
            "success": False
        }, ensure_ascii=False))
        sys.exit(1)

    prefix = sys.argv[1]
    ticket_number = sys.argv[2]
    description = sys.argv[3]

    result = create_branch(prefix, ticket_number, description)
    print(json.dumps(result, ensure_ascii=False))

    if not result.get("success"):
        sys.exit(1)


if __name__ == "__main__":
    main()
