#!/usr/bin/env python3
"""
Google Driveファイルの更新確認スクリプト

TARGET_FILES.mdから監視対象URLを読み込み、指定日以降に更新があったかを確認する。

使用方法:
    python3 check_file_modified.py <since_date>

引数:
    since_date: 基準日（YYYY-MM-DD形式）

出力:
    JSON形式で各ファイルの更新情報を出力
"""

import json
import os
import re
import sys
from datetime import datetime
from typing import Optional

# 同じディレクトリのauth.pyをインポート
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from auth import get_auth_client

from googleapiclient.discovery import build


def get_skill_dir() -> str:
    """スキルディレクトリのパスを取得"""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def parse_target_files() -> list[str]:
    """TARGET_FILES.mdからURLリストを抽出

    Returns:
        list: Google DriveのURLリスト
    """
    target_file_path = os.path.join(get_skill_dir(), "TARGET_FILES.md")

    if not os.path.exists(target_file_path):
        print(f"エラー: TARGET_FILES.mdが見つかりません: {target_file_path}", file=sys.stderr)
        return []

    with open(target_file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # "- https://..." パターンでURLを抽出
    pattern = r'^- (https://docs\.google\.com/[^\s]+)'
    urls = re.findall(pattern, content, re.MULTILINE)

    return urls


def extract_file_id(url: str) -> Optional[str]:
    """Google Drive URLからファイルIDを抽出

    Args:
        url: Google DriveのURL

    Returns:
        ファイルID、抽出できない場合はNone
    """
    # /d/xxxxxxx/edit や /d/xxxxxxx のパターンに対応
    pattern = r'/d/([a-zA-Z0-9_-]+)'
    match = re.search(pattern, url)
    return match.group(1) if match else None


def check_file_modified(drive_service, file_id: str, since_date: str) -> dict:
    """ファイルの更新情報を取得

    Args:
        drive_service: Google Drive APIサービス
        file_id: ファイルID
        since_date: 基準日（YYYY-MM-DD形式）

    Returns:
        dict: ファイル情報（name, modified, modifiedTime, lastModifyingUser）
    """
    try:
        # ファイルのメタデータを取得
        # 共有ドライブのファイルにもアクセスできるよう supportsAllDrives=True を指定
        file_metadata = drive_service.files().get(
            fileId=file_id,
            fields="name,modifiedTime,lastModifyingUser",
            supportsAllDrives=True
        ).execute()

        file_name = file_metadata.get("name", "不明")
        modified_time_str = file_metadata.get("modifiedTime", "")
        last_user = file_metadata.get("lastModifyingUser", {})
        last_user_email = last_user.get("emailAddress", "-")

        # 更新日時をパース
        if modified_time_str:
            # ISO 8601形式: 2025-01-15T14:30:00.000Z
            modified_time = datetime.fromisoformat(modified_time_str.replace("Z", "+00:00"))
            since_datetime = datetime.fromisoformat(f"{since_date}T00:00:00+00:00")
            is_modified = modified_time >= since_datetime
            formatted_time = modified_time.strftime("%Y-%m-%d %H:%M")
        else:
            is_modified = False
            formatted_time = "-"

        return {
            "fileId": file_id,
            "name": file_name,
            "modified": is_modified,
            "modifiedTime": formatted_time,
            "lastModifyingUser": last_user_email,
            "error": None
        }

    except Exception as e:
        return {
            "fileId": file_id,
            "name": "取得失敗",
            "modified": False,
            "modifiedTime": "-",
            "lastModifyingUser": "-",
            "error": str(e)
        }


def main():
    if len(sys.argv) < 2:
        print("使用方法: python3 check_file_modified.py <since_date>", file=sys.stderr)
        print("例: python3 check_file_modified.py 2025-01-01", file=sys.stderr)
        sys.exit(1)

    since_date = sys.argv[1]

    # 日付形式のバリデーション
    try:
        datetime.strptime(since_date, "%Y-%m-%d")
    except ValueError:
        print(f"エラー: 日付形式が不正です。YYYY-MM-DD形式で指定してください: {since_date}", file=sys.stderr)
        sys.exit(1)

    # TARGET_FILES.mdからURLを取得
    urls = parse_target_files()
    if not urls:
        print("エラー: 監視対象ファイルが見つかりません。TARGET_FILES.mdを確認してください。", file=sys.stderr)
        sys.exit(1)

    # 認証
    creds = get_auth_client()
    if not creds:
        print("エラー: 認証に失敗しました。SETUP.mdを参照してください。", file=sys.stderr)
        sys.exit(1)

    # Drive APIサービスを構築
    drive_service = build("drive", "v3", credentials=creds)

    # 各ファイルの更新を確認
    results = []
    for url in urls:
        file_id = extract_file_id(url)
        if file_id:
            result = check_file_modified(drive_service, file_id, since_date)
            result["url"] = url
            results.append(result)
        else:
            results.append({
                "url": url,
                "fileId": None,
                "name": "ID抽出失敗",
                "modified": False,
                "modifiedTime": "-",
                "lastModifyingUser": "-",
                "error": "URLからファイルIDを抽出できませんでした"
            })

    # JSON形式で出力
    output = {
        "sinceDate": since_date,
        "totalFiles": len(results),
        "modifiedCount": sum(1 for r in results if r["modified"]),
        "results": results
    }

    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
