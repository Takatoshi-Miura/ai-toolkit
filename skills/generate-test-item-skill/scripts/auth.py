#!/usr/bin/env python3
"""
Google Drive 認証モジュール

認証ファイル:
    ~/.config/google-drive-skills/client_secret.json
    ~/.config/google-drive-skills/token.json

このモジュールは generate-test-item-skill の各スクリプトから使用される。
read-google-drive-skill / write-google-drive-skill と同じ認証設定を共有する。
"""

import json
import os
from typing import Optional

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request


def get_config_paths() -> tuple[str, str]:
    """認証ファイルのパスを取得

    Returns:
        tuple: (credentials_path, token_path)
    """
    config_dir = os.path.join(os.path.expanduser("~"), ".config", "google-drive-skills")
    credentials_path = os.path.join(config_dir, "client_secret.json")
    token_path = os.path.join(config_dir, "token.json")
    return credentials_path, token_path


def get_auth_client() -> Optional[Credentials]:
    """認証クライアントを取得

    Returns:
        Credentials: 認証済みクライアント。失敗時はNone
    """
    credentials_path, token_path = get_config_paths()

    if not os.path.exists(credentials_path):
        print(f"認証情報ファイルが見つかりません: {credentials_path}")
        print("\n以下のいずれかの方法で認証ファイルを設定してください：")
        print("  1. GOOGLE_CREDENTIALS_PATH環境変数でclient_secret.jsonのパスを指定")
        print(f"  2. {os.path.dirname(credentials_path)}/client_secret.json にファイルを配置")
        return None

    if not os.path.exists(token_path):
        print(f"トークンファイルが見つかりません: {token_path}")
        print("\n以下のいずれかの方法でトークンファイルを設定してください：")
        print("  1. GOOGLE_TOKEN_PATH環境変数でtoken.jsonのパスを指定")
        print(f"  2. {os.path.dirname(token_path)}/token.json にファイルを配置")
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

        # client_id/client_secretがtoken.jsonにない場合、credentials.jsonから取得
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

        # トークンの有効期限チェックとリフレッシュ
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            # 更新されたトークンを保存
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
