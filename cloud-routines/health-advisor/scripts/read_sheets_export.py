#!/usr/bin/env python3
"""Driveコネクタでxlsxエクスポートしたスプレッドシートから、
「食事」シートとLifeGraphシートの行を取得するスクリプト（記録フロー・レポート作成フロー共用）

Usage:
    python3 read_sheets_export.py --input <エクスポート結果ファイル> --date 2026-10-25
    python3 read_sheets_export.py --mode record --input <エクスポート結果ファイル> --date 2026-10-25

--input には以下のどちらかを渡す:
    - Driveコネクタの download_file_content の結果が保存されたJSONファイル
      （{"content": "<base64>", ...} 形式）
    - xlsxファイルそのもの

--mode report（既定）: --date はレポート作成日。対象期間は前日を起点に直近7日分（date-7 〜 date-1）。
    あわせて、過去の週（同じ7日区切り）の週次サマリーを「食事」シート・LifeGraphシートから集計して返す。
--mode record: --date は記録対象日（前日）。対象日の入力状況（target_status）と、
    補完が必要な行（摂取カロリー・歩数・睡眠時間・たんぱく質・脂質・炭水化物のいずれかが空欄、
    または歩数・睡眠時間が「取得できませんでした」）を、Sheetsコネクタの update_values に渡す
    書き込み範囲（write_range）付きで返す。PFCの補完は直近 PFC_BACKFILL_DAYS 日の行だけを対象にし、
    摂取カロリーは入っていてPFCだけ空欄の行（過去分のバックフィル）は1回 PFC_BACKFILL_LIMIT 行までに絞る。
シート名はCONFIG.mdの meals.sheet_name / lifegraph.sheet_name を使う。
xlsxの解析は標準ライブラリのみで行う（openpyxl・PyYAML不要）。

出力の daily は日ごとの数値化済み指標:
    calorie_kcal: 「食事」シートの摂取カロリー
    protein_g / fat_g / carb_g: 「食事」シートのたんぱく質・脂質・炭水化物（g）
    protein_pct / fat_pct / carb_pct: その日のPFCエネルギー比率（3つそろった日のみ）
    steps / sleep_hours: 「食事」シートの値、空欄・「取得できませんでした」の日はLifeGraphの値
    *_source: 値の出どころ（"meals" / "lifegraph" / null=欠損）

report モードの週次サマリー:
    current_summary: 今週（対象期間）の週次サマリー。complete=false なら欠けている指標がある
    summaries: 過去の週の週次サマリー（古い順、全指標がそろった週のみ、最大 SUMMARY_WEEKS 週）
    いずれも report_date / period_start / period_end / days / calorie_kcal / protein_pct / fat_pct /
    carb_pct / steps / sleep_hours を持つ（build_artifact.py の --history にこの出力をそのまま渡す）
"""

import argparse
import base64
import io
import json
import math
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from datetime import date, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from config_parser import get_resource_config

SUMMARY_WEEKS = 12  # summaries に集計する過去週数（build_artifact.py の --weeks 既定8より多め）
PFC_BACKFILL_DAYS = 56  # 記録フローでPFCを補完する対象期間（対象日を含む直近8週）
PFC_BACKFILL_LIMIT = 14  # 摂取カロリーは入っていてPFCだけ空欄の行を、1回に補完する最大行数
PERIOD_DAYS = 7  # レポート対象期間（WORKFLOW-REPORT.md Phase 1の「直近7日分」）
EXCEL_EPOCH = date(1899, 12, 30)  # Excelシリアル値の基準日

NS = {
    "m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "pr": "http://schemas.openxmlformats.org/package/2006/relationships",
}
M = "{%s}" % NS["m"]


def output_json(data):
    print(json.dumps(data, ensure_ascii=False, indent=2))


def error_exit(message):
    output_json({"success": False, "error": message})
    sys.exit(1)


def parse_args():
    parser = argparse.ArgumentParser(description="xlsxエクスポートから食事・LifeGraphの対象期間の行を取得")
    parser.add_argument("--input", required=True, help="download_file_contentの結果JSON、またはxlsxファイルのパス")
    parser.add_argument("--date", required=True, help="report: レポート作成日 / record: 記録対象日 (YYYY-MM-DD)")
    parser.add_argument("--mode", choices=["report", "record"], default="report")
    return parser.parse_args()


