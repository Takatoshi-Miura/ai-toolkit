#!/usr/bin/env python3
"""
PR作成スクリプト

使用方法:
    python3 create_pr.py <template_path> <merge_target> <ticket_url> <pr_title>

機能:
    - PRテンプレートを読み込む
    - #xxxxx をチケットURLに置換
    - gh pr create でドラフトPR作成

出力:
    JSON形式でPR URLを出力
"""

import subprocess
import sys
import json
import re
import os

# 同じディレクトリのモジュールをインポート
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)
from git_auth import check_gh_auth


def get_repo_info() -> str | None:
    """owner/repo 形式でリポジトリ情報を取得"""
    result = subprocess.run(
        ["git", "remote", "get-url", "origin"],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        return None

    url = result.stdout.strip()
    # SSH or HTTPS形式からowner/repoを抽出
    match = re.search(r'[:/]([^/]+)/([^/.]+)(\.git)?$', url)
    if match:
        return f"{match.group(1)}/{match.group(2)}"
    return None


def get_current_branch() -> str | None:
    """現在のブランチ名を取得"""
    result = subprocess.run(
        ["git", "branch", "--show-current"],
        capture_output=True,
        text=True
    )
    return result.stdout.strip() if result.returncode == 0 else None


def create_pr(template_path: str, merge_target: str, ticket_url: str, pr_title: str) -> dict:
    """PRを作成する

    Args:
        template_path: PRテンプレートのパス
        merge_target: マージ先ブランチ
        ticket_url: チケットURL（テンプレート置換用）
        pr_title: PRタイトル

    Returns:
        dict: {"pr_url": str, "success": bool} または {"error": str, "success": false}
    """
    # GitHub CLI認証確認
    auth_result = check_gh_auth()
    if not auth_result.get("authenticated"):
        return {"error": auth_result.get("message"), "success": False}

    # テンプレート読み込み
    if not os.path.exists(template_path):
        return {"error": f"テンプレートが見つかりません: {template_path}", "success": False}

    with open(template_path, "r", encoding="utf-8") as f:
        body = f.read()

    # #xxxxx をチケットURLに置換
    body = re.sub(r'#xxxxx', ticket_url, body)

    # リポジトリ情報取得
    repo = get_repo_info()
    if not repo:
        return {"error": "リポジトリ情報を取得できません", "success": False}

    # 現在のブランチ
    branch = get_current_branch()
    if not branch:
        return {"error": "現在のブランチを取得できません", "success": False}

    # gh pr create
    result = subprocess.run(
        [
            "gh", "pr", "create",
            "--repo", repo,
            "--title", pr_title,
            "--base", merge_target,
            "--head", branch,
            "--draft",
            "--body", body
        ],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        pr_url = result.stdout.strip()
        return {"pr_url": pr_url, "success": True}
    else:
        return {"error": result.stderr.strip(), "success": False}


def main():
    if len(sys.argv) != 5:
        print(json.dumps({
            "error": "引数が不足しています。使用方法: create_pr.py <template_path> <merge_target> <ticket_url> <pr_title>",
            "success": False
        }, ensure_ascii=False))
        sys.exit(1)

    template_path = sys.argv[1]
    merge_target = sys.argv[2]
    ticket_url = sys.argv[3]
    pr_title = sys.argv[4]

    result = create_pr(template_path, merge_target, ticket_url, pr_title)
    print(json.dumps(result, ensure_ascii=False))

    if not result.get("success"):
        sys.exit(1)


if __name__ == "__main__":
    main()
