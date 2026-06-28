#!/usr/bin/env python3
"""
Google認証モジュール（daily-notebooklm-research専用）

既存のOAuth認証情報（client_secret.json/token.json）を共有して使う。
このファイルが対象とするのはGoogle Docs APIの読み取りのみ。

認証ファイル:
    ~/.config/google-drive-skills/client_secret.json
    ~/.config/google-drive-skills/token.json
"""

import json
import os
from typing import Optional

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/documents.readonly"]


def get_config_paths() -> tuple[str, str]:
    config_dir = os.path.join(os.path.expanduser("~"), ".config", "google-drive-skills")
    credentials_path = os.path.join(config_dir, "client_secret.json")
    token_path = os.path.join(config_dir, "token.json")
    return credentials_path, token_path


def get_auth_client() -> Optional[Credentials]:
    credentials_path, token_path = get_config_paths()

    if not os.path.exists(credentials_path):
        print(f"認証情報ファイルが見つかりません: {credentials_path}")
        return None

    if not os.path.exists(token_path):
        print("トークンが見つかりません。ブラウザで認証を行います...")
        try:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
            token_data = {
                "access_token": creds.token,
                "refresh_token": creds.refresh_token,
                "token_uri": creds.token_uri,
                "client_id": creds.client_id,
                "client_secret": creds.client_secret,
            }
            with open(token_path, "w") as f:
                json.dump(token_data, f)
            print(f"認証成功。トークンを保存しました: {token_path}")
            return creds
        except Exception as e:
            print(f"認証フロー中にエラー: {e}")
            return None

    try:
        with open(token_path, "r") as f:
            token_data = json.load(f)

        creds = Credentials(
            token=token_data.get("access_token"),
            refresh_token=token_data.get("refresh_token"),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=token_data.get("client_id"),
            client_secret=token_data.get("client_secret"),
        )

        if not creds.client_id or not creds.client_secret:
            with open(credentials_path, "r") as f:
                cred_data = json.load(f)
            installed = cred_data.get("installed") or cred_data.get("web", {})
            creds = Credentials(
                token=token_data.get("access_token"),
                refresh_token=token_data.get("refresh_token"),
                token_uri="https://oauth2.googleapis.com/token",
                client_id=installed.get("client_id"),
                client_secret=installed.get("client_secret"),
            )

        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            new_token_data = {
                "access_token": creds.token,
                "refresh_token": creds.refresh_token,
                "token_uri": creds.token_uri,
                "client_id": creds.client_id,
                "client_secret": creds.client_secret,
            }
            with open(token_path, "w") as f:
                json.dump(new_token_data, f)

        return creds
    except Exception as e:
        print(f"認証エラー: {e}")
        return None
