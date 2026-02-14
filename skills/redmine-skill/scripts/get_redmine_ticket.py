#!/usr/bin/env python3
"""
Redmineチケット詳細取得スクリプト

使用方法:
    python3 get_redmine_ticket.py <ticket_id>

設定:
    ~/.config/redmine-skill/config.json に設定が必要

出力:
    JSON形式で結果を出力
"""

import os
import sys
import json
import ssl
import urllib.request
import urllib.error

# 同じディレクトリのモジュールをインポート
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)
from redmine_auth import get_config, is_configured


def get_ticket(ticket_id: str) -> dict:
    """Redmineチケットの詳細を取得する

    Args:
        ticket_id: チケットID

    Returns:
        dict: チケット情報 または エラー情報
    """
    if not is_configured():
        return {
            "success": False,
            "error": "Redmine設定がありません。SETUP.mdを参照してください。"
        }

    config = get_config()
    redmine_url = config.get("url")
    api_key = config.get("api_key")

    url = f"{redmine_url}/issues/{ticket_id}.json?include=journals"
    req = urllib.request.Request(
        url,
        headers={
            "Content-Type": "application/json",
            "X-Redmine-API-Key": api_key
        }
    )

    # 自己署名証明書に対応するSSLコンテキスト
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    try:
        with urllib.request.urlopen(req, context=ssl_context) as response:
            data = json.loads(response.read().decode("utf-8"))
            issue = data.get("issue", {})

            result = {
                "success": True,
                "id": issue.get("id"),
                "subject": issue.get("subject"),
                "description": issue.get("description"),
                "status": issue.get("status", {}).get("name"),
                "priority": issue.get("priority", {}).get("name"),
                "assigned_to": issue.get("assigned_to", {}).get("name"),
                "due_date": issue.get("due_date"),
                "custom_fields": issue.get("custom_fields", []),
                "journals": [
                    {
                        "id": j.get("id"),
                        "user": j.get("user", {}).get("name"),
                        "notes": j.get("notes"),
                        "created_on": j.get("created_on"),
                        "details": j.get("details", [])
                    }
                    for j in issue.get("journals", [])
                    if j.get("notes")  # ノートが空でないものだけ
                ]
            }
            return result
    except urllib.error.HTTPError as e:
        return {"success": False, "error": f"HTTP {e.code}: {e.reason}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def main():
    if len(sys.argv) != 2:
        print(json.dumps({
            "error": "引数が不足しています。使用方法: get_redmine_ticket.py <ticket_id>",
            "success": False
        }, ensure_ascii=False))
        sys.exit(1)

    ticket_id = sys.argv[1]
    result = get_ticket(ticket_id)
    print(json.dumps(result, ensure_ascii=False, indent=2))

    if not result.get("success"):
        sys.exit(1)


if __name__ == "__main__":
    main()
