#!/usr/bin/env python3
"""Slack Message Router - Socket Modeリスナー

Slackメッセージを監視し、CONFIG.mdのルーティングルールに基づいて
適切なClaude Codeスキルを自動起動する常駐プロセス。

起動:
    python3 slack_listener.py

停止:
    Ctrl+C (SIGINT) または SIGTERM
"""

from __future__ import annotations

import json
import logging
import os
import shutil
import signal
import subprocess
import sys
import threading
from pathlib import Path

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# config_parserを同じディレクトリからインポート
sys.path.insert(0, str(Path(__file__).parent))
from config_parser import get_allowed_tools, parse_config

# --- 定数 ---
BOT_TOKEN_ENV = "SLACK_BOT_TOKEN"
APP_TOKEN_ENV = "SLACK_APP_TOKEN"

# --- グローバル状態 ---
logger = logging.getLogger("slack-message-router")


def main():
    config = parse_config()
    _setup_logging(config["listener"]["log_level"])

    # 環境変数の検証
    bot_token = os.environ.get(BOT_TOKEN_ENV)
    app_token = os.environ.get(APP_TOKEN_ENV)

    if not bot_token:
        logger.error(f"環境変数 {BOT_TOKEN_ENV} が設定されていません")
        sys.exit(1)
    if not app_token:
        logger.error(f"環境変数 {APP_TOKEN_ENV} が設定されていません")
        sys.exit(1)

    # claude CLIの存在確認（標準PATHに加え、一般的なインストール先もフォールバック検索）
    claude_path = shutil.which("claude")
    if not claude_path:
        for _p in [
            Path.home() / ".local/bin/claude",
            Path("/usr/local/bin/claude"),
            Path("/opt/homebrew/bin/claude"),
        ]:
            if _p.is_file() or _p.is_symlink():
                claude_path = str(_p)
                logger.warning(f"claude CLIをフォールバックパスで発見: {claude_path}")
                break
    if not claude_path:
        logger.error(
            "claude CLIが見つかりません。~/.local/bin/claude にシンボリックリンクを作成するか、"
            "PATHに claude のディレクトリを追加してください"
        )
        sys.exit(1)
    logger.info(f"claude CLI: {claude_path}")

    # 同時実行制御
    semaphore = threading.Semaphore(config["listener"]["max_concurrent"])

    # Slack App初期化
    app = App(token=bot_token)

    # メッセージハンドラ登録
    @app.event("message")
    def handle_message(event):
        _on_message(event, config, semaphore, claude_path)

    # グレースフルシャットダウン
    handler = SocketModeHandler(app, app_token)

    def _shutdown(signum, frame):
        sig_name = signal.Signals(signum).name
        logger.info(f"{sig_name} を受信。シャットダウンします...")
        _notify(config, f":octagonal_sign: リスナー停止", f"シグナル: {sig_name}", mention=False)
        handler.close()

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    # 起動通知（メンションなし、表形式で詳細表示）
    route_lines = "\n".join(
        f"| {r['skill']} | {', '.join(r['keywords'])} |"
        for r in config["routes"]
    ) if config["routes"] else "| (なし) | |"

    startup_body = (
        "*ルーティングルール:*\n"
        "| スキル名 | キーワード |\n"
        "|---|---|\n"
        f"{route_lines}"
    )

    _notify(config, ":rocket: リスナー起動", startup_body, mention=False)
    logger.info("Socket Mode接続を開始します...")
    handler.start()


# --- メッセージ処理 ---


def _on_message(event: dict, config: dict, semaphore: threading.Semaphore, claude_path: str):
    """メッセージイベントのハンドラ。"""
    # Botメッセージ・サブタイプ付きメッセージをスキップ
    if event.get("subtype") or event.get("bot_id"):
        return

    channel = event.get("channel", "")
    user = event.get("user", "")
    text = event.get("text", "")

    # メンション対象フィルター: 指定ユーザーへのメンションを含むメッセージのみ処理
    mention_targets = config["mention_targets"]
    if mention_targets:
        mentioned = any(f"<@{uid}>" in text for uid in mention_targets)
        if not mentioned:
            return

    # ルーティングルールマッチング（上から順、最初にマッチしたルールを実行）
    matched_route = None
    for route in config["routes"]:
        for keyword in route["keywords"]:
            if keyword.lower() in text.lower():
                matched_route = route
                break
        if matched_route:
            break

    if not matched_route:
        return

    logger.info(f"ルールマッチ: {matched_route['skill']} (user={user}, channel={channel})")

    # 同時実行数チェック
    if not semaphore.acquire(blocking=False):
        _notify(config, ":hourglass: 同時実行数上限に到達", "スキル実行をスキップしました")
        logger.warning(f"同時実行数上限: {matched_route['skill']}")
        return

    # 実行開始通知
    _notify(config, f":gear: スキル実行開始: *{matched_route['skill']}*")

    # サブスレッドでclaude CLI実行
    thread = threading.Thread(
        target=_run_skill,
        args=(config, matched_route, text, semaphore, claude_path),
        daemon=True,
    )
    thread.start()