def load_xlsx_bytes(path: Path) -> bytes:
    raw = path.read_bytes()
    if raw[:2] == b"PK":  # xlsx（zip）そのもの
        return raw
    try:
        content = json.loads(raw)["content"]
    except (ValueError, KeyError, TypeError):
        raise ValueError("入力がxlsxでも、contentキーを持つJSONでもありません")
    return base64.b64decode(content)


def col_index(cell_ref: str) -> int:
    """'C12' -> 2（0始まりの列番号）"""
    letters = re.match(r"[A-Z]+", cell_ref).group(0)
    idx = 0
    for ch in letters:
        idx = idx * 26 + (ord(ch) - ord("A") + 1)
    return idx - 1


def text_of(elem) -> str:
    """共有文字列・インライン文字列のテキスト（ふりがな rPh は除外）"""
    parts = [t.text or "" for t in elem.findall(f"{M}t")]
    for run in elem.findall(f"{M}r"):
        parts.extend(t.text or "" for t in run.findall(f"{M}t"))
    return "".join(parts)


def read_sheets(xlsx: bytes, names: set) -> dict:
    """指定シート名の全行を {シート名: [[セル値, ...], ...]} で返す。
    空行は詰めて返すため、シート上の行番号は result["__row_numbers__"][シート名] に並べて返す"""
    z = zipfile.ZipFile(io.BytesIO(xlsx))
    shared = []
    if "xl/sharedStrings.xml" in z.namelist():
        root = ET.fromstring(z.read("xl/sharedStrings.xml"))
        shared = [text_of(si) for si in root.findall("m:si", NS)]

    rels = {
        r.get("Id"): r.get("Target")
        for r in ET.fromstring(z.read("xl/_rels/workbook.xml.rels")).findall("pr:Relationship", NS)
    }
    workbook = ET.fromstring(z.read("xl/workbook.xml"))
    result = {"__all__": [s.get("name") for s in workbook.find("m:sheets", NS)], "__row_numbers__": {}}
    for sheet in workbook.find("m:sheets", NS):
        name = sheet.get("name")
        if name not in names:
            continue
        target = rels[sheet.get("{%s}id" % NS["r"])]
        path = target.lstrip("/") if target.startswith("/") else f"xl/{target}"
        rows = []
        row_numbers = []
        for row in ET.fromstring(z.read(path)).iter(f"{M}row"):
            values = {}
            for c in row.findall(f"{M}c"):
                t = c.get("t")
                v = c.find(f"{M}v")
                if t == "s" and v is not None:
                    val = shared[int(v.text)]
                elif t == "inlineStr":
                    val = text_of(c.find(f"{M}is"))
                else:
                    val = v.text if v is not None else ""
                values[col_index(c.get("r"))] = val
            if values:
                rows.append([values.get(i, "") for i in range(max(values) + 1)])
                row_numbers.append(int(row.get("r")))
        result[name] = rows
        result["__row_numbers__"][name] = row_numbers
    return result


