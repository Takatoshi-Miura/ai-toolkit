#!/usr/bin/env python3
"""
指定期間内のコード差分を取得するスクリプト

Usage:
    python3 git_diff_analyzer.py <repo_path> <author> <since> <until>

Arguments:
    repo_path: Gitリポジトリのパス
    author:    コミット作者名（git log --author に渡す値）
    since:     開始日（例: 2026-01-01）
    until:     終了日（例: 2026-02-14）

Output:
    JSON形式でコミット一覧・変更ファイル一覧を出力
"""
import json
import subprocess
import sys
from pathlib import Path


def run_git(repo_path: str, args: list) -> str:
    """gitコマンドを実行して標準出力を返す"""
    result = subprocess.run(
        ["git", "-C", repo_path] + args,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"git command failed: {result.stderr.strip()}")
    return result.stdout.strip()


def get_commits(repo_path: str, author: str, since: str, until: str) -> list:
    """コミット一覧を取得（マージコミット・git notes除外）"""
    output = run_git(repo_path, [
        "log",
        f"--author={author}",
        f"--since={since}",
        f"--until={until}",
        "--no-merges",
        "--pretty=format:%H|%h|%s|%ai",
        "--all",
    ])
    if not output:
        return []

    commits = []
    for line in output.split("\n"):
        parts = line.split("|", 3)
        if len(parts) != 4:
            continue
        message = parts[2].strip()
        # git notes のメタデータコミットを除外
        if message.startswith("Notes added by"):
            continue
        # stash の index コミットを除外
        if message.startswith("index on ") or message.startswith("WIP on "):
            continue
        commits.append({
            "hash": parts[0],
            "short_hash": parts[1],
            "message": message,
            "date": parts[3].strip(),
        })
    return commits


def get_changed_files(repo_path: str, author: str, since: str, until: str) -> list:
    """変更ファイル一覧を取得（マージコミット除外、ユニーク化）"""
    output = run_git(repo_path, [
        "log",
        f"--author={author}",
        f"--since={since}",
        f"--until={until}",
        "--no-merges",
        "--name-only",
        "--pretty=format:",
        "--all",
    ])
    if not output:
        return []

    files = sorted(set(
        line.strip()
        for line in output.split("\n")
        if line.strip() and not line.strip().startswith(("0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "a", "b", "c", "d", "e", "f"))
        or "/" in line.strip()
    ))
    # ファイルパスのみ抽出（コミットハッシュを除外）
    return [f for f in files if "/" in f]


def filter_production_kotlin(files: list) -> list:
    """本番用Kotlinファイルのみ抽出（src/main/java 配下の .kt ファイル）"""
    return [f for f in files if f.endswith(".kt") and "src/main/java" in f]


def analyze(repo_path: str, author: str, since: str, until: str) -> dict:
    """コード差分を分析する"""
    repo = Path(repo_path).resolve()
    if not (repo / ".git").exists():
        return {"success": False, "error": f"Gitリポジトリが見つかりません: {repo}"}

    commits = get_commits(str(repo), author, since, until)
    all_files = get_changed_files(str(repo), author, since, until)
    production_kotlin = filter_production_kotlin(all_files)

    return {
        "success": True,
        "repo_path": str(repo),
        "author": author,
        "period": {"since": since, "until": until},
        "commit_count": len(commits),
        "commits": commits,
        "all_files": all_files,
        "all_file_count": len(all_files),
        "production_kotlin_files": production_kotlin,
        "production_kotlin_file_count": len(production_kotlin),
    }


def main():
    if len(sys.argv) != 5:
        print(json.dumps({
            "success": False,
            "error": "引数が不足しています",
            "usage": "python3 git_diff_analyzer.py <repo_path> <author> <since> <until>",
        }, ensure_ascii=False))
        sys.exit(1)

    repo_path, author, since, until = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]

    try:
        result = analyze(repo_path, author, since, until)
    except Exception as e:
        result = {"success": False, "error": str(e)}

    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not result.get("success"):
        sys.exit(1)


if __name__ == "__main__":
    main()
