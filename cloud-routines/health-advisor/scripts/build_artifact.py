#!/usr/bin/env python3
"""週次レポートmdと週次サマリーから、アーティファクト「からだ週報」のファイル一式を生成する

Usage:
    python3 build_artifact.py --date 2026-10-18 --report <レポートmd> --history <read_sheets_export.pyの出力JSON> \
        [--state <data/state.json>] [--current <今週のサマリーJSON>] [--out-dir <出力先>] [--weeks 8]

入力:
    --report    今週のレポート本文（md）
    --history   read_sheets_export.py（reportモード）の出力JSON。summaries（過去の週）と
                current_summary（今週）を使う。サマリーの配列JSONも可
    --current   今週の週次サマリー（JSONオブジェクト1件）。省略時は --history の current_summary を使う
    --state     公開中のアーティファクトの data/state.json（号の一覧・フィードバック履歴・ガイド更新候補。artifact_state.py で検証済みのもの）。
                省略時は空（初回）として扱う
    assets/artifact-template.html 固定テンプレート
出力（--out-dir、既定 ./artifact。スキルディレクトリには書き込まない）:
    index.html              最新号のページ（Artifactツールの file_path に渡す）。過去の号へのリンク・フィードバック履歴・未反映のガイド更新候補つき
    weeks/<date>.html       今週号の単独ページ（過去の号として残る。files で publish する）
    data/state.json         号の一覧（今週号を追加済み）・フィードバック履歴・ガイド更新候補（files で publish する）

指標が欠けている週（値がnull）は、KPIを「データなし」、グラフはその週の点を省いて描く。
依存: 標準ライブラリのみ。markdown パッケージがあれば使い、なければ内蔵の簡易変換を使う
"""

import argparse
import datetime
import html
import json
import os
import re
import sys

try:
    import markdown
except ImportError:
    markdown = None

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE = os.path.join(SKILL_DIR, "assets", "artifact-template.html")

# 判定基準（references/ 配下のガイドの目安。ガイドを更新したらここも合わせる）
CAL_TARGET = (2350, 2750)  # nutrition-guide.md「推定エネルギー必要量」: 30〜49歳男性・身体活動レベル低い〜ふつう
CAL_WARN_MIN = 2050        # 独自区分: 目安下限から300kcal以内は「やや不足」（nutrition-guide.mdに記載）
P_RANGE = (13, 20)         # nutrition-guide.md「PFCバランス」
F_RANGE = (20, 30)
C_RANGE = (50, 65)
STEPS_TARGET = 8000        # exercise-guide.md: 1日約8,000歩
STEPS_WARN_MIN = 6000      # 独自区分: 目安の75%以上は「やや不足」（exercise-guide.mdに記載）
SLEEP_MIN = 6              # sleep-guide.md: 6時間以上（上限なし）
# PFCは目安の範囲外を「下限未満」(warn)・「上限超過」(bad)で区別する（独自区分、nutrition-guide.mdに記載）
REQUIRED_KEYS = ("report_date", "period_start", "period_end", "days")
METRIC_KEYS = ("calorie_kcal", "protein_pct", "fat_pct", "carb_pct", "steps", "sleep_hours")
STATE_SCRIPT_ID = "health-advisor-state"  # artifact_state.py と合わせる


def parse_args():
    p = argparse.ArgumentParser(description="アーティファクト用HTMLを生成")
    p.add_argument("--date", required=True, help="レポート作成日 YYYY-MM-DD")
    p.add_argument("--report", required=True, help="今週のレポートmdのパス")
    p.add_argument("--history", required=True, help="read_sheets_export.pyの出力JSON（または週次サマリーの配列JSON）のパス")
    p.add_argument("--current", help="今週の週次サマリーJSONのパス（省略時は --history の current_summary）")
    p.add_argument("--state", help="公開中のアーティファクトの data/state.json のパス（省略時は空）")
    p.add_argument("--out-dir", default="artifact", help="出力先ディレクトリ（既定: ./artifact）")
    p.add_argument("--weeks", type=int, default=8, help="週次推移に載せる週数（デフォルト8）")
    return p.parse_args()


def jp_date(iso, with_year=True):
    y, m, d = iso.split("-")
    return f"{y}年{int(m)}月{int(d)}日" if with_year else f"{int(m)}月{int(d)}日"


