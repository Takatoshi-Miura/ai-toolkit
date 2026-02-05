#!/usr/bin/env python3
"""
AI-Toolkit プロンプト分析スクリプト

このスクリプトはai-toolkitリポジトリ内のプロンプトファイルを分析し、
品質チェックと参照関係マップをJSON形式で出力します。

対象: ai-toolkitリポジトリのみ（スクリプト配置場所から自動決定）

品質チェック項目は各ベストプラクティスファイルから動的に読み取られます:
- skills/manage-resources/BEST-PRACTICES-SKILL.md
- skills/manage-resources/BEST-PRACTICES-COMMAND.md
- skills/manage-resources/BEST-PRACTICES-AGENT.md

Usage:
    python3 ./analyze_prompts.py
"""

import json
import re
import sys
from pathlib import Path
from typing import Any


def parse_frontmatter(content: str) -> dict[str, Any]:
    """YAMLフロントマターを解析する（外部依存なし）"""
    frontmatter = {}
    lines = content.split('\n')

    if not lines or lines[0].strip() != '---':
        return frontmatter

    end_idx = -1
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == '---':
            end_idx = i
            break

    if end_idx == -1:
        return frontmatter

    for line in lines[1:end_idx]:
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()
            # allowed-tools や tools はリストとして解析
            if key in ['allowed-tools', 'tools', 'disallowedTools']:
                frontmatter[key] = [v.strip() for v in value.split(',') if v.strip()]
            else:
                frontmatter[key] = value

    return frontmatter


def extract_checklist_from_best_practice(content: str) -> list[str]:
    """ベストプラクティスファイルの「## チェックリスト」セクションからチェック項目を抽出する"""
    checklist = []

    # ## チェックリスト セクションを探す
    checklist_match = re.search(r'## チェックリスト\s*\n((?:- \[[ x]\] .+\n?)+)', content)
    if checklist_match:
        checklist_section = checklist_match.group(1)
        # - [ ] または - [x] で始まる行を抽出
        items = re.findall(r'- \[[ x]\] (.+)', checklist_section)
        checklist.extend(items)

    return checklist


def load_best_practices(repo_path: Path) -> dict[str, dict]:
    """ベストプラクティスSkillsを読み込み、チェックリストを抽出する"""
    best_practices = {
        "skills": {
            "path": "skills/manage-resources/BEST-PRACTICES-SKILL.md",
            "checklist": [],
            "content": ""
        },
        "slash_commands": {
            "path": "skills/manage-resources/BEST-PRACTICES-COMMAND.md",
            "checklist": [],
            "content": ""
        },
        "agents": {
            "path": "skills/manage-resources/BEST-PRACTICES-AGENT.md",
            "checklist": [],
            "content": ""
        }
    }

    for resource_type, info in best_practices.items():
        file_path = repo_path / info["path"]
        if file_path.exists():
            content = file_path.read_text(encoding='utf-8')
            info["content"] = content
            info["checklist"] = extract_checklist_from_best_practice(content)

    return best_practices


def check_slash_command_quality(
    path: Path,
    frontmatter: dict,
    content: str,
    best_practice: dict
) -> list[dict]:
    """スラッシュコマンドの品質チェック（BEST-PRACTICES-COMMAND準拠）

    ベストプラクティスから読み取ったチェックリストに基づいてチェックを実行
    """
    issues = []
    checklist = best_practice.get("checklist", [])

    # チェックリスト項目に基づいて動的にチェック
    for item in checklist:
        item_lower = item.lower()

        # descriptionチェック
        if 'description' in item_lower:
            if not frontmatter.get('description'):
                issues.append({
                    "check": "description",
                    "status": "missing",
                    "recommendation": item,
                    "source": "best-practice-checklist"
                })

        # argument-hintチェック
        if 'argument-hint' in item_lower or '引数' in item:
            uses_arguments = '$ARGUMENTS' in content or re.search(r'\$[1-9]', content)
            if uses_arguments and not frontmatter.get('argument-hint'):
                issues.append({
                    "check": "argument_hint",
                    "status": "missing",
                    "recommendation": item,
                    "source": "best-practice-checklist"
                })

        # allowed-toolsチェック
        if 'allowed-tools' in item_lower:
            if not frontmatter.get('allowed-tools'):
                issues.append({
                    "check": "allowed_tools",
                    "status": "missing",
                    "recommendation": item,
                    "source": "best-practice-checklist"
                })

    return issues


