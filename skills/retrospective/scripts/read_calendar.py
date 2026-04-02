#!/usr/bin/env python3
"""Googleカレンダーイベント読み取りスクリプト

Usage:
    python3 read_calendar.py --start 2026-03-23 --end 2026-03-30
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from config_parser import get_resource_config
from drive_utils import get_credentials, output_json, error_result

from googleapiclient.discovery import build

WEEKDAY_NAMES = ["月", "火", "水", "木", "金", "土", "日"]


def parse_args():
    """コマンドライン引数を解析"""
    parser = argparse.ArgumentParser(description="Googleカレンダーイベント取得")
    parser.add_argument("--start", required=True, help="開始日 (YYYY-MM-DD)")
    parser.add_argument("--end", required=True, help="終了日 (YYYY-MM-DD)")
    return parser.parse_args()


def extract_tags(summary: str) -> list[str]:
    """イベントタイトルから全タグを抽出（複数対応）"""
    return re.findall(r"#\w+", summary or "")


def get_time_block(hour: int) -> str:
    """時刻（0-23）から時間帯名を返す"""
    if 5 <= hour < 7:
        return "early_morning_5_7"
    elif 7 <= hour < 12:
        return "morning_7_12"
    elif 12 <= hour < 17:
        return "afternoon_12_17"
    elif 17 <= hour < 21:
        return "evening_17_21"
    else:
        return "night_21_5"


def fetch_events(
    service, calendar_id: str, time_min: str, time_max: str, timezone: str
) -> list:
    """Calendar APIからイベントを全件取得（ページネーション対応）"""
    all_events = []
    page_token = None

    while True:
        response = (
            service.events()
            .list(
                calendarId=calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                timeZone=timezone,
                singleEvents=True,
                orderBy="startTime",
                pageToken=page_token,
            )
            .execute()
        )

        all_events.extend(response.get("items", []))
        page_token = response.get("nextPageToken")
        if not page_token:
            break

    return all_events


def parse_event(event: dict, tag_mapping: dict) -> dict | None:
    """APIレスポンスの1イベントを整形済み辞書に変換"""
    summary = event.get("summary", "（タイトルなし）")
    start = event.get("start", {})
    end = event.get("end", {})

    tags = extract_tags(summary)
    categories = (
        [tag_mapping.get(t, "未分類") for t in tags] if tags else ["未分類"]
    )

    # 終日イベント
    if "date" in start:
        return {
            "date": start["date"],
            "startTime": None,
            "endTime": None,
            "duration_hours": None,
            "summary": summary,
            "tags": tags,
            "categories": categories,
            "allDay": True,
        }

    # 時間指定イベント
    start_dt = datetime.fromisoformat(start["dateTime"])
    end_dt = datetime.fromisoformat(end["dateTime"])
    duration = (end_dt - start_dt).total_seconds() / 3600

    return {
        "date": start_dt.strftime("%Y-%m-%d"),
        "startTime": start_dt.strftime("%H:%M"),
        "endTime": end_dt.strftime("%H:%M"),
        "duration_hours": round(duration, 2),
        "summary": summary,
        "tags": tags,
        "categories": categories,
        "allDay": False,
    }


def build_daily_summary(events: list, start_date: str, end_date: str) -> list:
    """イベントリストから日別サマリーを生成"""
    daily = defaultdict(list)
    for ev in events:
        if ev["date"]:
            daily[ev["date"]].append(ev)

    summaries = []
    current = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    time_block_names = [
        "early_morning_5_7",
        "morning_7_12",
        "afternoon_12_17",
        "evening_17_21",
        "night_21_5",
    ]

    while current < end:
        date_str = current.strftime("%Y-%m-%d")
        day_events = daily.get(date_str, [])

        # カテゴリ別合計時間（複数タグの場合は全カテゴリにフル計上）
        total_by_category = defaultdict(float)
        for ev in day_events:
            if ev["duration_hours"] and ev["categories"]:
                for cat in ev["categories"]:
                    total_by_category[cat] += ev["duration_hours"]

        # 時間帯別の行動リスト
        time_blocks = {name: [] for name in time_block_names}
        for ev in day_events:
            if ev["allDay"] or not ev["startTime"]:
                continue
            hour = int(ev["startTime"].split(":")[0])
            block = get_time_block(hour)
            cats = ", ".join(ev["categories"])
            label = f"{ev['startTime']}-{ev['endTime']} {ev['summary']} [{cats}]"
            time_blocks[block].append(label)

        summaries.append(
            {
                "date": date_str,
                "dayOfWeek": WEEKDAY_NAMES[current.weekday()],
                "totalByCategory": dict(total_by_category),
                "timeBlocks": time_blocks,
            }
        )

        current += timedelta(days=1)

    return summaries


def main():
    args = parse_args()
    config = get_resource_config("calendar")
    creds = get_credentials()
    service = build("calendar", "v3", credentials=creds)

    calendar_id = config.get("calendar_id", "primary")
    timezone = config.get("timezone", "Asia/Tokyo")
    tag_mapping = config.get("tag_mapping", {})

    # RFC3339形式に変換
    time_min = f"{args.start}T00:00:00+09:00"
    time_max = f"{args.end}T23:59:59+09:00"

    try:
        raw_events = fetch_events(
            service, calendar_id, time_min, time_max, timezone
        )
        events = [parse_event(ev, tag_mapping) for ev in raw_events]
        events = [ev for ev in events if ev is not None]

        daily_summary = build_daily_summary(events, args.start, args.end)

        output_json(
            {
                "success": True,
                "resource": "calendar",
                "period": {"start": args.start, "end": args.end},
                "events": events,
                "dailySummary": daily_summary,
            }
        )
    except Exception as e:
        output_json(error_result(str(e)))
        sys.exit(1)


if __name__ == "__main__":
    main()