def short_date(iso):
    _, m, d = iso.split("-")
    return f"{int(m)}/{int(d)}"


def fail(msg):
    print(json.dumps({"success": False, "error": msg}, ensure_ascii=False))
    sys.exit(1)


def read_json(path, label):
    if not os.path.exists(path):
        fail(f"{label} が見つかりません: {path}")
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        fail(f"{label} のJSONが壊れています: {e}")


def check_summary(s, label):
    if not isinstance(s, dict):
        fail(f"{label} がJSONオブジェクトではありません")
    missing = [k for k in REQUIRED_KEYS if s.get(k) in ("", None)] + [k for k in METRIC_KEYS if k not in s]
    if missing:
        fail(f"{label} に必須キーがありません: {', '.join(missing)}")
    return s


ISSUE_MATCH_DAYS = 3  # シートから集計した週と、公開済みの号を同じ週とみなす日数差


def load_summaries(date, weeks, current_path, history_path, issues=()):
    """過去分と今週分（--current または current_summary）を結合し、古い順に直近 weeks 件を返す。
    過去分は公開済みの号（--state の weeks）を優先し、号のない週だけ --history の summaries（シートから集計）で埋める"""
    data = read_json(history_path, "--history")
    current = None
    if isinstance(data, dict):
        if "summaries" not in data:
            fail("--history に summaries キーがありません（read_sheets_export.py の report モード出力を渡す）")
        current = data.get("current_summary")
        data = data["summaries"]
    if current_path:
        current = read_json(current_path, "--current")
    if current is None:
        fail("今週のサマリーがありません（--current を渡すか、--history に current_summary を含める）")
    current = check_summary(current, "今週のサマリー")
    if current["report_date"] != date:
        fail(f"今週のサマリーの report_date（{current['report_date']}）が --date（{date}）と一致しません")
    history = [check_summary(s, f"--history の {s.get('report_date', '?') if isinstance(s, dict) else '?'}")
               for s in data]
    to_date = lambda d: datetime.date.fromisoformat(d)
    items = {w["report_date"]: w for w in issues if w["report_date"] < date
             and all(w.get(k) is not None for k in METRIC_KEYS)}
    for s in history:
        if s["report_date"] >= date:
            continue
        near = any(abs((to_date(s["report_date"]) - to_date(d)).days) <= ISSUE_MATCH_DAYS for d in items)
        if not near:
            items[s["report_date"]] = s
    items[date] = current
    return [items[k] for k in sorted(items)][-weeks:]


def load_state(path):
    """号の一覧（weeks）・フィードバック履歴（feedback）・ガイド更新候補（guide_candidates）を読む。省略時は空"""
    if not path:
        return {"weeks": [], "feedback": [], "guide_candidates": []}
    data = read_json(path, "--state")
    if not isinstance(data, dict) or not isinstance(data.get("weeks", []), list) \
            or not isinstance(data.get("feedback", []), list) \
            or not isinstance(data.get("guide_candidates", []), list):
        fail("--state は {\"weeks\": [...], \"feedback\": [...]} の形式にしてください（artifact_state.py の出力）")
    return {"weeks": data.get("weeks", []), "feedback": data.get("feedback", []),
            "guide_candidates": data.get("guide_candidates", [])}


# ---- 判定 ----

def status_cal(v):
    if v > CAL_TARGET[1]:
        return "warn", "上限超過"
    if v >= CAL_TARGET[0]:
        return "good", "目安内"
    if v >= CAL_WARN_MIN:
        return "warn", "やや不足"
    return "bad", "不足"


def status_range(v, lo, hi):
    if lo <= v <= hi:
        return "good", "目安内"
    return ("warn", "下限未満") if v < lo else ("bad", "上限超過")


def status_steps(v):
    if v >= STEPS_TARGET:
        return "good", "目安達成"
    if v >= STEPS_WARN_MIN:
        return "warn", "やや不足"
    return "bad", "不足"


def status_sleep(v):
    return ("good", "目安内") if v >= SLEEP_MIN else ("bad", "不足")


NO_DATA = ("warn", "データなし")


def chip(st):
    cls, text = st
    return f'<span class="chip {cls}">{html.escape(text)}</span>'