def to_date(value: str):
    """A列の値（Excelシリアル値 or YYYY/MM/DD）を date に変換。変換できなければ None"""
    value = (value or "").strip()
    try:
        return EXCEL_EPOCH + timedelta(days=int(float(value)))
    except ValueError:
        pass
    for fmt in ("%Y/%m/%d", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None


def to_value(value: str):
    """数値文字列は数値に（整数値ならint）、それ以外は文字列のまま"""
    try:
        num = float(value)
    except ValueError:
        return value
    if not math.isfinite(num):  # "NaN" 等は文字列のまま（不正なJSONを出さない）
        return value
    return int(num) if num.is_integer() else num


def parse_number(value):
    """'1530kcal' / '1952歩' / '10.0時間' / 5127 から数値を取り出す。取り出せなければ None"""
    if isinstance(value, (int, float)):
        return value
    match = re.search(r"\d+(?:\.\d+)?", str(value or ""))
    return float(match.group(0)) if match else None


def pfc_ratio(protein, fat, carb):
    """PFC（g）からエネルギー比率（%、小数1桁）を返す（たんぱく質・炭水化物4kcal/g、脂質9kcal/g）"""
    if None in (protein, fat, carb):
        return None
    kcal = (protein * 4, fat * 9, carb * 4)
    total = sum(kcal)
    if not total:
        return None
    return tuple(round(k / total * 100, 1) for k in kcal)


def build_daily(meals: list, lifegraph: list) -> list:
    """日ごとにカロリー・PFC・歩数・睡眠時間を数値化する（「食事」シート優先、歩数・睡眠の欠損はLifeGraphで補完）"""
    lg_by_date = {r["date"]: r for r in lifegraph}
    meals_by_date = {r["date"]: r for r in meals}
    daily = []
    for d in sorted(set(meals_by_date) | set(lg_by_date)):
        m = meals_by_date.get(d, {})
        lg = lg_by_date.get(d, {})
        lg_sleep_key = next((k for k in lg if "睡眠" in k), None)
        row = {"date": d, "calorie_kcal": parse_number(m.get("摂取カロリー"))}
        for name, col in zip(("protein_g", "fat_g", "carb_g"), PFC_COLUMNS):
            row[name] = parse_number(m.get(col))
        ratio = pfc_ratio(row["protein_g"], row["fat_g"], row["carb_g"])
        for i, name in enumerate(("protein_pct", "fat_pct", "carb_pct")):
            row[name] = ratio[i] if ratio else None
        for name, meals_key, lg_key in (("steps", "歩数", "歩数"), ("sleep_hours", "睡眠時間", lg_sleep_key)):
            value, source = parse_number(m.get(meals_key)), "meals"
            if value is None:
                value, source = parse_number(lg.get(lg_key)) if lg_key else None, "lifegraph"
            row[name] = value
            row[f"{name}_source"] = source if value is not None else None
        daily.append(row)
    return daily


def mean(values):
    values = [v for v in values if v is not None]
    return sum(values) / len(values) if values else None


def weekly_summary(daily: list, report_date: date) -> dict:
    """report_date のレポートの対象期間（report_date-7 〜 report_date-1）の週次サマリーを集計する"""
    start = (report_date - timedelta(days=PERIOD_DAYS)).isoformat()
    end = (report_date - timedelta(days=1)).isoformat()
    rows = [r for r in daily if start <= r["date"] <= end]
    metrics = ("calorie_kcal", "protein_g", "fat_g", "carb_g", "steps", "sleep_hours")
    has_data = [r["date"] for r in rows if any(r[k] is not None for k in metrics)]
    pfc_days = [r for r in rows if None not in (r["protein_g"], r["fat_g"], r["carb_g"])]
    ratio = pfc_ratio(*(sum(r[k] for r in pfc_days) for k in ("protein_g", "fat_g", "carb_g"))) if pfc_days else None
    cal, steps, sleep = (mean(r[k] for r in rows) for k in ("calorie_kcal", "steps", "sleep_hours"))
    summary = {
        "report_date": report_date.isoformat(),
        "period_start": min(has_data) if has_data else start,
        "period_end": max(has_data) if has_data else end,
        "days": sum(1 for r in rows if r["calorie_kcal"] is not None),
        "pfc_days": len(pfc_days),
        "calorie_kcal": round(cal) if cal is not None else None,
        "protein_pct": ratio[0] if ratio else None,
        "fat_pct": ratio[1] if ratio else None,
        "carb_pct": ratio[2] if ratio else None,
        "steps": round(steps) if steps is not None else None,
        "sleep_hours": round(sleep, 1) if sleep is not None else None,
    }
    summary["complete"] = None not in (summary["calorie_kcal"], summary["protein_pct"],
                                       summary["steps"], summary["sleep_hours"])
    return summary


def normalize_header(header: str) -> str:
    """ヘッダーの改行・前後空白を除去（例: '睡眠 \\n#sleep' -> '睡眠 #sleep'）"""
    return " ".join(str(header).split())


def rows_in_period(rows: list, start: date, end: date, row_numbers: list = None) -> list:
    """1行目をヘッダーとし、A列の日付が期間内の行を {ヘッダー: 値} の辞書にして返す。
    row_numbers を渡すと、シート上の行番号を "_row" に入れる（記録フローの書き込み範囲に使う）"""
    if not rows:
        return []
    headers = [normalize_header(h) for h in rows[0]]
    records = []
    for idx, row in enumerate(rows[1:], start=1):
        d = to_date(row[0] if row else "")
        if d is None or not (start <= d <= end):
            continue
        record = {"date": d.isoformat()}
        if row_numbers:
            record["_row"] = row_numbers[idx]
        for i, header in enumerate(headers[1:], start=1):
            if header:
                record[header] = to_value(row[i]) if i < len(row) else ""
        records.append(record)
    return records


PFC_COLUMNS = ("たんぱく質", "脂質", "炭水化物")
FILL_COLUMNS = ("摂取カロリー", "歩数", "睡眠時間") + PFC_COLUMNS  # 記録フローで補完する列（この順で隣接）
ESTIMATE_COLUMNS = ("摂取カロリー",) + PFC_COLUMNS  # 食事内容から見積もる列
MEAL_COLUMNS = ("朝食", "昼食", "夕食")
UNAVAILABLE = "取得できませんでした"


def lifegraph_texts(lg: dict) -> dict:
    """LifeGraphの1行から、「食事」シートに書く形式の歩数・睡眠時間を返す（0・欠損はNone）"""
    sleep_key = next((k for k in lg if "睡眠" in k), None)
    steps = parse_number(lg.get("歩数"))
    sleep = parse_number(lg.get(sleep_key)) if sleep_key else None
    return {
        "歩数": f"{int(round(steps))}歩" if steps else None,
        "睡眠時間": f"{sleep:.1f}時間" if sleep else None,
    }


def column_letter(index: int) -> str:
    """0始まりの列番号をA1表記の列名にする（0 -> A）"""
    letters = ""
    index += 1
    while index:
        index, rem = divmod(index - 1, 26)
        letters = chr(ord("A") + rem) + letters
    return letters


def fill_columns_span(header_row: list) -> tuple:
    """FILL_COLUMNSの列名（A1表記）の先頭・末尾を返す。書き込みは1行1範囲で行うため隣接している必要がある"""
    headers = [normalize_header(h) for h in header_row]
    missing = [c for c in FILL_COLUMNS if c not in headers]
    if missing:
        error_exit(f"「食事」シートにヘッダーがありません: {', '.join(missing)}")
    idx = [headers.index(c) for c in FILL_COLUMNS]
    if idx != list(range(idx[0], idx[0] + len(idx))):
        error_exit(f"{'・'.join(FILL_COLUMNS)} の列が隣接していません（CONFIG.mdの列構成を確認）")
    return column_letter(idx[0]), column_letter(idx[-1])


def quote_sheet(name: str) -> str:
    """A1表記用にシート名を引用する（空白・記号を含む名前でも範囲が壊れないように）"""
    return "'" + name.replace("'", "''") + "'"


def meals_complete(m: dict) -> bool:
    return all(str(m.get(c, "")).strip() for c in MEAL_COLUMNS)


def build_record_status(meals: list, lifegraph: list, target: date, sheet_name: str, span: tuple) -> dict:
    """記録フロー用: 対象日の入力状況と、補完が必要な行の一覧（書き込み範囲付き）を返す"""
    lg_by_date = {r["date"]: lifegraph_texts(r) for r in lifegraph}
    sheet = quote_sheet(sheet_name)
    pfc_from = (target - timedelta(days=PFC_BACKFILL_DAYS - 1)).isoformat()
    candidates = []
    for m in meals:
        missing = [c for c in FILL_COLUMNS if str(m.get(c, "")).strip() in ("", UNAVAILABLE)]
        if m["date"] < pfc_from:
            missing = [c for c in missing if c not in PFC_COLUMNS]
        if missing:
            candidates.append((m, missing))

    # 摂取カロリーは入っていてPFCだけ空欄の行（過去分のバックフィル）は、新しい日から PFC_BACKFILL_LIMIT 行まで
    pfc_only = [m["date"] for m, missing in candidates
                if "摂取カロリー" not in missing and any(c in missing for c in PFC_COLUMNS) and meals_complete(m)]
    deferred = set(sorted(pfc_only, reverse=True)[PFC_BACKFILL_LIMIT:])

    backfill = []
    for m, missing in candidates:
        if m["date"] in deferred:
            missing = [c for c in missing if c not in PFC_COLUMNS]
            if not missing:
                continue
        backfill.append({
            "date": m["date"],
            "write_range": f"{sheet}!{span[0]}{m['_row']}:{span[1]}{m['_row']}",
            "missing": missing,
            "needs_estimate": [c for c in ESTIMATE_COLUMNS if c in missing],
            "meals": {c: m.get(c, "") for c in MEAL_COLUMNS},
            "meals_complete": meals_complete(m),
            "lifegraph": lg_by_date.get(m["date"], {"歩数": None, "睡眠時間": None}),
        })
    target_key = target.isoformat()
    target_row = next((m for m in meals if m["date"] == target_key), None)
    if target_row is None:
        target_status = "missing"
    else:
        target_status = "complete" if meals_complete(target_row) else "partial"
    return {
        "target_date": target_key,
        "target_status": target_status,
        "write_columns": list(FILL_COLUMNS),
        "backfill": backfill,
        "pfc_backfill_remaining": len(deferred),
    }


def main():
    args = parse_args()
    try:
        report_date = datetime.strptime(args.date, "%Y-%m-%d").date()
    except ValueError:
        error_exit(f"日付の形式が不正です（YYYY-MM-DDで指定してください）: {args.date}")

    input_path = Path(args.input).expanduser()
    if not input_path.exists():
        error_exit(f"入力ファイルが見つかりません: {input_path}")

    try:
        meals_sheet = get_resource_config("meals")["sheet_name"]
        lifegraph_sheet = get_resource_config("lifegraph")["sheet_name"]
    except Exception as e:
        error_exit(f"CONFIG.mdの読み込みに失敗しました: {e}")

    try:
        sheets = read_sheets(load_xlsx_bytes(input_path), {meals_sheet, lifegraph_sheet})
    except (ValueError, zipfile.BadZipFile, KeyError, ET.ParseError) as e:
        error_exit(f"xlsxの解析に失敗しました: {e}")

    missing = [n for n in (meals_sheet, lifegraph_sheet) if n not in sheets]
    if missing:
        output_json({
            "success": False,
            "error": f"シートが見つかりません: {', '.join(missing)}（CONFIG.mdのsheet_nameを確認）",
            "availableSheets": sheets["__all__"],
        })
        sys.exit(1)

    if args.mode == "record":
        meals = rows_in_period(sheets[meals_sheet], date.min, report_date, sheets["__row_numbers__"][meals_sheet])
        lifegraph = rows_in_period(sheets[lifegraph_sheet], date.min, report_date)
        if not sheets[meals_sheet]:
            error_exit(f"「{meals_sheet}」シートが空です（1行目にヘッダーが必要）")
        span = fill_columns_span(sheets[meals_sheet][0])
        status = build_record_status(meals, lifegraph, report_date, meals_sheet, span)
        output_json({"success": True, "mode": "record", **status})
        return

    start = report_date - timedelta(days=PERIOD_DAYS)
    end = report_date - timedelta(days=1)
    history_start = report_date - timedelta(days=PERIOD_DAYS * (SUMMARY_WEEKS + 1))
    all_daily = build_daily(rows_in_period(sheets[meals_sheet], history_start, end),
                            rows_in_period(sheets[lifegraph_sheet], history_start, end))
    meals = rows_in_period(sheets[meals_sheet], start, end)
    lifegraph = rows_in_period(sheets[lifegraph_sheet], start, end)

    current = weekly_summary(all_daily, report_date)
    summaries = []
    for k in range(SUMMARY_WEEKS, 0, -1):
        s = weekly_summary(all_daily, report_date - timedelta(days=PERIOD_DAYS * k))
        if s["complete"]:
            summaries.append(s)
    warnings = []
    if not current["complete"]:
        lacking = [k for k in ("calorie_kcal", "protein_pct", "steps", "sleep_hours") if current[k] is None]
        warnings.append(f"今週の週次サマリーに欠けている指標があります: {', '.join(lacking)}")

    output_json({
        "success": True,
        "period_start": start.isoformat(),
        "period_end": end.isoformat(),
        "daily": [r for r in all_daily if r["date"] >= start.isoformat()],
        "meals": meals,
        "lifegraph": lifegraph,
        "current_summary": current,
        "summaries": summaries,
        "warnings": warnings,
    })

if __name__ == "__main__":
    main()