def check_skill_quality(
    path: Path,
    frontmatter: dict,
    content: str,
    line_count: int,
    best_practice: dict
) -> list[dict]:
    """Skillの品質チェック（BEST-PRACTICES-SKILL準拠）

    ベストプラクティスから読み取ったチェックリストに基づいてチェックを実行
    """
    issues = []
    checklist = best_practice.get("checklist", [])
    bp_content = best_practice.get("content", "")

    # ベストプラクティスから制約値を動的に抽出
    max_name_length = 64  # デフォルト
    max_description_length = 1024  # デフォルト
    max_line_count = 500  # デフォルト

    # 最大文字数の抽出を試みる
    name_match = re.search(r'最大(\d+)文字.*name', bp_content) or re.search(r'name.*最大(\d+)文字', bp_content)
    if name_match:
        max_name_length = int(name_match.group(1))

    desc_match = re.search(r'最大(\d+)文字.*description', bp_content) or re.search(r'description.*最大(\d+)文字', bp_content)
    if desc_match:
        max_description_length = int(desc_match.group(1))

    line_match = re.search(r'(\d+)行以下', bp_content)
    if line_match:
        max_line_count = int(line_match.group(1))

    # チェックリスト項目に基づいて動的にチェック
    for item in checklist:
        item_lower = item.lower()

        # nameチェック
        if 'name' in item_lower and ('小文字' in item or '数字' in item or 'ハイフン' in item):
            name = frontmatter.get('name', '')
            if not name:
                issues.append({
                    "check": "name",
                    "status": "missing",
                    "recommendation": item,
                    "source": "best-practice-checklist"
                })
            elif not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', name):
                issues.append({
                    "check": "name",
                    "status": "invalid_format",
                    "recommendation": item,
                    "source": "best-practice-checklist"
                })
            elif len(name) > max_name_length:
                issues.append({
                    "check": "name",
                    "status": "too_long",
                    "recommendation": f"nameは最大{max_name_length}文字です（現在: {len(name)}文字）",
                    "source": "best-practice-checklist"
                })

        # descriptionチェック
        if 'description' in item_lower:
            description = frontmatter.get('description', '')
            if not description:
                issues.append({
                    "check": "description",
                    "status": "missing",
                    "recommendation": item,
                    "source": "best-practice-checklist"
                })
            elif len(description) > max_description_length:
                issues.append({
                    "check": "description",
                    "status": "too_long",
                    "recommendation": f"descriptionは最大{max_description_length}文字です（現在: {len(description)}文字）",
                    "source": "best-practice-checklist"
                })

        # allowed-toolsチェック
        if 'allowed-tools' in item_lower:
            if not frontmatter.get('allowed-tools'):
                issues.append({
                    "check": "allowed_tools",
                    "status": "missing",
                    "recommendation": item,
                    "source": "best-practice-checklist"
                })

        # 行数チェック
        if '行以下' in item or 'line' in item_lower:
            if line_count > max_line_count:
                issues.append({
                    "check": "line_count",
                    "status": "too_long",
                    "recommendation": f"SKILL.mdは{max_line_count}行以下に保ってください（現在: {line_count}行）",
                    "source": "best-practice-checklist"
                })

        # 発動条件チェック
        # NOTE: Claude公式ドキュメントでは「発動条件」セクションは推奨されていない
        # 発動条件は description フィールドに含めるべき
        # このチェックは廃止（2026-01-20）
        # if '発動条件' in item:
        #     if '## 発動条件' not in content and '## Trigger' not in content.lower():
        #         issues.append({
        #             "check": "trigger_section",
        #             "status": "missing",
        #             "recommendation": item,
        #             "source": "best-practice-checklist"
        #         })

    return issues


