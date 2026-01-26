#!/usr/bin/env python3
"""
ブランチプッシュスクリプト

使用方法:
    python3 push_branch.py <branch_name>

出力:
    JSON形式で結果を出力
"""

import subprocess
import sys
import json


def push_branch(branch_name: str) -> dict:
    """ブランチをリモートにプッシュする

    Args:
        branch_name: プッシュするブランチ名

    Returns:
        dict: {"success": bool} または {"error": str, "success": false}
    """
    result = subprocess.run(
        ["git", "push", "-u", "origin", branch_name],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        return {"success": True}
    else:
        return {"error": result.stderr.strip(), "success": False}


def main():
    if len(sys.argv) != 2:
        print(json.dumps({
            "error": "ブランチ名が指定されていません。使用方法: push_branch.py <branch_name>",
            "success": False
        }, ensure_ascii=False))
        sys.exit(1)

    branch_name = sys.argv[1]

    result = push_branch(branch_name)
    print(json.dumps(result, ensure_ascii=False))

    if not result.get("success"):
        sys.exit(1)


if __name__ == "__main__":
    main()
