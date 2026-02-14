#!/usr/bin/env python3
"""
Redmine認証モジュール

設定ファイル: ~/.config/redmine-skill/config.json
"""

import json
import os
from typing import Optional


CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".config", "redmine-skill")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")


def get_config() -> Optional[dict]:
    """設定を読み込む

    Returns:
        dict: {"url": str, "api_key": str} または None
    """
    if not os.path.exists(CONFIG_PATH):
        return None

    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)

        if not config.get("url") or not config.get("api_key"):
            return None

        return config
    except (json.JSONDecodeError, IOError):
        return None


def save_config(url: str, api_key: str) -> bool:
    """設定を保存する

    Args:
        url: RedmineのベースURL
        api_key: Redmine APIキー

    Returns:
        bool: 成功時True
    """
    try:
        os.makedirs(CONFIG_DIR, exist_ok=True)

        config = {
            "url": url.rstrip("/"),
            "api_key": api_key
        }

        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        return True
    except IOError as e:
        print(f"設定保存エラー: {e}")
        return False


def is_configured() -> bool:
    """設定済みかどうかを確認

    Returns:
        bool: 設定済みならTrue
    """
    return get_config() is not None


def main():
    """メイン関数（CLIから呼び出し用）"""
    result = {
        "configured": is_configured(),
        "config_path": CONFIG_PATH
    }

    if is_configured():
        config = get_config()
        result["url"] = config.get("url")
        # APIキーは安全のため表示しない
        result["api_key_set"] = bool(config.get("api_key"))

    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