def delta_text(cur, prev, key, unit, digits=0):
    if cur[key] is None:
        return "今週データなし"
    if prev is None or prev[key] is None:
        return "前週データなし"
    d = cur[key] - prev[key]
    sign = "+" if d > 0 else ("±" if d == 0 else "−")
    val = f"{abs(d):,.{digits}f}"
    return f"前週比 <span class=\"num\">{sign}{val}</span>{unit}"


# ---- 部品 ----

def build_kpis(cur, prev):
    def st(func, key, *a):
        return func(cur[key], *a) if cur[key] is not None else NO_DATA

    def val(key, fmt):
        return fmt(cur[key]) if cur[key] is not None else "—"

    if cur["protein_pct"] is None:
        pfc_label = NO_DATA
    else:
        p_st = status_range(cur["protein_pct"], *P_RANGE)
        f_st = status_range(cur["fat_pct"], *F_RANGE)
        c_st = status_range(cur["carb_pct"], *C_RANGE)
        pfc_worst = next((s for s in (f_st, p_st, c_st) if s[0] == "bad"), None) or \
            next((s for s in (f_st, p_st, c_st) if s[0] == "warn"), None) or ("good", "目安内")
        pfc_label = (pfc_worst[0], "要調整" if pfc_worst[0] != "good" else "目安内")

    def pfc_row(name, v, rng):
        if v is None:
            return f'<div class="pfc-row"><span>{name}</span><span class="bar"></span><span class="num">—</span></div>'
        return (f'<div class="pfc-row"><span>{name}</span>'
                f'<span class="bar"><span style="width:{min(v, 100):.1f}%"></span></span>'
                f'<span class="num">{v:.1f}%</span></div>')

    cards = [
        f'''<div class="kpi"><div class="head"><span class="label">摂取カロリー（1日平均）</span>{chip(st(status_cal, "calorie_kcal"))}</div>
<div class="value">{val("calorie_kcal", lambda v: f"{v:,}")}<small>kcal</small></div>
<div class="target">目安 {CAL_TARGET[0]:,}〜{CAL_TARGET[1]:,}kcal</div>
<div class="delta">{delta_text(cur, prev, "calorie_kcal", "kcal")}</div></div>''',
        f'''<div class="kpi"><div class="head"><span class="label">PFCバランス</span>{chip(pfc_label)}</div>
<div class="pfc-rows">{pfc_row("たんぱく質", cur["protein_pct"], P_RANGE)}{pfc_row("脂質", cur["fat_pct"], F_RANGE)}{pfc_row("炭水化物", cur["carb_pct"], C_RANGE)}</div>
<div class="target">目安 P {P_RANGE[0]}〜{P_RANGE[1]}%・F {F_RANGE[0]}〜{F_RANGE[1]}%・C {C_RANGE[0]}〜{C_RANGE[1]}%</div></div>''',
        f'''<div class="kpi"><div class="head"><span class="label">歩数（1日平均）</span>{chip(st(status_steps, "steps"))}</div>
<div class="value">{val("steps", lambda v: f"{v:,}")}<small>歩</small></div>
<div class="target">目安 {STEPS_TARGET:,}歩</div>
<div class="delta">{delta_text(cur, prev, "steps", "歩")}</div></div>''',
        f'''<div class="kpi"><div class="head"><span class="label">睡眠時間（1日平均）</span>{chip(st(status_sleep, "sleep_hours"))}</div>
<div class="value">{val("sleep_hours", lambda v: f"{v:.1f}")}<small>時間</small></div>
<div class="target">目安 {SLEEP_MIN}時間以上</div>
<div class="delta">{delta_text(cur, prev, "sleep_hours", "時間", 1)}</div></div>''',
    ]
    return "\n".join(cards)


def nice_bounds(values, band):
    lo = min(values + [band[0]])
    hi = max(values + [band[1]])
    pad = (hi - lo) * 0.12 or 1
    return lo - pad, hi + pad


