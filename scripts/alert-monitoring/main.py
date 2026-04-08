"""アラート監視システムのエントリーポイント。

monitors.yamlの設定に基づいてGmailを監視し、条件に一致するメールをSlackに通知する。
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path

import yaml

from monitors.gmail_monitor import build_credentials, run_monitor
from monitors.slack_notifier import notify

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

PROCESSED_IDS_FILE = "processed_ids.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Gmail アラート監視システム")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Slack通知を送信せず、stdout に出力する",
    )
    parser.add_argument(
        "--config",
        default="monitors.yaml",
        help="monitors.yaml のパス（デフォルト: monitors.yaml）",
    )
    return parser.parse_args()


def load_config(config_path: str) -> dict:
    path = Path(config_path)
    if not path.exists():
        logger.error("設定ファイルが見つかりません: %s", config_path)
        sys.exit(1)

    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def setup_credentials():
    credentials_json = os.environ.get("GMAIL_CREDENTIALS")
    token_json = os.environ.get("GMAIL_TOKEN")

    if not credentials_json or not token_json:
        logger.error(
            "環境変数 GMAIL_CREDENTIALS と GMAIL_TOKEN を設定してください。\n"
            "詳しくは README.md を参照してください。"
        )
        sys.exit(1)

    return build_credentials(credentials_json, token_json)


def main() -> None:
    args = parse_args()

    if args.dry_run:
        logger.info("=== DRY-RUN モード ===")

    config = load_config(args.config)
    monitors = config.get("monitors", [])

    if not monitors:
        logger.warning("monitors.yaml に監視設定がありません")
        return

    credentials = setup_credentials()
    bot_token = os.environ.get("SLACK_BOT_TOKEN", "")
    if not bot_token and not args.dry_run:
        logger.error("環境変数 SLACK_BOT_TOKEN を設定してください")
        sys.exit(1)

    processed_ids_path = Path(PROCESSED_IDS_FILE)
    total_matched = 0
    total_notified = 0

    for monitor_config in monitors:
        name = monitor_config.get("name", "unknown")

        if not monitor_config.get("enabled", True):
            logger.info("monitor '%s' はスキップされました（enabled: false）", name)
            continue

        monitor_type = monitor_config.get("type", "")
        if monitor_type != "gmail":
            logger.warning("未対応のmonitor type: %s（monitor: %s）", monitor_type, name)
            continue

        new_emails = run_monitor(monitor_config, credentials, processed_ids_path)
        total_matched += len(new_emails)

        if new_emails:
            channel = monitor_config.get("slack_channel", "#general")
            sent = notify(name, new_emails, bot_token, channel, dry_run=args.dry_run)
            total_notified += sent

    logger.info(
        "=== 完了: %d件のmonitor処理, %d件マッチ, %d件通知 ===",
        sum(1 for m in monitors if m.get("enabled", True)),
        total_matched,
        total_notified,
    )


if __name__ == "__main__":
    main()
