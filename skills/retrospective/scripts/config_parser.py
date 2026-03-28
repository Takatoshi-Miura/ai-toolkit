#!/usr/bin/env python3
"""
CONFIG.md パーサー

CONFIG.mdのYAMLコードブロックからリソース設定を読み込み、
Google Drive URLからファイルIDを自動抽出する。
"""

import re
import subprocess
import sys
from pathlib import Path

CONFIG_PATH = Path(__file__).parent.parent / "CONFIG.md"


def _ensure_pyyaml():
    """PyYAMLがなければインストール"""
    try:
        import yaml  # noqa: F401
    except ImportError:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "pyyaml", "-q"]
        )


def extract_file_id(url: str) -> str:
    """Google Drive URLからファイルIDを抽出

    対応パターン:
        https://docs.google.com/spreadsheets/d/{file_id}/edit...
        https://docs.google.com/document/d/{file_id}/edit...
        https://docs.google.com/presentation/d/{file_id}/edit...
    """
    match = re.search(r"/d/([a-zA-Z0-9_-]+)", url)
    if not match:
        raise ValueError(f"URLからファイルIDを抽出できません: {url}")
    return match.group(1)


def _extract_yaml_block(markdown_text: str) -> str:
    """Markdownからyamlコードブロックの中身を抽出"""
    match = re.search(r"```yaml\s*\n(.*?)```", markdown_text, re.DOTALL)
    if not match:
        raise ValueError("CONFIG.mdにYAMLコードブロックが見つかりません")
    return match.group(1)


def _add_file_ids(config: dict) -> dict:
    """各リソースのurlフィールドからfile_idを抽出して追加"""
    for key, value in config.items():
        if isinstance(value, dict) and "url" in value:
            value["file_id"] = extract_file_id(value["url"])
    return config


def load_config() -> dict:
    """CONFIG.mdからリソース設定を読み込む。urlからfile_idを自動付与"""
    _ensure_pyyaml()
    import yaml

    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"CONFIG.mdが見つかりません: {CONFIG_PATH}")

    markdown_text = CONFIG_PATH.read_text(encoding="utf-8")
    yaml_text = _extract_yaml_block(markdown_text)
    config = yaml.safe_load(yaml_text)
    return _add_file_ids(config)


def get_resource_config(resource_name: str) -> dict:
    """特定リソースの設定を取得（file_id付き）

    例: get_resource_config("lifegraph")
    """
    config = load_config()
    if resource_name not in config:
        raise KeyError(
            f'リソース "{resource_name}" がCONFIG.mdに見つかりません。'
            f"利用可能: {list(config.keys())}"
        )
    return config[resource_name]