def check_agent_quality(
    path: Path,
    frontmatter: dict,
    content: str,
    best_practice: dict
) -> list[dict]:
    """サブエージェントの品質チェック（BEST-PRACTICES-AGENT準拠）

    ベストプラクティスから読み取ったチェックリストに基づいてチェックを実行
    """
    issues = []
    checklist = best_practice.get("checklist", [])

    # チェックリスト項目に基づいて動的にチェック
    for item in checklist:
        item_lower = item.lower()

        # nameチェック
        if 'name' in item_lower and ('小文字' in item or 'ハイフン' in item):
            name = frontmatter.get('name', '')
            if not name:
                issues.append({
                    "check": "name",
                    "status": "missing",
                    "recommendation": item,
                    "source": "best-practice-checklist"
                })
            elif not re.match(r'^[a-z]+(-[a-z]+)*$', name):
                issues.append({
                    "check": "name",
                    "status": "invalid_format",
                    "recommendation": item,
                    "source": "best-practice-checklist"
                })

        # descriptionチェック
        if 'description' in item_lower:
            if not frontmatter.get('description'):
                issues.append({
                    "check": "description",
                    "status": "missing",
                    "recommendation": item,
                    "source": "best-practice-checklist"
                })

        # toolsチェック
        if 'tools' in item_lower and 'allowed' not in item_lower:
            # toolsフィールドの存在は必須ではないが、設定されている場合は確認
            pass

        # modelチェック
        if 'model' in item_lower:
            model = frontmatter.get('model', '')
            if model and model not in ['haiku', 'sonnet', 'opus', 'inherit']:
                issues.append({
                    "check": "model",
                    "status": "invalid_value",
                    "recommendation": item,
                    "source": "best-practice-checklist"
                })

        # システムプロンプト/手順チェック
        if '手順' in item or 'システムプロンプト' in item:
            # 手順セクションの存在確認
            # NOTE: 「## 実行手順」「## 手順」「## Steps」などにマッチ
            has_steps = bool(re.search(r'(##?\s*.*手順|##?\s*Steps|##?\s*When invoked)', content, re.IGNORECASE))
            if not has_steps:
                issues.append({
                    "check": "steps_section",
                    "status": "missing",
                    "recommendation": item,
                    "source": "best-practice-checklist"
                })

    return issues


def check_common_quality(path: Path, content: str) -> list[dict]:
    """共通の品質チェック"""
    issues = []

    # フロントマター形式チェック
    lines = content.split('\n')
    if not lines or lines[0].strip() != '---':
        issues.append({
            "check": "frontmatter",
            "status": "missing",
            "recommendation": "フロントマター（---で囲む）を追加してください",
            "source": "common"
        })

    # kebab-case命名チェック
    filename = path.stem
    if filename != "SKILL" and not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', filename):
        issues.append({
            "check": "filename",
            "status": "invalid_format",
            "recommendation": f"ファイル名はkebab-caseで命名してください（現在: {filename}）",
            "source": "common"
        })

    return issues


def analyze_file(
    path: Path,
    resource_type: str,
    best_practices: dict
) -> dict[str, Any]:
    """ファイルを分析する"""
    content = path.read_text(encoding='utf-8')
    frontmatter = parse_frontmatter(content)
    line_count = len(content.split('\n'))

    file_info = {
        "path": str(path),
        "name": path.stem,
        "frontmatter": frontmatter,
        "line_count": line_count,
        "quality_issues": []
    }

    # description と allowed_tools を抽出
    file_info["description"] = frontmatter.get('description', '')
    file_info["allowed_tools"] = frontmatter.get('allowed-tools', [])

    # 共通チェック
    file_info["quality_issues"].extend(check_common_quality(path, content))

    # リソースタイプ別チェック（ベストプラクティスを参照）
    best_practice = best_practices.get(resource_type, {})

    if resource_type == "slash_commands":
        file_info["quality_issues"].extend(
            check_slash_command_quality(path, frontmatter, content, best_practice)
        )
    elif resource_type == "skills":
        file_info["quality_issues"].extend(
            check_skill_quality(path, frontmatter, content, line_count, best_practice)
        )
    elif resource_type == "agents":
        file_info["quality_issues"].extend(
            check_agent_quality(path, frontmatter, content, best_practice)
        )

    return file_info


