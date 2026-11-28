#!/usr/bin/env python3
"""
CONFIG.md パーサー

CONFIG.mdのYAMLコードブロック（2階層の「キー: 値」のみ）からリソース設定を読み込み、
Google Drive URLからファイルIDを自動抽出する。
クラウド環境でpipが使えない場合に備え、PyYAMLに依存せず標準ライブラリだけで解析する。
"""

import re
from pathlib import Path

CONFIG_PATH = Path(__file__).parent.parent / "CONFIG.md"


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


def _scalar(text: str):
    """値の文字列を解釈する（引用符は外す。空はNone、数値はint）"""
    text = text.strip()
    if len(text) >= 2 and text[0] == text[-1] and text[0] in "\"'":
        return text[1:-1]
    text = re.sub(r"\s+#.*$", "", text)  # 引用符なしの値の行末コメント
    if text in ("", "~", "null"):
        return None
    if re.fullmatch(r"-?\d+", text):
        return int(text)
    return text


def _parse_simple_yaml(yaml_text: str) -> dict:
    """「トップレベルキー:」の下にインデントした「キー: 値」が並ぶ2階層のYAMLを辞書にする"""
    config, current = {}, None
    for lineno, raw in enumerate(yaml_text.splitlines(), start=1):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        match = re.match(r"^(\s*)([A-Za-z0-9_]+):(.*)$", raw)
        if not match:
            raise ValueError(f"CONFIG.mdのYAML {lineno}行目を解釈できません: {raw}")
        indent, key, rest = match.groups()
        if not indent:
            if rest.strip():
                config[key] = _scalar(rest)
                current = None
            else:
                current = config[key] = {}
        elif current is None:
            raise ValueError(f"CONFIG.mdのYAML {lineno}行目: 親キーのない字下げです: {raw}")
        else:
            current[key] = _scalar(rest)
    return config


def _add_file_ids(config: dict) -> dict:
    """各リソースのurlフィールドからfile_idを抽出して追加"""
    for value in config.values():
        if isinstance(value, dict) and "docs.google.com" in (value.get("url") or ""):
            value["file_id"] = extract_file_id(value["url"])
    return config


def load_config() -> dict:
    """CONFIG.mdからリソース設定を読み込む。urlからfile_idを自動付与"""
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"CONFIG.mdが見つかりません: {CONFIG_PATH}")
    markdown_text = CONFIG_PATH.read_text(encoding="utf-8")
    return _add_file_ids(_parse_simple_yaml(_extract_yaml_block(markdown_text)))


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
