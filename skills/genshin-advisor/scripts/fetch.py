#!/usr/bin/env python3
"""
genshin-advisor fetch.py
公式HoYoLAB APIからデータを取得してJSONで出力する。

使い方:
  python3 fetch.py allchars <UID> --ltoken <ltoken_v2> --ltuid <ltuid_v2>
  python3 fetch.py status   <UID> --ltoken <ltoken_v2> --ltuid <ltuid_v2>
"""

import sys
import json
import argparse
import urllib.request
from pathlib import Path

# translate.py が同ディレクトリにある場合はインポート
_SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(_SCRIPT_DIR))
try:
    from translate import Translator as _Translator
    _translator = _Translator()
    def _t(text: str) -> str:
        return _translator.translate(text)
except ImportError:
    def _t(text: str) -> str:  # フォールバック: 変換なし
        return text

# ────────────── 定数 ──────────────
STATUS_URL   = "https://bbs-api-os.hoyoverse.com/game_record/genshin/api/dailyNote"
CHAR_LIST_URL   = "https://bbs-api-os.hoyoverse.com/game_record/genshin/api/character/list"
CHAR_DETAIL_URL = "https://bbs-api-os.hoyoverse.com/game_record/genshin/api/character/detail"
CACHE_DIR  = Path(".genshin_cache")

# HoYoLAB の property_type 数値 → 日本語名マッピング
PROP_TYPE_JP = {
    1:  "HP",
    2:  "HP",
    3:  "HP%",
    4:  "攻撃力",
    5:  "攻撃力",
    6:  "攻撃%",
    7:  "防御力",
    8:  "防御力",
    9:  "防御%",
    20: "会心率",
    22: "会心ダメージ",
    23: "元素チャージ効率",
    26: "元素熟知",
    28: "物理ダメ%",
    29: "炎元素ダメ%",
    30: "雷元素ダメ%",
    31: "水元素ダメ%",
    32: "草元素ダメ%",
    33: "風元素ダメ%",
    34: "岩元素ダメ%",
    35: "氷元素ダメ%",
    40: "回復効果",
    43: "シールド強化",
}

# pos（部位番号） → 日本語スロット名
POS_JP = {1: "花", 2: "羽", 3: "時計", 4: "杯", 5: "冠"}

# ────────────── ユーティリティ ──────────────
def fetch_json(url, headers=None):
    req = urllib.request.Request(
        url,
        headers=headers or {"User-Agent": "genshin-advisor/1.0"}
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode())

def uid_to_server(uid):
    return {
        "1": "cn_gf01", "2": "cn_gf01", "3": "cn_gf01", "4": "cn_gf01",
        "5": "cn_qd01", "6": "os_usa",  "7": "os_euro",
        "8": "os_asia", "9": "os_cht",
    }.get(str(uid)[0], "os_asia")

def score_grade(score):
    if score >= 220: return "SS"
    if score >= 200: return "S"
    if score >= 180: return "A"
    if score >= 100: return "B"
    if score >= 60:  return "C"
    return "D"

# ────────────── allchars (HoYoLAB 全キャラ+聖遺物) ──────────────
def hoyolab_headers(ltoken, ltuid):
    return {
        "Cookie":      f"ltoken_v2={ltoken}; ltuid_v2={ltuid}",
        "User-Agent":  "Mozilla/5.0",
        "Referer":     "https://www.hoyolab.com/",
        "Origin":      "https://www.hoyolab.com",
        "Content-Type": "application/json",
    }

def post_json(url, payload, headers):
    data = json.dumps(payload).encode()
    req  = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode())

def calc_score_hoyolab(sub_list):
    score = 0.0
    for s in sub_list:
        pt  = s.get("property_type")
        raw = str(s.get("value", "0")).replace("%", "")
        try:
            v = float(raw)
        except ValueError:
            continue
        if   pt == 20: score += v * 2      # 会心率
        elif pt == 22: score += v           # 会心ダメージ
        elif pt == 6:  score += v           # 攻撃%
        elif pt == 26: score += v / 4       # 元素熟知
        elif pt == 23: score += v * 0.65   # 元素チャージ効率
        elif pt == 3:  score += v * 0.5    # HP%
        elif pt == 9:  score += v * 0.4    # 防御%
    return round(score, 1)