def analyze_repository(repo_path: Path) -> dict[str, Any]:
    """リポジトリ全体を分析する"""

    # ベストプラクティスを読み込む
    best_practices = load_best_practices(repo_path)

    result = {
        "summary": {
            "slash_commands": 0,
            "agents": 0,
            "skills": 0,
            "total": 0
        },
        "best_practice_references": {
            "skills": best_practices["skills"]["path"],
            "slash_commands": best_practices["slash_commands"]["path"],
            "agents": best_practices["agents"]["path"]
        },
        "best_practice_checklists": {
            "skills": best_practices["skills"]["checklist"],
            "slash_commands": best_practices["slash_commands"]["checklist"],
            "agents": best_practices["agents"]["checklist"]
        },
        "files": {
            "slash_commands": [],
            "agents": [],
            "skills": []
        },
        "quality_issues": [],
        "refactoring_candidates": {
            "merge_candidates": [],
            "extract_candidates": []
        }
    }

    # commands
    slash_commands_dir = repo_path / "commands"
    if slash_commands_dir.exists():
        for path in slash_commands_dir.glob("*.md"):
            file_info = analyze_file(path, "slash_commands", best_practices)
            result["files"]["slash_commands"].append(file_info)
            result["summary"]["slash_commands"] += 1

    # agents
    agents_dir = repo_path / "agents"
    if agents_dir.exists():
        for path in agents_dir.glob("*.md"):
            file_info = analyze_file(path, "agents", best_practices)
            result["files"]["agents"].append(file_info)
            result["summary"]["agents"] += 1

    # skills
    skills_dir = repo_path / "skills"
    if skills_dir.exists():
        for skill_dir in skills_dir.iterdir():
            if skill_dir.is_dir():
                skill_file = skill_dir / "SKILL.md"
                if skill_file.exists():
                    file_info = analyze_file(skill_file, "skills", best_practices)
                    result["files"]["skills"].append(file_info)
                    result["summary"]["skills"] += 1

    # 合計
    result["summary"]["total"] = (
        result["summary"]["slash_commands"] +
        result["summary"]["agents"] +
        result["summary"]["skills"]
    )

    # 品質問題の集約
    for resource_type, file_list in result["files"].items():
        best_practice_ref = result["best_practice_references"].get(
            resource_type,
            ""
        )
        for file_info in file_list:
            if file_info["quality_issues"]:
                result["quality_issues"].append({
                    "file": file_info["path"],
                    "resource_type": resource_type,
                    "best_practice_ref": best_practice_ref,
                    "issues": file_info["quality_issues"]
                })

    return result


def main():
    """ai-toolkitリポジトリのプロンプトを分析する（パス固定）"""
    # スクリプト配置場所から ai-toolkit リポジトリのルートを決定
    # skills/manage-resources/analyze_prompts.py → 2階層上がリポジトリルート
    script_path = Path(__file__).resolve()
    repo_path = script_path.parent.parent.parent

    # ai-toolkitリポジトリであることを確認
    if not (repo_path / "CLAUDE.md").exists():
        print(f"Error: ai-toolkitリポジトリが見つかりません: {repo_path}", file=sys.stderr)
        print("このスクリプトはai-toolkit/skills/manage-resources/に配置して実行してください", file=sys.stderr)
        sys.exit(1)

    result = analyze_repository(repo_path)

    # JSON出力
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