def line_chart(title, unit, series, key, band, fmt):
    """band: (下限, 上限)。上限がNoneのものは上端まで塗る"""
    W, H = 320, 150
    L, R, T, B = 44, 40, 12, 22  # 左は目盛り、右は最終値ラベルの余白
    series = [s for s in series if s[key] is not None]
    if not series:
        return (f'<div class="chart"><h3><span>{html.escape(title)}</span></h3>'
                f'<p class="label">データなし</p></div>')
    vals = [s[key] for s in series]
    band_hi = band[1] if band[1] is not None else max(vals + [band[0]])
    y0, y1 = nice_bounds(vals, (band[0], band_hi))
    if band[1] is None:
        y1 = max(y1, band[0] * 1.05)

    def x(i):
        return L + (W - L - R) * (i / (len(series) - 1) if len(series) > 1 else 0.5)

    def y(v):
        return T + (H - T - B) * (1 - (v - y0) / (y1 - y0))

    parts = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{html.escape(title)}の週次推移">']
    by_top = y(min(band_hi if band[1] is not None else y1, y1))
    by_bot = y(max(band[0], y0))
    parts.append(f'<rect class="band" x="{L}" y="{by_top:.1f}" width="{W - L - R}" height="{max(by_bot - by_top, 0):.1f}"/>')
    ticks = [band[0]] + ([band[1]] if band[1] is not None else [])
    for t in ticks:
        parts.append(f'<line class="grid" x1="{L}" x2="{W - R}" y1="{y(t):.1f}" y2="{y(t):.1f}"/>')
        parts.append(f'<text x="{L - 6}" y="{y(t) + 3:.1f}" text-anchor="end">{fmt(t)}</text>')
    pts = " ".join(f"{x(i):.1f},{y(v):.1f}" for i, v in enumerate(vals))
    parts.append(f'<polyline class="line" points="{pts}"/>')
    for i, v in enumerate(vals):
        last = " last" if i == len(vals) - 1 else ""
        parts.append(f'<circle class="dot{last}" cx="{x(i):.1f}" cy="{y(v):.1f}" r="{4 if last else 2.8}"/>')
    lx, lv = x(len(vals) - 1), vals[-1]
    parts.append(f'<text class="endval" x="{lx + 7:.1f}" y="{y(lv) + 4:.1f}">{fmt(lv)}</text>')
    for i, s in enumerate(series):
        if i in (0, len(series) - 1) or (len(series) > 4 and i == len(series) // 2):
            parts.append(f'<text x="{x(i):.1f}" y="{H - 6}" text-anchor="middle">{short_date(s["report_date"])}</text>')
    parts.append("</svg>")
    band_txt = f"目安 {fmt(band[0])}〜{fmt(band[1])}{unit}" if band[1] is not None else f"目安 {fmt(band[0])}{unit}以上"
    return (f'<div class="chart"><h3><span>{html.escape(title)}</span>'
            f'<span class="label">{band_txt}</span></h3>{"".join(parts)}</div>')


def build_charts(series):
    return "\n".join([
        line_chart("摂取カロリー", "kcal", series, "calorie_kcal", CAL_TARGET, lambda v: f"{v:,.0f}"),
        line_chart("たんぱく質比率", "%", series, "protein_pct", P_RANGE, lambda v: f"{v:.1f}" if v % 1 else f"{v:.0f}"),
        line_chart("脂質比率", "%", series, "fat_pct", F_RANGE, lambda v: f"{v:.1f}" if v % 1 else f"{v:.0f}"),
        line_chart("炭水化物比率", "%", series, "carb_pct", C_RANGE, lambda v: f"{v:.1f}" if v % 1 else f"{v:.0f}"),
        line_chart("歩数", "歩", series, "steps", (STEPS_TARGET, None), lambda v: f"{v:,.0f}"),
        line_chart("睡眠時間", "時間", series, "sleep_hours", (SLEEP_MIN, None), lambda v: f"{v:.1f}" if v % 1 else f"{v:.0f}"),
    ])


def build_trend_table(series):
    head = ("<tr><th>レポート日</th><th>対象期間</th><th class=\"n\">日数</th><th class=\"n\">カロリー</th>"
            "<th class=\"n\">P</th><th class=\"n\">F</th><th class=\"n\">C</th><th class=\"n\">歩数</th><th class=\"n\">睡眠</th></tr>")

    def cell(s, key, fmt):
        return f'<td class="n">{fmt(s[key]) if s[key] is not None else "—"}</td>'

    rows = []
    for i, s in enumerate(reversed(series)):
        cls = ' class="current"' if i == 0 else ""
        rows.append(
            f'<tr{cls}><td>{short_date(s["report_date"])}</td>'
            f'<td>{short_date(s["period_start"])}〜{short_date(s["period_end"])}</td>'
            f'<td class="n">{s["days"]}</td>'
            + cell(s, "calorie_kcal", lambda v: f"{v:,}kcal")
            + cell(s, "protein_pct", lambda v: f"{v:.1f}%") + cell(s, "fat_pct", lambda v: f"{v:.1f}%")
            + cell(s, "carb_pct", lambda v: f"{v:.1f}%") + cell(s, "steps", lambda v: f"{v:,}")
            + cell(s, "sleep_hours", lambda v: f"{v:.1f}h") + "</tr>")
    return f'<table class="trend-table"><thead>{head}</thead><tbody>{"".join(rows)}</tbody></table>'


def week_path(report_date):
    return f"weeks/{report_date}.html"


def build_archive(weeks, current_date):
    """過去の号（新しい順）へのリンク一覧"""
    items = []
    for w in sorted(weeks, key=lambda w: w["report_date"], reverse=True):
        cur = w["report_date"] == current_date
        label = f'{jp_date(w["report_date"])}号'
        span = f'{short_date(w["period_start"])}〜{short_date(w["period_end"])}（{w.get("days", "?")}日分）'
        link = (f'<span class="issue">{html.escape(label)}</span>' if cur else
                f'<a class="issue" href="{week_path(w["report_date"])}">{html.escape(label)}</a>')
        li_class = ' class="current"' if cur else ""
        note = "　このページ" if cur else ""
        items.append(f'<li{li_class}>{link}<span class="span">{html.escape(span)}{note}</span></li>')
    return (f'  <section class="section" aria-labelledby="archive-h">\n    <h2 id="archive-h">過去のレポート</h2>\n'
            f'    <p class="lead">各号は作成した週の内容のまま残しています。</p>\n'
            f'    <ul class="archive">{"".join(items)}</ul>\n  </section>')


def build_feedback(items):
    """フィードバック履歴（新しい順）のセクション"""
    if not items:
        body = '<p class="lead">まだフィードバックはありません。</p>'
    else:
        parts = []
        for f in sorted(items, key=lambda f: str(f.get("date", "")), reverse=True):
            issue = str(f.get("issue", "")).strip()
            first = issue.splitlines()[0] if issue else "（指摘なし）"
            parts.append(
                f'<details class="fb"><summary><span class="num">{html.escape(str(f.get("date", "")))}</span>'
                f'<span>{html.escape(first)}</span></summary>'
                f'<dl><dt>指摘</dt><dd>{html.escape(issue)}</dd>'
                f'<dt>反映</dt><dd>{html.escape(str(f.get("applied", "")).strip())}</dd></dl></details>')
        body = "\n".join(parts)
    return (f'  <section class="section" aria-labelledby="fb-h">\n    <h2 id="fb-h">フィードバック履歴</h2>\n'
            f'    <p class="lead">レポートへの指摘と反映内容です。次回以降のレポート作成で参照します。</p>\n'
            f'    <div class="feedback">{body}</div>\n  </section>')


def build_candidates(items):
    """未反映のガイド更新候補（新しい順）のセクション。なければ出さない"""
    open_items = [c for c in items if not c.get("resolved")]
    if not open_items:
        return ""
    parts = []
    for c in sorted(open_items, key=lambda c: str(c.get("date", "")), reverse=True):
        source = str(c.get("source", "")).strip()
        source_html = f'<dt>出典</dt><dd>{html.escape(source)}</dd>' if source else ""
        parts.append(
            f'<details class="fb"><summary><span class="num">{html.escape(str(c.get("date", "")))}</span>'
            f'<span>{html.escape(str(c.get("target", "")))}</span></summary>'
            f'<dl><dt>修正案</dt><dd>{html.escape(str(c.get("proposal", "")).strip())}</dd>{source_html}</dl></details>')
    return (f'\n\n  <section class="section" aria-labelledby="guide-h">\n    <h2 id="guide-h">ガイド更新候補</h2>\n'
            f'    <p class="lead">レポート作成中に見つかった、判定の目安（参照ガイド）の見直し候補です。スキルに反映すると一覧から消えます。</p>\n'
            f'    <div class="feedback">{"".join(parts)}</div>\n  </section>')


def state_script(state):
    """次回の読み取り用に、ページにも状態JSONを埋め込む（data/state.json が読めない環境の予備）"""
    data = json.dumps(state, ensure_ascii=False).replace("</", "<\\/")
    return f'<script type="application/json" id="{STATE_SCRIPT_ID}">{data}</script>'


WEEK_PAGE_HEAD = """<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<style>:root{box-sizing:border-box;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style>
</head>
<body>
"""


# ---- 簡易Markdown変換（markdown パッケージがない環境用） ----

def md_inline(text):
    """インライン記法（コード・リンク・太字・斜体）。先にエスケープしてからタグを入れる"""
    codes = []

    def keep_code(m):
        codes.append(f"<code>{html.escape(m.group(1))}</code>")
        return f"\x00{len(codes) - 1}\x00"

    text = re.sub(r"`([^`]+)`", keep_code, text)
    text = html.escape(text, quote=False)
    text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)",
                  lambda m: f'<a href="{html.escape(m.group(2))}">{m.group(1)}</a>', text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<![*\w])\*(?!\s)(.+?)(?<!\s)\*(?![*\w])", r"<em>\1</em>", text)
    return re.sub(r"\x00(\d+)\x00", lambda m: codes[int(m.group(1))], text)


