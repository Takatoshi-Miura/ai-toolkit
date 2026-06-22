#!/usr/bin/env python3
"""jsonl_to_markdown.py が生成したMarkdownログからルール化候補を粗く抽出する。

サブコマンド:
  scan : Markdownログファイルを読み込み、フィードバック候補をJSONで出力する

このスクリプトは正規表現でカテゴリラベル付きの候補を広く抽出するだけで、
ルール化すべきか・どのプロジェクトの話か・既存ルールと重複するかの判断は行わない。
それらの最終判断はSKILL.mdの手順内でClaude本体が行う。

入力は scripts/jsonl_to_markdown.py の出力Markdown（FORMAT: `# Session Log:` で
セッション区切り、`## <timestamp> | Q{n}` でQ&A区切り、`### Question`配下の
`>`引用行がユーザー発言）。
"""

import argparse
import json
import re
import sys
from pathlib import Path

CANDIDATE_PATTERNS = {
    "prohibition": r"(しないで|やめて|禁止|二度と|もうしない|やめましょう)",
    "mandate": r"(必ず|常に|今後は|次回から|これから|べき|すること($|[。.\n])|してね|して欲しい|してください|したい($|[。.\n])|するように)",
    "approval": r"(これでいい|それで(いい|OK)|この方針で|承認|完璧|そうそう|それで(お願い|いき)|OK[。.\n]|良い(感じ|です)ね)",
    "standardize": r"(統一して|標準化|フォーマットを.*して|揺れがある)",
    "correction": r"(違う|そうじゃなくて|間違い|修正して|認識であっている|あってる\?)",
}

CONTEXT_RADIUS = 1
WARN_CANDIDATE_THRESHOLD = 200
CANDIDATE_TEXT_LIMIT = 300
CONTEXT_EXCERPT_LIMIT = 200

SESSION_HEADER_RE = re.compile(r"^# Session Log: ")
META_PROJECT_RE = re.compile(r"^- Project: `(.*)`$")
META_SESSION_ID_RE = re.compile(r"^- Session ID: `(.*)`$")
QA_HEADER_RE = re.compile(r"^## (\S+) \| Q(\d+)$")
QUESTION_HEADER_RE = re.compile(r"^### Question$")
ANSWER_HEADER_RE = re.compile(r"^### Answer$")
QUOTE_LINE_RE = re.compile(r"^> ?(.*)$")
SKIPPED_QUESTION_MARKER = "(スキル定義文の混入のため省略)"


# ---------- 1. Markdownパース ----------

def parse_markdown_log(text: str) -> list[dict]:
    """Markdownログをセッション単位の質問エントリ一覧にパースする。"""
    lines = text.splitlines()
    entries = []

    current_session_id = None
    current_project = ""
    in_question_block = False
    in_answer_block = False
    question_lines: list[str] = []
    pending_timestamp = None

    def flush_question():
        nonlocal question_lines, pending_timestamp
        if pending_timestamp is None:
            question_lines = []
            return
        question_text = "\n".join(question_lines).strip()
        if question_text and question_text != SKIPPED_QUESTION_MARKER:
            entries.append({
                "text": question_text,
                "timestamp": pending_timestamp,
                "project_dir_name": current_project,
                "sessionId": current_session_id,
            })
        question_lines = []

    for line in lines:
        if SESSION_HEADER_RE.match(line):
            flush_question()
            pending_timestamp = None
            in_question_block = False
            in_answer_block = False
            continue

        m = META_SESSION_ID_RE.match(line)
        if m:
            current_session_id = m.group(1)
            continue

        m = META_PROJECT_RE.match(line)
        if m:
            current_project = Path(m.group(1)).name if m.group(1) else ""
            continue

        m = QA_HEADER_RE.match(line)
        if m:
            flush_question()
            pending_timestamp = m.group(1)
            in_question_block = False
            in_answer_block = False
            continue

        if QUESTION_HEADER_RE.match(line):
            in_question_block = True
            in_answer_block = False
            continue

        if ANSWER_HEADER_RE.match(line):
            in_question_block = False
            in_answer_block = True
            continue

        if in_question_block:
            m = QUOTE_LINE_RE.match(line)
            if m:
                question_lines.append(m.group(1))

    flush_question()
    return entries


# ---------- 2. パターンマッチ ----------

def match_feedback_patterns(text: str) -> list[str]:
    matched = []
    for category, pattern in CANDIDATE_PATTERNS.items():
        if re.search(pattern, text):
            matched.append(category)
    return matched


def truncate(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + "…（以下省略）"


def build_context_excerpt(entries: list[dict], index: int) -> str:
    lo = max(0, index - CONTEXT_RADIUS)
    hi = min(len(entries), index + CONTEXT_RADIUS + 1)
    parts = []
    for i in range(lo, hi):
        if i == index:
            continue
        cleaned = truncate(entries[i]["text"], CONTEXT_EXCERPT_LIMIT)
        if cleaned:
            parts.append(cleaned)
    return "\n---\n".join(parts)


# ---------- 3. スキャン処理本体 ----------

def scan(markdown_path: Path) -> dict:
    text = markdown_path.read_text(encoding="utf-8")
    entries = parse_markdown_log(text)

    candidates = []
    warnings = []

    for i, entry in enumerate(entries):
        matched_categories = match_feedback_patterns(entry["text"])
        if not matched_categories:
            continue
        candidates.append({
            "text": truncate(entry["text"], CANDIDATE_TEXT_LIMIT),
            "matched_categories": matched_categories,
            "project_dir_name": entry["project_dir_name"],
            "timestamp": entry["timestamp"],
            "sessionId": entry["sessionId"],
            "context_excerpt": build_context_excerpt(entries, i),
        })

    if len(candidates) > WARN_CANDIDATE_THRESHOLD:
        warnings.append(
            f"候補が{len(candidates)}件と多いため、対象ログの期間を絞ることを推奨します"
        )

    return {
        "success": True,
        "source_markdown": str(markdown_path),
        "total_questions_scanned": len(entries),
        "candidates": candidates,
        "warnings": warnings,
    }


# ---------- 4. CLI ----------

def cmd_scan(args) -> dict:
    markdown_path = Path(args.input).expanduser()
    if not markdown_path.exists():
        return {"success": False, "error": f"input markdown not found: {markdown_path}"}

    return scan(markdown_path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_scan = sub.add_parser("scan")
    p_scan.add_argument("--input", required=True, help="jsonl_to_markdown.pyが生成したMarkdownファイルのパス")

    args = parser.parse_args()
    result = cmd_scan(args)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result.get("success", True) else 1)


if __name__ == "__main__":
    main()
