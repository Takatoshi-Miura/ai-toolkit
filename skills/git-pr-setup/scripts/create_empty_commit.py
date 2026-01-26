#!/usr/bin/env python3
"""
空コミット作成スクリプト

使用方法:
    python3 create_empty_commit.py <commit_prefix> <ticket_title> <ticket_number>

例:
    python3 create_empty_commit.py "撮影対応" "閉じるボタンの位置を修正" 12345

出力:
    JSON形式でコミットメッセージを出力
    {"commit_message": "撮影対応／閉じるボタンの位置を修正 refs #12345", "success": true}
"""

import subprocess
import sys
import json


def create_empty_commit(commit_prefix: str, ticket_title: str, ticket_number: str) -> dict:
    """空コミットを作成する

    Args:
        commit_prefix: コミットメッセージのprefix
        ticket_title: チケットタイトル
        ticket_number: チケット番号

    Returns:
        dict: {"commit_message": str, "success": bool} または {"error": str, "success": false}
    """
    commit_message = f"{commit_prefix}／{ticket_title} refs #{ticket_number}"

    result = subprocess.run(
        ["git", "commit", "--allow-empty", "-m", commit_message],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        return {"commit_message": commit_message, "success": True}
    else:
        return {"error": result.stderr.strip(), "success": False}


def main():
    if len(sys.argv) != 4:
        print(json.dumps({
            "error": "引数が不足しています。使用方法: create_empty_commit.py <commit_prefix> <ticket_title> <ticket_number>",
            "success": False
        }, ensure_ascii=False))
        sys.exit(1)

    commit_prefix = sys.argv[1]
    ticket_title = sys.argv[2]
    ticket_number = sys.argv[3]

    result = create_empty_commit(commit_prefix, ticket_title, ticket_number)
    print(json.dumps(result, ensure_ascii=False))

    if not result.get("success"):
        sys.exit(1)


if __name__ == "__main__":
    main()
