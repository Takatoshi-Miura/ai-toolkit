"""CONFIG.mdパーサー

Markdownテーブル形式のCONFIG.mdを読み取り、構造化されたdictを返す。
対象スキルのSKILL.mdフロントマターからallowed-toolsを読み取る機能も提供する。
"""

from __future__ import annotations

import re
from pathlib import Path

# CONFIG.mdのデフォルトパス
DEFAULT_CONFIG_PATH = Path(__file__).parent.parent / "CONFIG.md"

# スキルの配置先ベースパス
SKILLS_BASE_PATH = Path.home() / ".claude" / "skills"


def parse_config(config_path: str | Path | None = None) -> dict:
    """CONFIG.mdを読み取り、構造化されたdictを返す。"""
    path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH
    content = path.read_text(encoding="utf-8")

    sections = _split_sections(content)

    return {
        "listener": {"log_level": "INFO", "max_concurrent": 3},
        "notifications": _parse_notifications(sections),
        "channels": _parse_channels(sections),
        "mention_targets": _parse_mention_targets(sections),
        "routes": _parse_routes(sections),
    }


def get_allowed_tools(skill_name: str) -> str:
    """対象スキルのSKILL.mdフロントマターからallowed-toolsを読み取る。"""
    skill_path = SKILLS_BASE_PATH / skill_name / "SKILL.md"
    if not skill_path.exists():
        return "Bash,Read,TodoWrite"

    content = skill_path.read_text(encoding="utf-8")
    frontmatter = _parse_frontmatter(content)
    return frontmatter.get("allowed-tools", "Bash,Read,TodoWrite")


# --- 内部ユーティリティ ---


def _split_sections(content: str) -> dict[str, str]:
    """Markdownの見出し(##)でセクションを分割する。"""
    sections = {}
    current_key = ""
    current_lines = []

    for line in content.split("\n"):
        if line.startswith("## "):
            if current_key:
                sections[current_key] = "\n".join(current_lines)
            current_key = line[3:].strip()
            current_lines = []
        else:
            current_lines.append(line)

    if current_key:
        sections[current_key] = "\n".join(current_lines)

    return sections


def _parse_table(text: str) -> list[dict[str, str]]:
    """Markdownテーブルをパースし、ヘッダーをキーとしたdictのリストを返す。"""
    lines = [l.strip() for l in text.strip().split("\n") if l.strip()]

    # テーブル行のみ抽出（|で始まる行）
    table_lines = [l for l in lines if l.startswith("|")]
    if len(table_lines) < 2:
        return []

    # ヘッダー行
    headers = [_clean_cell(c) for c in _split_table_row(table_lines[0])]

    rows = []
    for line in table_lines[2:]:  # セパレーター行をスキップ
        cells = [_clean_cell(c) for c in _split_table_row(line)]
        if len(cells) == len(headers):
            rows.append(dict(zip(headers, cells)))

    return rows


def _split_table_row(line: str) -> list[str]:
    """テーブル行をセル分割する。バッククォート内の|は列区切りとして扱わない。"""
    # バッククォート内の|を一時的にプレースホルダーに置換
    placeholder = "\x00PIPE\x00"
    in_backtick = False
    chars = []
    for ch in line:
        if ch == "`":
            in_backtick = not in_backtick
            chars.append(ch)
        elif ch == "|" and in_backtick:
            chars.append(placeholder)
        else:
            chars.append(ch)
    protected = "".join(chars)

    # |で分割してプレースホルダーを元に戻す
    cells = protected.split("|")[1:-1]  # 先頭と末尾の空要素を除去
    return [c.replace(placeholder, "|") for c in cells]


def _clean_cell(cell: str) -> str:
    """セル内のバッククォートや余分な空白を除去する。"""
    return cell.strip().strip("`").strip()


def _parse_frontmatter(content: str) -> dict[str, str]:
    """SKILL.mdのYAMLフロントマター(---で囲まれた部分)をパースする。"""
    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return {}

    frontmatter = {}
    for line in match.group(1).split("\n"):
        line = line.strip()
        if ":" in line:
            key, _, value = line.partition(":")
            frontmatter[key.strip()] = value.strip()
    return frontmatter


# --- セクション別パーサー ---


def _parse_notifications(sections: dict[str, str]) -> dict:
    """通知チャンネルセクションをパースする。先頭行のチャンネルIDを使用。"""
    rows = _parse_table(sections.get("通知チャンネル", ""))
    return {
        "channel": rows[0].get("チャンネルID", "") if rows else "",
    }


def _parse_channels(sections: dict[str, str]) -> list[dict[str, str]]:
    """監視対象チャンネルセクションをパースする。"""
    rows = _parse_table(sections.get("監視対象チャンネル", ""))
    return [
        {"id": row.get("チャンネルID", ""), "name": row.get("チャンネル名（メモ）", "")}
        for row in rows if row.get("チャンネルID")
    ]


def _parse_mention_targets(sections: dict[str, str]) -> list[str]:
    """メンション対象ユーザーセクションをパースする。"""
    rows = _parse_table(sections.get("メンション対象ユーザー", ""))
    return [row.get("ユーザーID", "") for row in rows if row.get("ユーザーID")]


def _parse_routes(sections: dict[str, str]) -> list[dict]:
    """ルーティングルールセクションをパースする。"""
    rows = _parse_table(sections.get("ルーティングルール", ""))
    routes = []
    for row in rows:
        keywords_raw = row.get("キーワード", "")
        keywords = [k.strip() for k in keywords_raw.split(",") if k.strip()]
        routes.append({
            "skill": row.get("スキル名", ""),
            "keywords": keywords,
        })
    return routes


if __name__ == "__main__":
    import json
    config = parse_config()
    print(json.dumps(config, ensure_ascii=False, indent=2))