def md_table(lines):
    def cells(line):
        return [c.strip() for c in line.strip().strip("|").split("|")]

    head = "\n".join(f"<th>{md_inline(c)}</th>" for c in cells(lines[0]))
    rows = "\n".join("<tr>\n" + "\n".join(f"<td>{md_inline(c)}</td>" for c in cells(l)) + "\n</tr>"
                     for l in lines[2:])
    return f"<table>\n<thead>\n<tr>\n{head}\n</tr>\n</thead>\n<tbody>\n{rows}\n</tbody>\n</table>"


def simple_markdown(md_text):
    """レポートで使う記法（見出し・段落・箇条書き・番号付きリスト・表・水平線・インライン）だけを変換する"""
    lines = md_text.splitlines()
    out, i = [], 0
    is_table_sep = lambda l: re.fullmatch(r"\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?\s*", l)
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
        elif re.fullmatch(r"\s*(-{3,}|\*{3,}|_{3,})\s*", line):
            out.append("<hr />")
            i += 1
        elif m := re.match(r"^(#{1,6})\s+(.*?)\s*#*\s*$", line):
            n = len(m.group(1))
            out.append(f"<h{n}>{md_inline(m.group(2))}</h{n}>")
            i += 1
        elif "|" in line and i + 1 < len(lines) and is_table_sep(lines[i + 1]):
            block = [line, lines[i + 1]]
            i += 2
            while i < len(lines) and "|" in lines[i] and lines[i].strip():
                block.append(lines[i])
                i += 1
            out.append(md_table(block))
        elif re.match(r"^\s*([-*+]|\d+\.)\s+", line):
            ordered = bool(re.match(r"^\s*\d+\.", line))
            tag = "ol" if ordered else "ul"
            pat = r"^\s*\d+\.\s+" if ordered else r"^\s*[-*+]\s+"
            items = []
            while i < len(lines) and re.match(pat, lines[i]):
                items.append(f"<li>{md_inline(re.sub(pat, '', lines[i]))}</li>")
                i += 1
            out.append(f"<{tag}>\n" + "\n".join(items) + f"\n</{tag}>")
        else:
            para = []
            while i < len(lines) and lines[i].strip() and not re.match(
                    r"^(#{1,6}\s|\s*([-*+]|\d+\.)\s+|\s*(-{3,}|\*{3,}|_{3,})\s*$)", lines[i]) \
                    and not ("|" in lines[i] and i + 1 < len(lines) and is_table_sep(lines[i + 1])):
                para.append(lines[i].strip())
                i += 1
            out.append(f"<p>{md_inline(chr(10).join(para))}</p>")
    return "\n".join(out)


