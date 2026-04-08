"""Slack App（Bot Token）経由でアラート通知を送信するモジュール。"""

from __future__ import annotations

import logging

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

logger = logging.getLogger(__name__)


def format_notification(monitor_name: str, email: dict) -> str:
    """メール情報からSlack通知メッセージを整形する。"""
    subject = email.get("subject", "(件名なし)")
    received_at = email.get("received_at", "(不明)")
    body_preview = email.get("body_preview", "")

    return (
        f":rotating_light: *[アラート]* {monitor_name}\n"
        f":envelope: *件名:* {subject}\n"
        f":calendar: *受信時刻:* {received_at}\n"
        f":memo: *本文（先頭300文字）:*\n{body_preview}"
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
