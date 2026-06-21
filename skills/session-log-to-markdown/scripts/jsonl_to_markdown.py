#!/usr/bin/env python3
"""Claude Codeのセッションログ(JSONL)を1つのMarkdownファイルに変換する。

サブコマンド:
  list    : 指定プロジェクトのセッション一覧をJSONで表示
  convert : 指定セッション(群)をMarkdownに変換して書き出す
"""

import argparse
import json
import sys
from datetime import datetime, date
from pathlib import Path

KNOWN_TYPES = {"user", "assistant"}
TOOL_RESULT_PREVIEW_LIMIT = 2000
NOISE_TAGS = ("ide_opened_file", "system-reminder", "ide_selection")


# ---------- 1. セッション検出 ----------

def resolve_project_log_dir(project_dir: str | None) -> Path:
    cwd = project_dir or str(Path.cwd())
    hyphenated = cwd.replace("/", "-")
    return Path.home() / ".claude" / "projects" / hyphenated


def list_sessions(log_dir: Path) -> list[dict]:
    index_path = log_dir / "sessions-index.json"
    if index_path.exists():
        try:
            index = json.loads(index_path.read_text(encoding="utf-8"))
            entries = index.get("entries", [])
            sessions = []
            for e in entries:
                jsonl_path = log_dir / f"{e['sessionId']}.jsonl"
                if not jsonl_path.exists():
                    continue
                sessions.append({
                    "session_id": e["sessionId"],
                    "path": str(jsonl_path),
                    "mtime": e.get("fileMtime") or e.get("modified"),
                    "first_prompt": e.get("firstPrompt"),
                    "message_count": e.get("messageCount"),
                })
            if sessions:
                sessions.sort(key=lambda s: s["mtime"] or "", reverse=True)
                return sessions
        except (json.JSONDecodeError, KeyError):
            pass

    sessions = []
    for jsonl_path in log_dir.glob("*.jsonl"):
        stat = jsonl_path.stat()
        sessions.append({
            "session_id": jsonl_path.stem,
            "path": str(jsonl_path),
            "mtime": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "first_prompt": None,
            "message_count": None,
        })
    sessions.sort(key=lambda s: s["mtime"], reverse=True)
    return sessions


def select_sessions(log_dir: Path, mode: str, session_ids=None,
                     since: date | None = None, until: date | None = None) -> list[dict]:
    sessions = list_sessions(log_dir)

    if mode == "latest":
        return sessions[:1]

    if mode == "ids":
        wanted = set(session_ids or [])
        return [s for s in sessions if s["session_id"] in wanted]

    if mode == "all":
        return sessions

    if mode == "range":
        result = []
        for s in sessions:
            mtime = s["mtime"]
            if not mtime:
                continue
            s_date = datetime.fromisoformat(mtime.replace("Z", "+00:00")).date()
            if since and s_date < since:
                continue
            if until and s_date > until:
                continue
            result.append(s)
        return result

    raise ValueError(f"unknown mode: {mode}")


# ---------- 2. JSONL読み込み・パース ----------

