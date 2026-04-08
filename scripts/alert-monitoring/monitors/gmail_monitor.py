"""Gmail APIでメールを取得・フィルタリングするモジュール。"""

from __future__ import annotations

import base64
import json
import logging
import re
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

logger = logging.getLogger(__name__)

MAX_RESULTS = 50
MAX_PROCESSED_IDS = 1000


def build_credentials(credentials_json: str, token_json: str) -> Credentials:
    """環境変数から読み込んだJSONでOAuth2認証情報を構築する。"""
    creds_data = json.loads(credentials_json)
    token_data = json.loads(token_json)

    # credentials.json の installed or web キーからクライアント情報を取得
    client_info = creds_data.get("installed") or creds_data.get("web", {})

    creds = Credentials(
        token=token_data.get("token"),
        refresh_token=token_data.get("refresh_token"),
        token_uri=client_info.get("token_uri", "https://oauth2.googleapis.com/token"),
        client_id=client_info.get("client_id"),
        client_secret=client_info.get("client_secret"),
        scopes=["https://www.googleapis.com/auth/gmail.readonly"],
    )

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())

    return creds


def build_query(monitor_config: dict) -> str:
    """monitors.yamlの設定からGmail検索クエリを構築する。"""
    parts: list[str] = []

    from_addr = monitor_config.get("from_address", "")
    if from_addr:
        parts.append(f"from:{from_addr}")

    subjects = monitor_config.get("subject_contains", [])
    if isinstance(subjects, str):
        subjects = [subjects]
    if subjects:
        subject_query = " OR ".join(f"subject:{s}" for s in subjects)
        if len(subjects) > 1:
            subject_query = f"({subject_query})"
        parts.append(subject_query)

    parts.append("newer_than:1h")

    return " ".join(parts)


def _decode_body(payload: dict) -> str:
    """メールのpayloadから本文をデコードする。"""
    # シンプルなメール（partsなし）
    if "body" in payload and payload["body"].get("data"):
        return base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="replace")

    # マルチパートメール
    for part in payload.get("parts", []):
        mime_type = part.get("mimeType", "")
        if mime_type == "text/plain" and part.get("body", {}).get("data"):
            return base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="replace")

    # text/plain がなければ text/html からタグ除去
    for part in payload.get("parts", []):
        mime_type = part.get("mimeType", "")
        if mime_type == "text/html" and part.get("body", {}).get("data"):
            html = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="replace")
            return re.sub(r"<[^>]+>", "", html)

    return ""


def _extract_header(headers: list[dict], name: str) -> str:
    """メールヘッダーから指定フィールドを取得する。"""
    for header in headers:
        if header.get("name", "").lower() == name.lower():
            return header.get("value", "")
    return ""


def fetch_emails(service, monitor_config: dict) -> list[dict]:
    """Gmail APIでメールを検索・取得する。"""
    query = build_query(monitor_config)
    logger.info("Gmail検索クエリ: %s", query)

    try:
        result = service.users().messages().list(
            userId="me", q=query, maxResults=MAX_RESULTS
        ).execute()
    except Exception:
        logger.exception("Gmail APIの呼び出しに失敗しました")
        return []

    messages = result.get("messages", [])
    if not messages:
        logger.info("該当するメールはありませんでした")
        return []

    emails = []
    for msg_info in messages:
        try:
            msg = service.users().messages().get(
                userId="me", id=msg_info["id"], format="full"
            ).execute()
        except Exception:
            logger.warning("メール %s の取得に失敗しました", msg_info["id"])
            continue

        payload = msg.get("payload", {})
        headers = payload.get("headers", [])
        body = _decode_body(payload)

        emails.append({
            "message_id": msg_info["id"],
            "subject": _extract_header(headers, "Subject"),
            "from": _extract_header(headers, "From"),
            "received_at": _extract_header(headers, "Date"),
            "body_preview": body[:300],
        })

    return emails


def filter_by_body(emails: list[dict], body_contains: list[str]) -> list[dict]:
    """本文に指定キーワードを含むメールのみ返す（OR条件）。"""
    if not body_contains:
        return emails

    return [
        email for email in emails
        if any(keyword in email.get("body_preview", "") for keyword in body_contains)
    ]


def load_processed_ids(path: Path) -> set[str]:
    """処理済みメールIDをファイルから読み込む。"""
    if not path.exists():
        return set()

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return set(data.get("processed", []))
    except (json.JSONDecodeError, OSError):
        logger.warning("processed_ids.json の読み込みに失敗しました。新規作成します")
        return set()


def save_processed_ids(path: Path, ids: set[str]) -> None:
    """処理済みメールIDをファイルに保存する（最新1000件のみ保持）。"""
    trimmed = list(ids)[-MAX_PROCESSED_IDS:]
    data = {"processed": trimmed}
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def run_monitor(monitor_config: dict, credentials: Credentials, processed_ids_path: Path) -> list[dict]:
    """1つのmonitor設定に対してメール取得・フィルタリングを実行する。"""
    service = build("gmail", "v1", credentials=credentials)
    processed_ids = load_processed_ids(processed_ids_path)

    emails = fetch_emails(service, monitor_config)
    emails = filter_by_body(emails, monitor_config.get("body_contains", []))

    # 処理済みメールを除外
    new_emails = [e for e in emails if e["message_id"] not in processed_ids]

    # 処理済みIDを更新
    for email in new_emails:
        processed_ids.add(email["message_id"])
    save_processed_ids(processed_ids_path, processed_ids)

    logger.info(
        "monitor '%s': %d件取得, %d件新規",
        monitor_config.get("name", "unknown"),
        len(emails),
        len(new_emails),
    )

    return new_emails
