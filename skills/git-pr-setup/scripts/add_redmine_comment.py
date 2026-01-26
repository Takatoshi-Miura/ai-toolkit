#!/usr/bin/env python3
"""
Redmineコメント追加スクリプト

使用方法:
    python3 add_redmine_comment.py <ticket_number> <pr_url>

設定:
    ~/.config/redmine-skills/config.json に設定が必要
    設定がない場合はスキップ（エラーにならない）

出力:
    JSON形式で結果を出力
"""

import os
import sys
import json
import urllib.request
import urllib.error

# 同じディレクトリのモジュールをインポート
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)
from redmine_auth import get_config, is_configured


def add_comment(ticket_number: str, pr_url: str) -> dict:
    """Redmineチケットにコメントを追加する

    Args:
        ticket_number: チケット番号
        pr_url: PR URL

    Returns:
        dict: {"success": bool, "skipped": bool} または {"error": str, "success": false}
    """
    # 設定確認
    if not is_configured():
        return {
            "success": True,
            "skipped": True,
            "message": "Redmine設定がないためスキップしました"
        }

    config = get_config()
    redmine_url = config.get("url")
    api_key = config.get("api_key")

    # コメント内容
    comment = f"h3. PR\n\n{pr_url}"

    # Redmine API呼び出し
    url = f"{redmine_url}/issues/{ticket_number}.json"
    data = json.dumps({"issue": {"notes": comment}}).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "X-Redmine-API-Key": api_key
        },
        method="PUT"
    )

    try:
        with urllib.request.urlopen(req) as response:
            return {"success": True, "skipped": False}
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}: {e.reason}", "success": False, "skipped": False}
    except Exception as e:
        return {"error": str(e), "success": False, "skipped": False}


def main():
    if len(sys.argv) != 3:
        print(json.dumps({
            "error": "引数が不足しています。使用方法: add_redmine_comment.py <ticket_number> <pr_url>",
            "success": False
        }, ensure_ascii=False))
        sys.exit(1)

    ticket_number = sys.argv[1]
    pr_url = sys.argv[2]

    result = add_comment(ticket_number, pr_url)
    print(json.dumps(result, ensure_ascii=False))

    # skippedの場合は成功扱い
    if not result.get("success") and not result.get("skipped"):
        sys.exit(1)


if __name__ == "__main__":
    main()