def cmd_allchars(uid, ltoken, ltuid):
    server  = uid_to_server(uid)
    headers = hoyolab_headers(ltoken, ltuid)

    # ① 全キャラ一覧取得
    try:
        resp = post_json(CHAR_LIST_URL, {"role_id": str(uid), "server": server}, headers)
    except Exception as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        sys.exit(1)

    if resp.get("retcode") != 0:
        print(json.dumps({"error": resp.get("message", "キャラ一覧取得失敗")}, ensure_ascii=False))
        sys.exit(1)

    all_chars = resp["data"]["list"]
    char_ids  = [c["id"] for c in all_chars]
    char_meta = {c["id"]: c for c in all_chars}

    # ② 詳細（聖遺物）を20件ずつバッチ取得
    detail_map = {}
    BATCH = 20
    for i in range(0, len(char_ids), BATCH):
        batch = char_ids[i:i+BATCH]
        try:
            dr = post_json(
                CHAR_DETAIL_URL,
                {"role_id": str(uid), "server": server, "character_ids": batch},
                headers
            )
        except Exception as e:
            print(json.dumps({"error": str(e)}, ensure_ascii=False))
            sys.exit(1)
        if dr.get("retcode") != 0:
            print(json.dumps({"error": dr.get("message", "詳細取得失敗")}, ensure_ascii=False))
            sys.exit(1)
        for c in dr["data"]["list"]:
            detail_map[c["base"]["id"]] = c

    # ③ 整形
    characters = []
    for cid in char_ids:
        meta   = char_meta[cid]
        detail = detail_map.get(cid, {})

        # 聖遺物
        artifacts = []
        for r in detail.get("relics", []):
            main = r.get("main_property", {})
            subs = r.get("sub_property_list", [])
            score = calc_score_hoyolab(subs)
            artifacts.append({
                "slot":       POS_JP.get(r.get("pos"), r.get("pos_name", "?")),
                "set_name":   _t(r.get("set", {}).get("name", "")),
                "level":      r.get("level", 0),
                "main_prop":  PROP_TYPE_JP.get(main.get("property_type"), f"type:{main.get('property_type')}"),
                "main_value": main.get("value", ""),
                "substats": [
                    {
                        "prop":  PROP_TYPE_JP.get(s.get("property_type"), f"type:{s.get('property_type')}"),
                        "value": s.get("value", ""),
                        "times": s.get("times", 0),
                    }
                    for s in subs
                ],
                "score": score,
                "grade": score_grade(score),
            })

        total_score = round(sum(a["score"] for a in artifacts), 1)

        # 武器
        w = detail.get("weapon", {})
        weapon = {
            "name":   _t(w.get("name", "")),
            "level":  w.get("level", 1),
            "refine": w.get("affix_level", 1),
            "rarity": w.get("rarity", 0),
        } if w else None

        # スキルレベル
        skills = [
            {"name": _t(s.get("name", "")), "level": s.get("level", 1)}
            for s in detail.get("skills", [])
        ]

        characters.append({
            "name":          _t(meta.get("name", "")),
            "level":         meta.get("level", 1),
            "element":       meta.get("element", ""),
            "rarity":        meta.get("rarity", 0),
            "constellation": meta.get("actived_constellation_num", 0),
            "weapon":        weapon,
            "skills":        skills,
            "artifacts":     artifacts,
            "total_score":   total_score,
            "total_grade":   score_grade(total_score),
        })

    characters.sort(key=lambda x: x["total_score"], reverse=True)

    result = {
        "total_characters": len(characters),
        "characters":       characters,
        "score_formula":    "会心率×2 + 会心ダメ×1 + 攻撃%×1 + 元素熟知÷4 + チャージ×0.65 + HP%×0.5 + 防御%×0.4",
        "grade_thresholds": "SS≥220 / S≥180 / A≥140 / B≥100 / C≥60 / D<60",
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))

