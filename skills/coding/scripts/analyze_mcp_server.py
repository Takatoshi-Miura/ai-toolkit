#!/usr/bin/env python3
"""MCPサーバーのツール一覧を自動抽出するスクリプト。

指定ディレクトリ内のソースファイルから server.tool() 定義を解析し、
ツール名・説明・パラメータを一覧表示する。

使用例:
    python3 analyze_mcp_server.py ~/Documents/Git/MCP-GoogleDrive
"""

import re
import sys
from pathlib import Path


def find_source_files(directory: Path) -> list[Path]:
    """ソースファイル(.ts, .js)を再帰検索。node_modules, distは除外。"""
    exclude_dirs = {"node_modules", "dist", ".git", "__pycache__"}
    files = []
    for ext in ("*.ts", "*.js"):
        for f in directory.rglob(ext):
            if not any(part in exclude_dirs for part in f.parts):
                files.append(f)
    return sorted(files)


def extract_tools(file_path: Path) -> list[dict]:
    """ファイルから server.tool() 定義を抽出。"""
    content = file_path.read_text(encoding="utf-8")
    tools = []

    # server.tool("name", "description", { ... }, async handler) パターン
    pattern = r'server\.tool\(\s*["\']([^"\']+)["\']\s*,\s*["\']([^"\']+)["\']\s*,'
    for match in re.finditer(pattern, content):
        tool_name = match.group(1)
        tool_desc = match.group(2)

        # パラメータ部分を抽出（tool定義の開始位置から次の閉じ括弧まで）
        start = match.end()
        params = extract_params(content, start)

        tools.append({
            "name": tool_name,
            "description": tool_desc,
            "params": params,
            "file": str(file_path),
        })

    return tools


def extract_params(content: str, start: int) -> list[str]:
    """zodスキーマからパラメータ名を抽出。"""
    # { key: z.xxx(), ... } ブロックを探す
    brace_start = content.find("{", start)
    if brace_start == -1 or brace_start - start > 200:
        return []

    depth = 0
    end = brace_start
    for i in range(brace_start, min(brace_start + 2000, len(content))):
        if content[i] == "{":
            depth += 1
        elif content[i] == "}":
            depth -= 1
            if depth == 0:
                end = i
                break

    block = content[brace_start:end + 1]
    # key: z.xxx() パターンでパラメータ名を抽出
    param_pattern = r'(\w+)\s*:\s*z\.'
    return re.findall(param_pattern, block)


def main():
    if len(sys.argv) < 2:
        print("使用法: python3 analyze_mcp_server.py <MCPサーバーディレクトリ>")
        sys.exit(1)

    directory = Path(sys.argv[1]).expanduser().resolve()
    if not directory.is_dir():
        print(f"エラー: ディレクトリが見つかりません: {directory}")
        sys.exit(1)

    files = find_source_files(directory)
    if not files:
        print(f"ソースファイルが見つかりません: {directory}")
        sys.exit(1)

    all_tools = []
    for f in files:
        tools = extract_tools(f)
        all_tools.extend(tools)

    if not all_tools:
        print("ツール定義が見つかりませんでした。")
        sys.exit(0)

    # テーブル形式で出力
    print(f"\n## MCPツール一覧 ({directory.name})\n")
    print(f"| # | ツール名 | 説明 | パラメータ | 定義ファイル |")
    print(f"|---|---------|------|-----------|-------------|")
    for i, tool in enumerate(all_tools, 1):
        params = ", ".join(tool["params"]) if tool["params"] else "-"
        rel_path = Path(tool["file"]).relative_to(directory)
        print(f"| {i} | `{tool['name']}` | {tool['description']} | {params} | {rel_path} |")

    print(f"\n合計: {len(all_tools)} ツール")


if __name__ == "__main__":
    main()
