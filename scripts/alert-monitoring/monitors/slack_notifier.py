"""Slack App（Bot Token）経由でアラート通知を送信するモジュール。"""

from __future__ import annotations

import logging
from email.utils import parsedate_to_datetime
from zoneinfo import ZoneInfo

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

logger = logging.getLogger(__name__)

_WEEKDAYS_JA = ["月", "火", "水", "木", "金", "土", "日"]


def _format_received_at(raw: str) -> str:
    """RFC 2822形式の日時文字列を日本時間の読みやすい形式に変換する。"""
    try:
        dt = parsedate_to_datetime(raw).astimezone(ZoneInfo("Asia/Tokyo"))
        weekday = _WEEKDAYS_JA[dt.weekday()]
        return dt.strftime(f"%Y/%m/%d({weekday}) %H:%M")
    except Exception:
        return raw


def format_notification(monitor_name: str, email: dict) -> str:
    """メール情報からSlack通知メッセージを整形する。"""
    subject = email.get("subject", "(件名なし)")
    received_at = _format_received_at(email.get("received_at", "(不明)"))
    body_preview = email.get("body_preview", "")

    return (
        f"*[アラート]* {monitor_name}\n"
        f"*件名:* {subject}\n"
        f"*受信時刻:* {received_at}\n"
        f"*本文（先頭300文字）:*\n```{body_preview}```"
    )


def send_slack_message(bot_token: str, channel: str, message: str) -> bool:
    """Slack APIでメッセージを送信する。"""
    client = WebClient(token=bot_token)
    try:
        client.chat_postMessage(channel=channel, text=message)
        return True
    except SlackApiError as e:
        logger.error("Slack通知失敗: %s", e)
        return False


def notify(
    monitor_name: str,
    emails: list[dict],
    bot_token: str,
    channel: str,
    dry_run: bool = False,
) -> int:
    """マッチしたメール群をSlackに通知する。送信成功数を返す。"""
    sent = 0
    for email in emails:
        message = format_notification(monitor_name, email)

        if dry_run:
            print(f"[DRY-RUN] Channel: {channel}")
            print(message)
            print("---")
            sent += 1
            continue

        if send_slack_message(bot_token, channel, message):
            sent += 1

    return sent