# ────────────── status ──────────────
def cmd_status(uid, ltoken, ltuid):
    server = uid_to_server(uid)
    url    = f"{STATUS_URL}?role_id={uid}&server={server}"
    headers = {
        "Cookie":     f"ltoken_v2={ltoken}; ltuid_v2={ltuid}",
        "User-Agent": "genshin-advisor/1.0",
        "Referer":    "https://www.hoyolab.com/",
        "Origin":     "https://www.hoyolab.com",
    }
    try:
        resp = fetch_json(url, headers=headers)
    except Exception as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        sys.exit(1)

    d = resp.get("data")
    if not d:
        print(json.dumps({"error": resp.get("message", "データ取得失敗")}, ensure_ascii=False))
        sys.exit(1)

    rec_sec  = int(d.get("resin_recovery_time", 0))
    coin_sec = int(d.get("home_coin_recovery_time", 0))

    expeditions = []
    for ex in d.get("expeditions", []):
        rem = int(ex.get("remained_time", 0))
        expeditions.append({
            "status":         "完了済み" if rem == 0 else "派遣中",
            "remained_hours": rem // 3600,
            "remained_mins":  (rem % 3600) // 60,
        })

    result = {
        "resin": {
            "current": d.get("current_resin"),
            "max":     d.get("max_resin"),
            "full_in": f"{rec_sec//3600}時間{(rec_sec%3600)//60}分" if rec_sec > 0 else "満タン",
        },
        "daily": {
            "done":  d.get("finished_task_num"),
            "total": d.get("total_task_num", 4),
        },
        "weekly_boss_discount": d.get("remain_resin_discount_num"),
        "home_coin": {
            "current": d.get("home_coin"),
            "max":     d.get("max_home_coin"),
            "full_in": f"{coin_sec//3600}時間{(coin_sec%3600)//60}分" if coin_sec > 0 else "満タン",
        },
        "expeditions": expeditions,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))

# ────────────── 設定ファイル読み込み ──────────────
def load_config():
    """
    skills/genshin-advisor/.genshin_config から uid / ltoken_v2 / ltuid_v2 を読み込む。
    fetch.py は scripts/ に置かれているため、親ディレクトリを探索する。
    """
    import configparser
    config_paths = [
        _SCRIPT_DIR.parent / ".genshin_config",  # skills/genshin-advisor/.genshin_config
        Path.home() / ".genshin_config",          # ~/.genshin_config（フォールバック）
    ]
    for path in config_paths:
        if path.exists():
            cp = configparser.ConfigParser()
            cp.read(str(path))
            section = cp["genshin"] if "genshin" in cp else {}
            return {
                "uid":      section.get("uid", ""),
                "ltoken":   section.get("ltoken_v2", ""),
                "ltuid":    section.get("ltuid_v2", ""),
            }
    return {"uid": "", "ltoken": "", "ltuid": ""}

# ────────────── エントリポイント ──────────────
def main():
    parser = argparse.ArgumentParser(description="原神データ取得スクリプト（公式HoYoLAB API）")
    parser.add_argument("command", choices=["allchars", "status", "help"])
    parser.add_argument("uid", nargs="?", type=int)
    parser.add_argument("--ltoken", default="")
    parser.add_argument("--ltuid",  default="")
    args = parser.parse_args()

    if args.command == "help":
        print("使い方:")
        print("  python3 fetch.py allchars [UID] [--ltoken <ltoken_v2>] [--ltuid <ltuid_v2>]")
        print("  python3 fetch.py status   [UID] [--ltoken <ltoken_v2>] [--ltuid <ltuid_v2>]")
        print("  UID・Cookie省略時は .genshin_config から自動読み込み")
        return

    # 設定ファイルから値を補完（引数で渡された値を優先）
    cfg = load_config()
    uid    = args.uid    or (int(cfg["uid"])    if cfg["uid"]    else None)
    ltoken = args.ltoken or cfg["ltoken"]
    ltuid  = args.ltuid  or cfg["ltuid"]

    if not uid:
        print(json.dumps({"error": "UID が指定されておらず、.genshin_config にも見つかりません"}, ensure_ascii=False))
        sys.exit(1)

    if not ltoken or not ltuid:
        print(json.dumps({"error": "--ltoken / --ltuid が指定されておらず、.genshin_config にも見つかりません"}, ensure_ascii=False))
        sys.exit(1)

    if args.command == "allchars":
        cmd_allchars(uid, ltoken, ltuid)
    elif args.command == "status":
        cmd_status(uid, ltoken, ltuid)

if __name__ == "__main__":
    main()
