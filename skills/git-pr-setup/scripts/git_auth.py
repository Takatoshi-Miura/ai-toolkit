#!/usr/bin/env python3
"""
Git認証ヘルパー

GitHub CLIの認証状態を確認する。
"""

import subprocess
import json


def check_gh_auth() -> dict:
    """GitHub CLI認証状態を確認

    Returns:
        dict: {"authenticated": bool, "message": str}
    """
    try:
        result = subprocess.run(
            ["gh", "auth", "status"],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            return {
                "authenticated": True,
                "message": "GitHub CLI認証済み"
            }
        else:
            return {
                "authenticated": False,
                "message": "GitHub CLI未認証。`gh auth login` を実行してください。",
                "stderr": result.stderr.strip()
            }
    except FileNotFoundError:
        return {
            "authenticated": False,
            "message": "GitHub CLI (gh) が見つかりません。`brew install gh` でインストールしてください。"
        }
    except Exception as e:
        return {
            "authenticated": False,
            "message": f"認証確認中にエラー: {str(e)}"
        }


def main():
    """メイン関数（CLIから呼び出し用）"""
    result = check_gh_auth()
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
