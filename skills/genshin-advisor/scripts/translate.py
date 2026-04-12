#!/usr/bin/env python3
"""
translate.py — 中国語 → 日本語 変換モジュール

Enka の loc.json（.genshin_cache/ にキャッシュ済み）を使って
HoYoLAB API が返す中国語のキャラ名・武器名・聖遺物セット名を日本語に変換する。

使い方（モジュールとして）:
    from translate import Translator
    t = Translator()
    t.char("那维莱特")   # -> "ヌヴィレット"
    t.weapon("万世流涌大典") # -> "久遠流転の大典"
    t.name("深林的记忆")  # -> "深林の記憶"（汎用・聖遺物セット等）

使い方（CLIとして）:
    python translate.py "那维莱特"
    python translate.py --type weapon "万世流涌大典"
    python translate.py --rebuild   # キャッシュを再構築
"""

import json
import sys
import argparse
import urllib.request
from pathlib import Path

CACHE_DIR  = Path(".genshin_cache")
CHAR_URL   = "https://raw.githubusercontent.com/EnkaNetwork/API-docs/master/store/characters.json"
LOC_URL    = "https://raw.githubusercontent.com/EnkaNetwork/API-docs/master/store/loc.json"
TABLE_FILE = CACHE_DIR / "zh_to_ja.json"


def _fetch_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "genshin-advisor/1.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode())


def _load_cached(filename: str, url: str) -> dict:
    CACHE_DIR.mkdir(exist_ok=True)
    path = CACHE_DIR / filename
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    data = _fetch_json(url)
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return data


def build_table(force: bool = False) -> dict:
    """zh-cn → ja 変換テーブルを構築してキャッシュに保存する。"""
    if not force and TABLE_FILE.exists():
        return json.loads(TABLE_FILE.read_text(encoding="utf-8"))

    chars = _load_cached("characters.json", CHAR_URL)
    loc   = _load_cached("loc.json", LOC_URL)
    loc_zh = loc.get("zh-cn", {})
    loc_ja = loc.get("ja", {})

    # キャラ名: NameTextMapHash 経由
    table: dict[str, str] = {}
    for cdata in chars.values():
        h  = str(cdata.get("NameTextMapHash", ""))
        zh = loc_zh.get(h)
        ja = loc_ja.get(h)
        if zh and ja:
            table[zh] = ja

    # 武器名・聖遺物セット名・その他すべて: zh-cn 逆引き → ja
    # (loc_zh の値→キー逆引きテーブルを一度だけ構築)
    zh_to_hash = {v: k for k, v in loc_zh.items()}
    for zh, h in zh_to_hash.items():
        if zh not in table:
            ja = loc_ja.get(h)
            if ja:
                table[zh] = ja

    CACHE_DIR.mkdir(exist_ok=True)
    TABLE_FILE.write_text(json.dumps(table, ensure_ascii=False, indent=2), encoding="utf-8")
    return table


class Translator:
    """中国語テキストを日本語に変換するシンプルなクラス。"""

    def __init__(self, force_rebuild: bool = False):
        self._table = build_table(force=force_rebuild)

    def translate(self, text: str, fallback: str | None = None) -> str:
        """汎用変換。未登録の場合は fallback（省略時は元の文字列）を返す。"""
        return self._table.get(text, fallback if fallback is not None else text)

    # 意味を明確にするエイリアス
    def char(self, name: str)   -> str: return self.translate(name)
    def weapon(self, name: str) -> str: return self.translate(name)
    def name(self, text: str)   -> str: return self.translate(text)

    def stats(self) -> dict:
        return {"entries": len(self._table)}


# ────────────── CLI ──────────────
def main():
    parser = argparse.ArgumentParser(description="中国語→日本語 変換ツール")
    parser.add_argument("text", nargs="?", help="変換したい中国語テキスト")
    parser.add_argument("--type", choices=["char", "weapon", "any"], default="any",
                        help="変換対象の種別（デフォルト: any）")
    parser.add_argument("--rebuild", action="store_true",
                        help="変換テーブルを強制再構築してキャッシュを更新する")
    parser.add_argument("--stats", action="store_true",
                        help="テーブルの統計情報を表示する")
    args = parser.parse_args()

    t = Translator(force_rebuild=args.rebuild)

    if args.stats or args.rebuild:
        s = t.stats()
        print(f"変換テーブル件数: {s['entries']} エントリ")
        if not args.text:
            return

    if not args.text:
        parser.print_help()
        return

    print(t.translate(args.text))


if __name__ == "__main__":
    main()