def read_jsonl_lines(path: Path) -> tuple[list[dict], list[tuple[int, str]]]:
    records = []
    errors = []
    with path.open("r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                errors.append((lineno, line[:200]))
    return records, errors


# ---------- 3. ペア構築 ----------

def _extract_text_blocks(content) -> list[str]:
    if isinstance(content, str):
        return [content] if content else []
    blocks = []
    if isinstance(content, list):
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                text = item.get("text", "")
                if text:
                    blocks.append(text)
    return blocks


def _extract_tool_uses(content) -> list[dict]:
    uses = []
    if isinstance(content, list):
        for item in content:
            if isinstance(item, dict) and item.get("type") == "tool_use":
                uses.append({
                    "id": item.get("id"),
                    "name": item.get("name"),
                    "input": item.get("input", {}),
                })
    return uses


def _extract_tool_results(content) -> dict[str, dict]:
    results = {}
    if isinstance(content, list):
        for item in content:
            if isinstance(item, dict) and item.get("type") == "tool_result":
                tool_use_id = item.get("tool_use_id")
                if not tool_use_id:
                    continue
                raw = item.get("content")
                if isinstance(raw, list):
                    text_parts = [p.get("text", "") for p in raw if isinstance(p, dict) and p.get("type") == "text"]
                    text = "\n".join(text_parts)
                else:
                    text = str(raw) if raw is not None else ""
                results[tool_use_id] = {
                    "result_text": text,
                    "is_error": bool(item.get("is_error")),
                }
    return results


def build_turns(records: list[dict]) -> list[dict]:
    turns = []
    pending_tool_calls: dict[str, dict] = {}

    for rec in records:
        rec_type = rec.get("type")
        if rec_type not in KNOWN_TYPES:
            continue

        message = rec.get("message", {})
        content = message.get("content")
        timestamp = rec.get("timestamp")

        if rec_type == "user":
            tool_results = _extract_tool_results(content)
            if tool_results:
                for tool_use_id, result in tool_results.items():
                    if tool_use_id in pending_tool_calls:
                        pending_tool_calls[tool_use_id].update(result)
                continue

            text_blocks = _extract_text_blocks(content)
            if not text_blocks:
                continue
            turns.append({
                "timestamp": timestamp,
                "role": "user",
                "text_blocks": text_blocks,
                "tool_calls": [],
            })

        elif rec_type == "assistant":
            text_blocks = _extract_text_blocks(content)
            tool_uses = _extract_tool_uses(content)
            tool_calls = []
            for use in tool_uses:
                call = {
                    "id": use["id"],
                    "name": use["name"],
                    "input": use["input"],
                    "result_text": None,
                    "is_error": False,
                }
                tool_calls.append(call)
                if use["id"]:
                    pending_tool_calls[use["id"]] = call

            if not text_blocks and not tool_calls:
                continue
            turns.append({
                "timestamp": timestamp,
                "role": "assistant",
                "text_blocks": text_blocks,
                "tool_calls": tool_calls,
            })

    return turns


def pair_question_answer(turns: list[dict]) -> list[dict]:
    pairs = []
    current = None

    for turn in turns:
        if turn["role"] == "user":
            if current is not None:
                pairs.append(current)
            current = {
                "timestamp": turn["timestamp"],
                "question": "\n".join(turn["text_blocks"]),
                "answer_blocks": [],
                "tool_calls": [],
            }
        else:
            if current is None:
                current = {
                    "timestamp": turn["timestamp"],
                    "question": "",
                    "answer_blocks": [],
                    "tool_calls": [],
                }
            current["answer_blocks"].extend(turn["text_blocks"])
            current["tool_calls"].extend(turn["tool_calls"])

    if current is not None:
        pairs.append(current)

    return pairs


# ---------- 4. コンテンツ整形 ----------

def format_question(text: str) -> str:
    import re
    for tag in NOISE_TAGS:
        text = re.sub(rf"<{tag}>.*?</{tag}>", "", text, flags=re.DOTALL)
    return text.strip()


def format_tool_call(call: dict) -> str:
    name = call.get("name", "unknown")
    input_str = json.dumps(call.get("input", {}), ensure_ascii=False)
    summary_input = input_str if len(input_str) <= 80 else input_str[:80] + "..."

    lines = [f"- `{name}` `{summary_input}`"]

    result_text = call.get("result_text")
    if result_text:
        preview = result_text[:TOOL_RESULT_PREVIEW_LIMIT]
        truncated = "\n（以下省略）" if len(result_text) > TOOL_RESULT_PREVIEW_LIMIT else ""
        lines.append("  <details><summary>詳細</summary>\n")
        lines.append(f"  入力: {input_str}\n")
        lines.append(f"  結果:\n  ```\n  {preview}{truncated}\n  ```")
        lines.append("  </details>")
    else:
        lines.append("  <details><summary>詳細</summary>\n")
        lines.append(f"  入力: {input_str}\n")
        lines.append("  結果: (結果なし)")
        lines.append("  </details>")

    return "\n".join(lines)


def format_answer(answer_blocks: list[str], tool_calls: list[dict]) -> str:
    parts = []
    text = "\n\n".join(b.strip() for b in answer_blocks if b.strip())
    if text:
        parts.append(text)
    if tool_calls:
        parts.append("**Tool calls:**\n")
        parts.append("\n".join(format_tool_call(c) for c in tool_calls))
    return "\n\n".join(parts) if parts else "(応答テキストなし)"


# ---------- 5. Markdown生成・書き出し ----------

def render_session_markdown(session_meta: dict, qa_pairs: list[dict]) -> str:
    lines = []
    first_question = format_question(qa_pairs[0]["question"]) if qa_pairs else ""
    title = session_meta.get("title") or (first_question[:40] if first_question else "(無題)")
    lines.append(f"# Session Log: {title}")
    lines.append("")
    lines.append(f"- Session ID: `{session_meta.get('session_id')}`")
    lines.append(f"- Project: `{session_meta.get('cwd', '')}`")
    lines.append(f"- Branch: `{session_meta.get('git_branch', '')}`")
    lines.append(f"- 開始: `{session_meta.get('start_time', '')}` / 終了: `{session_meta.get('end_time', '')}`")
    lines.append("")
    lines.append("---")

    for i, pair in enumerate(qa_pairs, start=1):
        lines.append("")
        lines.append(f"## {pair['timestamp']} | Q{i}")
        lines.append("")
        lines.append("### Question")
        lines.append("")
        question = format_question(pair["question"])
        for q_line in question.splitlines() or [""]:
            lines.append(f"> {q_line}")
        lines.append("")
        lines.append("### Answer")
        lines.append("")
        lines.append(format_answer(pair["answer_blocks"], pair["tool_calls"]))
        lines.append("")
        lines.append("---")

    return "\n".join(lines)


def write_output(path: Path, content: str) -> dict:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return {"written": False, "path": str(path), "unchanged": True}
    path.write_text(content, encoding="utf-8")
    return {"written": True, "path": str(path), "unchanged": False}


# ---------- 6. CLI ----------

def cmd_list(args) -> dict:
    log_dir = resolve_project_log_dir(args.project_dir)
    if not log_dir.exists():
        return {"success": False, "error": f"project log dir not found: {log_dir}"}
    sessions = list_sessions(log_dir)
    return {"success": True, "log_dir": str(log_dir), "sessions": sessions}


def cmd_convert(args) -> dict:
    log_dir = resolve_project_log_dir(args.project_dir)
    if not log_dir.exists():
        return {"success": False, "error": f"project log dir not found: {log_dir}"}

    if args.latest:
        mode = "latest"
    elif args.session_id:
        mode = "ids"
    elif args.all:
        mode = "all"
    elif args.since:
        mode = "range"
    else:
        mode = "latest"

    since = date.fromisoformat(args.since) if args.since else None
    until = date.fromisoformat(args.until) if args.until else None

    sessions = select_sessions(log_dir, mode, args.session_id, since, until)
    if not sessions:
        return {"success": False, "error": "no matching sessions found"}

    all_warnings = []
    total_skipped = 0
    session_summaries = []
    rendered_sections = []

    for session in sessions:
        jsonl_path = Path(session["path"])
        records, errors = read_jsonl_lines(jsonl_path)
        total_skipped += len(errors)
        if errors:
            all_warnings.append(f"{session['session_id']}: {len(errors)} 行のパースに失敗")

        turns = build_turns(records)
        qa_pairs = pair_question_answer(turns)

        if not qa_pairs:
            all_warnings.append(f"{session['session_id']}: メッセージが空のためスキップ")
            continue

        first_rec = next((r for r in records if r.get("type") in KNOWN_TYPES), {})
        session_meta = {
            "session_id": session["session_id"],
            "cwd": first_rec.get("cwd", ""),
            "git_branch": first_rec.get("gitBranch", ""),
            "start_time": qa_pairs[0]["timestamp"],
            "end_time": qa_pairs[-1]["timestamp"],
            "title": None,
        }

        rendered_sections.append(render_session_markdown(session_meta, qa_pairs))
        session_summaries.append({
            "session_id": session["session_id"],
            "qa_count": len(qa_pairs),
            "skipped_lines": len(errors),
        })

    if not rendered_sections:
        return {"success": False, "error": "no convertible sessions (all empty)", "warnings": all_warnings}

    content = "\n\n".join(rendered_sections)
    output_path = Path(args.output).expanduser()
    write_result = write_output(output_path, content)

    return {
        "success": True,
        "output_path": write_result["path"],
        "unchanged": write_result["unchanged"],
        "sessions": session_summaries,
        "skipped_lines": total_skipped,
        "warnings": all_warnings,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list")
    p_list.add_argument("--project-dir")

    p_conv = sub.add_parser("convert")
    p_conv.add_argument("--output", required=True)
    g = p_conv.add_mutually_exclusive_group()
    g.add_argument("--latest", action="store_true")
    g.add_argument("--session-id", action="append")
    g.add_argument("--all", action="store_true")
    g.add_argument("--since")
    p_conv.add_argument("--until")
    p_conv.add_argument("--project-dir")

    args = parser.parse_args()
    result = cmd_list(args) if args.command == "list" else cmd_convert(args)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result.get("success", True) else 1)


if __name__ == "__main__":
    main()
