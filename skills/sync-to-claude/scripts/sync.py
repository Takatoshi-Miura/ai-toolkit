#!/usr/bin/env python3
"""
ai-toolkit → ~/.claude/ 一方向同期スクリプト

ai-toolkitリポジトリ内のcommands, agents, skillsを
~/.claude/ の対応ディレクトリにコピーする。
~/.claude/ にしか存在しないファイルは一切触れない。

使用方法:
    python3 sync.py [--dry-run]

オプション:
    --dry-run: 実際にはコピーせず、何がコピーされるかを表示
"""

import filecmp
import json
import os
import shutil
import sys


def get_repo_root() -> str:
    """ai-toolkitリポジトリのルートパスを取得"""
    # このスクリプトは skills/sync-to-claude/scripts/sync.py にある
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(os.path.dirname(os.path.dirname(script_dir)))


def get_claude_dir() -> str:
    """~/.claude/ のパスを取得"""
    return os.path.join(os.path.expanduser("~"), ".claude")


def sync_flat_files(src_dir: str, dst_dir: str, pattern: str, dry_run: bool) -> dict:
    """フラットなファイル群を同期（commands/, agents/）

    Args:
        src_dir: コピー元ディレクトリ
        dst_dir: コピー先ディレクトリ
        pattern: ファイル拡張子（例: ".md"）
        dry_run: Trueの場合コピーしない

    Returns:
        dict: 同期結果（copied, skipped, errorsのリスト）
    """
    result = {"copied": [], "skipped": [], "errors": [], "onlyInDest": []}

    if not os.path.isdir(src_dir):
        return result

    os.makedirs(dst_dir, exist_ok=True)

    src_files = {f for f in os.listdir(src_dir)
                 if f.endswith(pattern) and os.path.isfile(os.path.join(src_dir, f))}

    for filename in sorted(src_files):
        src_path = os.path.join(src_dir, filename)
        dst_path = os.path.join(dst_dir, filename)

        try:
            if os.path.exists(dst_path) and filecmp.cmp(src_path, dst_path, shallow=False):
                result["skipped"].append(filename)
            else:
                if not dry_run:
                    shutil.copy2(src_path, dst_path)
                result["copied"].append(filename)
        except Exception as e:
            result["errors"].append({"file": filename, "error": str(e)})

    # ~/.claude/ にのみ存在するファイルを検出
    if os.path.isdir(dst_dir):
        dst_files = {f for f in os.listdir(dst_dir)
                     if f.endswith(pattern) and os.path.isfile(os.path.join(dst_dir, f))}
        result["onlyInDest"] = sorted(dst_files - src_files)

    return result


def sync_skill_dir(src_skill: str, dst_skill: str, dry_run: bool) -> dict:
    """スキルディレクトリを再帰的に同期

    Args:
        src_skill: コピー元スキルディレクトリ
        dst_skill: コピー先スキルディレクトリ
        dry_run: Trueの場合コピーしない

    Returns:
        dict: 同期結果（copied, skipped, errorsのリスト）
    """
    result = {"copied": [], "skipped": [], "errors": []}

    for dirpath, _dirnames, filenames in os.walk(src_skill):
        rel_dir = os.path.relpath(dirpath, src_skill)
        dst_dir = os.path.join(dst_skill, rel_dir) if rel_dir != "." else dst_skill

        if not dry_run:
            os.makedirs(dst_dir, exist_ok=True)

        for filename in sorted(filenames):
            src_path = os.path.join(dirpath, filename)
            dst_path = os.path.join(dst_dir, filename)
            rel_path = os.path.relpath(src_path, src_skill)

            try:
                if os.path.exists(dst_path) and filecmp.cmp(src_path, dst_path, shallow=False):
                    result["skipped"].append(rel_path)
                else:
                    if not dry_run:
                        shutil.copy2(src_path, dst_path)
                    result["copied"].append(rel_path)
            except Exception as e:
                result["errors"].append({"file": rel_path, "error": str(e)})

    return result


def sync_skills(src_dir: str, dst_dir: str, dry_run: bool) -> dict:
    """skills/ ディレクトリ全体を同期

    Args:
        src_dir: コピー元 skills/ ディレクトリ
        dst_dir: コピー先 skills/ ディレクトリ
        dry_run: Trueの場合コピーしない

    Returns:
        dict: スキル名をキーとした同期結果
    """
    results = {"_synced": {}, "_onlyInDest": []}

    if not os.path.isdir(src_dir):
        return results

    os.makedirs(dst_dir, exist_ok=True)

    src_skills = {d for d in os.listdir(src_dir)
                  if os.path.isdir(os.path.join(src_dir, d))}

    for skill_name in sorted(src_skills):
        src_skill = os.path.join(src_dir, skill_name)
        dst_skill = os.path.join(dst_dir, skill_name)
        results["_synced"][skill_name] = sync_skill_dir(src_skill, dst_skill, dry_run)

    # ~/.claude/skills/ にのみ存在するスキルを検出
    if os.path.isdir(dst_dir):
        dst_skills = {d for d in os.listdir(dst_dir)
                      if os.path.isdir(os.path.join(dst_dir, d))}
        results["_onlyInDest"] = sorted(dst_skills - src_skills)

    return results


def main():
    dry_run = "--dry-run" in sys.argv

    repo_root = get_repo_root()
    claude_dir = get_claude_dir()

    output = {
        "mode": "dry-run" if dry_run else "sync",
        "source": repo_root,
        "destination": claude_dir,
        "commands": {},
        "agents": {},
        "skills": {},
        "summary": {"totalCopied": 0, "totalSkipped": 0, "totalErrors": 0}
    }

    # commands/ の同期
    output["commands"] = sync_flat_files(
        os.path.join(repo_root, "commands"),
        os.path.join(claude_dir, "commands"),
        ".md",
        dry_run
    )

    # agents/ の同期
    output["agents"] = sync_flat_files(
        os.path.join(repo_root, "agents"),
        os.path.join(claude_dir, "agents"),
        ".md",
        dry_run
    )

    # skills/ の同期
    output["skills"] = sync_skills(
        os.path.join(repo_root, "skills"),
        os.path.join(claude_dir, "skills"),
        dry_run
    )

    # サマリー集計
    total_only_in_dest = []
    for category in ["commands", "agents"]:
        data = output[category]
        output["summary"]["totalCopied"] += len(data.get("copied", []))
        output["summary"]["totalSkipped"] += len(data.get("skipped", []))
        output["summary"]["totalErrors"] += len(data.get("errors", []))
        for f in data.get("onlyInDest", []):
            total_only_in_dest.append(f"{category}/{f}")

    for _skill_name, data in output["skills"].get("_synced", {}).items():
        output["summary"]["totalCopied"] += len(data.get("copied", []))
        output["summary"]["totalSkipped"] += len(data.get("skipped", []))
        output["summary"]["totalErrors"] += len(data.get("errors", []))

    for skill_name in output["skills"].get("_onlyInDest", []):
        total_only_in_dest.append(f"skills/{skill_name}/")

    output["summary"]["onlyInDest"] = total_only_in_dest

    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
