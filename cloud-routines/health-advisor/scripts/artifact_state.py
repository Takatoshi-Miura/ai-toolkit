#!/usr/bin/env python3
"""「からだ週報」アーティファクトの状態（号の一覧・フィードバック履歴・ガイド更新候補）を読み込み・検証・追記する

状態はアーティファクトの data/state.json（Artifactツールの read_file で取得）に
{"weeks": [{report_date, period_start, period_end, days, ..., path}], "feedback": [{date, issue, applied}],
 "guide_candidates": [{date, target, proposal, source, resolved}]}
の形で置く。同じ内容が index.html の <script type="application/json" id="health-advisor-state"> にも埋め込まれている。

Usage:
    # 読み込み・検証（state.json、index.htmlのHTML、またはどちらかのJSON部分だけを書き出したファイル）
    python3 artifact_state.py load --input <ファイル> --out <WORK>/state.json

    # 状態が取れない初回だけ: 空の状態を作る
    python3 artifact_state.py init --out <WORK>/state.json

    # フィードバックを1件追記する（指摘・反映は改行を含んでよい）
    python3 artifact_state.py add-feedback --input <WORK>/state.json --date 2026-11-29 \
        --issue "<指摘内容>" --applied "<反映内容>" --out <WORK>/state.json

    # 参照ガイド（references/）の更新候補を1件追記する
    python3 artifact_state.py add-candidate --input <WORK>/state.json --date 2026-11-29 \
        --target "references/exercise-guide.md「歩数の目安」" --proposal "<修正案>" --source "<出典URL>" \
        --out <WORK>/state.json

    # ガイド更新候補を反映済みにする（--date と --target が一致するもの）
    python3 artifact_state.py resolve-candidate --input <WORK>/state.json --date 2026-11-29 \
        --target "<add-candidate の --target と同じ文字列>" --out <WORK>/state.json

出力: {"success": true, "source": <読み取り元の形式>, "weeks": <号数>, "feedback": <件数>,
       "open_candidates": [<未反映のガイド更新候補>], "out": <パス>}
"""

import argparse
import html
import json
import re
import sys
from pathlib import Path

SCRIPT_ID = "health-advisor-state"  # build_artifact.py の STATE_SCRIPT_ID と合わせる
LEGACY_FEEDBACK_ID = "health-advisor-feedback"  # 移行前（フィードバックのみ埋め込み）の版


def fail(message):
    print(json.dumps({"success": False, "error": message}, ensure_ascii=False))
    sys.exit(1)


def script_json(text, script_id):
    pattern = rf'<script[^>]*id=["\']{script_id}["\'][^>]*>(.*?)</script>'
    match = re.search(pattern, text, re.S) or re.search(pattern, html.unescape(text), re.S)
    if not match:
        return None
    try:
        return json.loads(match.group(1).strip() or "null")
    except json.JSONDecodeError as e:
        fail(f"埋め込まれた状態JSONが壊れています: {e}")


def parse(text):
    """入力テキストから状態を取り出し、(状態, 読み取り元の形式) を返す"""
    stripped = text.lstrip()
    if stripped.startswith(("{", "[")):
        try:
            data = json.loads(stripped)
        except json.JSONDecodeError as e:
            fail(f"状態JSONが壊れています: {e}")
        if isinstance(data, list):
            return {"weeks": [], "feedback": data}, "feedback-array"
        return data, "state-json"
    data = script_json(text, SCRIPT_ID)
    if data is not None:
        return data, "html"
    legacy = script_json(text, LEGACY_FEEDBACK_ID)
    if legacy is not None:
        return {"weeks": [], "feedback": legacy}, "legacy-html"
    fail("状態が見つかりません（data/state.json か、からだ週報のHTMLを渡してください）")


def validate(state):
    if not isinstance(state, dict):
        fail("状態はJSONオブジェクトにしてください")
    weeks, feedback = state.get("weeks", []), state.get("feedback", [])
    if not isinstance(weeks, list) or not all(isinstance(w, dict) and w.get("report_date") for w in weeks):
        fail("weeks は report_date を持つオブジェクトの配列にしてください")
    if not isinstance(feedback, list) or not all(isinstance(f, dict) and f.get("date") for f in feedback):
        fail("feedback は {date, issue, applied} の配列にしてください")
    candidates = state.get("guide_candidates", [])
    if not isinstance(candidates, list) or not all(isinstance(c, dict) and c.get("date") and c.get("target")
                                                   for c in candidates):
        fail("guide_candidates は {date, target, proposal, source, resolved} の配列にしてください")
    return {"weeks": sorted(weeks, key=lambda w: w["report_date"]),
            "feedback": sorted(feedback, key=lambda f: str(f["date"])),
            "guide_candidates": sorted(candidates, key=lambda c: str(c["date"]))}


def save(state, out, source):
    Path(out).expanduser().write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"success": True, "source": source, "weeks": len(state["weeks"]),
                      "feedback": len(state["feedback"]),
                      "open_candidates": [c for c in state["guide_candidates"] if not c.get("resolved")],
                      "out": str(Path(out).expanduser())}, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description="からだ週報の状態を読み書きする")
    sub = parser.add_subparsers(dest="command", required=True)
    p_load = sub.add_parser("load", help="読み込み・検証して書き出す")
    p_load.add_argument("--input", required=True)
    p_load.add_argument("--out", required=True)
    p_init = sub.add_parser("init", help="空の状態を作る")
    p_init.add_argument("--out", required=True)
    p_add = sub.add_parser("add-feedback", help="フィードバックを1件追記する")
    p_add.add_argument("--input", required=True)
    p_add.add_argument("--date", required=True)
    p_add.add_argument("--issue", required=True)
    p_add.add_argument("--applied", required=True)
    p_add.add_argument("--out", required=True)
    p_cand = sub.add_parser("add-candidate", help="ガイド更新候補を1件追記する")
    p_cand.add_argument("--input", required=True)
    p_cand.add_argument("--date", required=True)
    p_cand.add_argument("--target", required=True)
    p_cand.add_argument("--proposal", required=True)
    p_cand.add_argument("--source", default="")
    p_cand.add_argument("--out", required=True)
    p_res = sub.add_parser("resolve-candidate", help="ガイド更新候補を反映済みにする")
    p_res.add_argument("--input", required=True)
    p_res.add_argument("--date", required=True)
    p_res.add_argument("--target", required=True)
    p_res.add_argument("--out", required=True)
    args = parser.parse_args()

    if args.command == "init":
        save({"weeks": [], "feedback": [], "guide_candidates": []}, args.out, "init")
        return
    path = Path(args.input).expanduser()
    if not path.exists():
        fail(f"入力ファイルが見つかりません: {path}")
    state, source = parse(path.read_text(encoding="utf-8", errors="replace"))
    state = validate(state)
    if args.command == "add-feedback":
        state["feedback"].append({"date": args.date, "issue": args.issue.strip(), "applied": args.applied.strip()})
        source = "add-feedback"
    elif args.command == "add-candidate":
        state["guide_candidates"].append({"date": args.date, "target": args.target.strip(),
                                          "proposal": args.proposal.strip(), "source": args.source.strip(),
                                          "resolved": False})
        source = "add-candidate"
    elif args.command == "resolve-candidate":
        hits = [c for c in state["guide_candidates"]
                if str(c["date"]) == args.date and c["target"] == args.target.strip()]
        if not hits:
            fail(f"該当するガイド更新候補がありません: {args.date} {args.target}")
        for c in hits:
            c["resolved"] = True
        source = "resolve-candidate"
    save(state, args.out, source)


if __name__ == "__main__":
    main()