# --- スキル実行 ---


def _run_skill(
    config: dict,
    route: dict,
    message: str,
    semaphore: threading.Semaphore,
    claude_path: str,
):
    """サブスレッドでclaude CLIを実行する。"""
    try:
        # allowed-toolsをスキルのSKILL.mdから読み取り
        allowed_tools = get_allowed_tools(route["skill"])

        # claude CLIコマンドを組み立て
        prompt_data = {
            "skill": route["skill"],
            "message": message,
        }

        prompt_json = json.dumps(prompt_data, ensure_ascii=False)
        cmd = [
            claude_path,
            "-p",
            prompt_json,
            "--output-format", "json",
            "--allowed-tools", allowed_tools,
        ]

        logger.info(f"コマンド実行: claude -p '{prompt_json}' --allowed-tools \"{allowed_tools}\"")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=1800,  # 30分タイムアウト
        )

        result_text = _extract_result_text(result.stdout)

        if result_text:
            # 成功結果はルート指定の通知先に投稿（未指定ならデフォルト）
            result_ch = route.get("notify_channel") or None
            _notify(config, result_text, channel_override=result_ch)
        elif result.returncode == 0:
            _notify(config, f":white_check_mark: スキル実行完了: *{route['skill']}*")
        else:
            error_msg = result.stderr[:500] if result.stderr else "不明なエラー"
            _notify(
                config,
                f":x: スキル実行エラー: *{route['skill']}*",
                f"```\n{error_msg}\n```",
            )

        if result.returncode == 0:
            logger.info(f"スキル実行完了: {route['skill']}")
        else:
            logger.error(f"スキル実行エラー: {route['skill']}")

    except subprocess.TimeoutExpired:
        _notify(
            config,
            f":warning: スキル実行タイムアウト: *{route['skill']}*",
            "30分でタイムアウトしました",
        )
        logger.error(f"スキル実行タイムアウト: {route['skill']}")

    except Exception as e:
        _notify(config, f":x: 予期しないエラー: *{route['skill']}*", f"エラー: {e}")
        logger.exception(f"予期しないエラー: {route['skill']}")

    finally:
        semaphore.release()


# --- スキル結果解析 ---


def _extract_result_text(stdout: str) -> str:
    """Claude CLI JSON出力からresultフィールドのテキストを取得する。"""
    if not stdout:
        return ""
    try:
        cli_output = json.loads(stdout)
        if isinstance(cli_output, dict) and "result" in cli_output:
            return cli_output["result"]
    except (json.JSONDecodeError, TypeError):
        pass
    return stdout


# --- Slack通知ヘルパー ---


def _mention_str(config: dict) -> str:
    """メンション対象ユーザーのメンション文字列を返す。"""
    targets = config.get("mention_targets", [])
    if not targets:
        return ""
    return " ".join(f"<@{uid}>" for uid in targets)


def _notify(config: dict, subject: str, body: str = "", mention: bool = True, channel_override: str = None):
    """通知チャンネルにメッセージを送信する。形式: メンション → 件名 → 内容"""
    channel = channel_override or config["notifications"].get("channel")
    if not channel:
        return
    mention_text = _mention_str(config) if mention else ""
    parts = [p for p in [mention_text, subject, body] if p]
    message = "\n".join(parts)
    _send_slack_message(config, channel, message)


def _send_slack_message(config: dict, channel: str, message: str):
    """Slack APIでメッセージを送信する。リスナー内部用。"""
    from slack_sdk import WebClient
    from slack_sdk.errors import SlackApiError

    token = os.environ.get(BOT_TOKEN_ENV)
    if not token:
        logger.error("Bot Tokenが未設定のためSlack通知をスキップ")
        return

    client = WebClient(token=token)
    try:
        client.chat_postMessage(channel=channel, text=message)
    except SlackApiError as e:
        logger.error(f"Slack通知失敗: {e}")


# --- ユーティリティ ---


def _setup_logging(level: str):
    """ロギングを設定する。"""
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


if __name__ == "__main__":
    main()
