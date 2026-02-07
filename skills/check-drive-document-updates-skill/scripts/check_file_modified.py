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


def parse_file_metadata(file_metadata: dict, file_id: str, since_date: str) -> dict:
    """APIレスポンスからファイル更新情報をパース

    Args:
        file_metadata: Google Drive APIのレスポンス
        file_id: ファイルID
        since_date: 基準日（YYYY-MM-DD形式）

    Returns:
        dict: ファイル情報（name, modified, modifiedTime, lastModifyingUser）
    """
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


def check_files_modified_batch(drive_service, file_entries: list[dict], since_date: str) -> list[dict]:
    """バッチリクエストで複数ファイルの更新情報を一括取得

    Args:
        drive_service: Google Drive APIサービス
        file_entries: ファイル情報のリスト（各要素は url, file_id を含む dict）
        since_date: 基準日（YYYY-MM-DD形式）

    Returns:
        list[dict]: 各ファイルの更新情報リスト
    """
    results = [None] * len(file_entries)

    def callback(request_id, response, exception):
        idx = int(request_id)
        entry = file_entries[idx]
        if exception:
            results[idx] = {
                "url": entry["url"],
                "fileId": entry["file_id"],
                "name": "取得失敗",
                "modified": False,
                "modifiedTime": "-",
                "lastModifyingUser": "-",
                "error": str(exception)
            }
        else:
            result = parse_file_metadata(response, entry["file_id"], since_date)
            result["url"] = entry["url"]
            results[idx] = result

    batch = drive_service.new_batch_http_request(callback=callback)
    for i, entry in enumerate(file_entries):
        batch.add(
            drive_service.files().get(
                fileId=entry["file_id"],
                fields="name,modifiedTime,lastModifyingUser",
                supportsAllDrives=True
            ),
            request_id=str(i)
        )

    batch.execute()
    return results


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

    # URLからファイルIDを抽出し、バッチ対象とエラー分を分離
    file_entries = []
    error_results = []
    for url in urls:
        file_id = extract_file_id(url)
        if file_id:
            file_entries.append({"url": url, "file_id": file_id})
        else:
            error_results.append({
                "url": url,
                "fileId": None,
                "name": "ID抽出失敗",
                "modified": False,
                "modifiedTime": "-",
                "lastModifyingUser": "-",
                "error": "URLからファイルIDを抽出できませんでした"
            })

    # バッチリクエストで一括取得
    if file_entries:
        results = check_files_modified_batch(drive_service, file_entries, since_date)
    else:
        results = []

    results.extend(error_results)

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