def build_report(md_text):
    md_text = re.sub(r"^# .*\n", "", md_text, count=1)  # H1は見出し部と重複するため除く
    if markdown is not None:
        body = markdown.markdown(md_text, extensions=["tables"])
    else:
        body = simple_markdown(md_text)
    body = body.replace("<table>", '<div class="table-wrap"><table>').replace("</table>", "</table></div>")
    body = body.replace("<a href=", '<a target="_blank" rel="noopener" href=')
    return body


def main():
    args = parse_args()
    try:
        datetime.datetime.strptime(args.date, "%Y-%m-%d")
    except ValueError:
        fail(f"--date は YYYY-MM-DD 形式で指定してください: {args.date}")
    if args.weeks < 1:
        fail("--weeks は1以上で指定してください")
    if not os.path.exists(args.report):
        fail(f"--report が見つかりません: {args.report}")
    state = load_state(args.state)
    series = load_summaries(args.date, args.weeks, args.current, args.history, state["weeks"])

    cur = series[-1]
    prev = series[-2] if len(series) > 1 else None
    with open(args.report, encoding="utf-8") as f:
        md_text = f.read()
    with open(TEMPLATE, encoding="utf-8") as f:
        template = f.read()

    # 号の一覧に今週号を追加（同じ日の号は置き換え）
    entry = {k: cur[k] for k in REQUIRED_KEYS + METRIC_KEYS}
    entry["path"] = week_path(args.date)
    weeks = [w for w in state["weeks"] if w.get("report_date") != args.date] + [entry]
    state = {"weeks": sorted(weeks, key=lambda w: w["report_date"]), "feedback": state["feedback"],
             "guide_candidates": state["guide_candidates"]}

    period = (f'{jp_date(cur["period_start"])}〜{jp_date(cur["period_end"], with_year=False)}'
              f'<span class="num">（{cur["days"]}日分）</span>')
    meta = f'{jp_date(cur["report_date"])}作成　記録元: 「食事」シート・LifeGraphシート・健康診断結果'
    lead = (f'直近{len(series)}週分の1日平均。帯は目安の範囲です'
            f'（{short_date(series[0]["report_date"])}〜{short_date(cur["report_date"])}のレポート）。')
    common = {
        "<!--@PERIOD-->": period,
        "<!--@META-->": html.escape(meta),
        "<!--@KPIS-->": build_kpis(cur, prev),
        "<!--@TREND_LEAD-->": html.escape(lead),
        "<!--@CHARTS-->": build_charts(series),
        "<!--@TREND_TABLE-->": build_trend_table(series),
        "<!--@REPORT-->": build_report(md_text),
    }

    def render(extra):
        page = template
        for k, v in {**common, **extra}.items():
            page = page.replace(k, v)
        return page

    index_html = render({
        "<!--@NAV-->": '    <nav class="issue-nav" aria-label="号の切り替え"><a href="#archive-h">過去のレポートを見る</a></nav>',
        "<!--@EXTRA_SECTIONS-->": (build_archive(state["weeks"], args.date) + "\n\n" + build_feedback(state["feedback"])
                                  + build_candidates(state["guide_candidates"])),
        "<!--@STATE_SCRIPT-->": state_script(state),
    })
    week_html = WEEK_PAGE_HEAD + render({
        "<!--@NAV-->": '    <nav class="issue-nav" aria-label="号の切り替え"><a href="../index.html">最新号と過去のレポート一覧へ</a></nav>',
        "<!--@EXTRA_SECTIONS-->": "",
        "<!--@STATE_SCRIPT-->": "",
    }) + "\n</body>\n</html>\n"

    out_dir = os.path.abspath(os.path.expanduser(args.out_dir))
    outputs = {"index.html": index_html, week_path(args.date): week_html,
               "data/state.json": json.dumps(state, ensure_ascii=False, indent=2) + "\n"}
    for rel, text in outputs.items():
        path = os.path.join(out_dir, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
    print(json.dumps({
        "success": True,
        "out_dir": out_dir,
        "file_path": os.path.join(out_dir, "index.html"),
        "files": {rel: os.path.join(out_dir, rel) for rel in outputs if rel != "index.html"},
        "weeks": len(series),
        "issues": len(state["weeks"]),
        "markdown_engine": "markdown" if markdown is not None else "builtin",
    }, ensure_ascii=False))

if __name__ == "__main__":
    main()
