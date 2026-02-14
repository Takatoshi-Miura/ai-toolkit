#!/usr/bin/env python3
"""
JaCoCoレポートからInstruction Coverageを抽出するスクリプト

Usage:
    python3 jacoco_coverage_extractor.py <report_dir> [file1.kt file2.kt ...]

Arguments:
    report_dir: JaCoCoレポートのルートディレクトリ
                （例: app/build/reports/jacoco）
    file1.kt:   抽出対象のファイル名（省略時は全クラスを出力）

Output:
    JSON形式で各ファイルのInstruction Coverage %を出力

Note:
    - generateCoverageReportOnly タスクで生成されたレポートを使用すること
    - html/ サブディレクトリではなく、ルートディレクトリのレポートを参照する
    - Instruction Coverage（命令カバレッジ）を抽出する（JaCoCoレポートのデフォルト表示と同一）
"""
import json
import re
import sys
from pathlib import Path
from typing import Optional


def find_package_index_files(report_dir: Path) -> list:
    """パッケージごとのindex.htmlを検索する（html/サブディレクトリを除外）"""
    index_files = []
    for index_html in report_dir.glob("*/index.html"):
        # html/ サブディレクトリ配下は除外（古いレポートの可能性）
        if "html" in index_html.parent.name:
            continue
        # ルート直下の index.html は除外（全体サマリー）
        if index_html.parent == report_dir:
            continue
        index_files.append(index_html)
    return index_files


def extract_coverage_from_index(index_html: Path) -> list:
    """パッケージindex.htmlからクラスごとのInstruction Coverageを抽出する"""
    content = index_html.read_text(encoding="utf-8")
    package_name = index_html.parent.name

    results = []

    # テーブル行からクラス名とctr2（Instruction Coverage %）を抽出
    # パターン: <a href="ClassName.html" class="el_class">ClassName</a> ... <td class="ctr2" ...>XX%</td>
    row_pattern = re.compile(
        r'<a\s+href="[^"]*?\.html"\s+class="el_class">([^<]+)</a>'
        r'.*?'
        r'<td\s+class="ctr2"\s+id="[^"]*">(\d+)%</td>',
        re.DOTALL,
    )

    for match in row_pattern.finditer(content):
        class_name = match.group(1).strip()
        coverage_percent = int(match.group(2))
        results.append({
            "class_name": class_name,
            "package": package_name,
            "coverage_percent": coverage_percent,
        })

    return results


def match_file_to_classes(
    target_file: str,
    all_classes: list,
) -> dict:
    """ファイル名に対応するクラスを検索する

    sealed class のサブクラスも親ファイルにマッチさせる。
    例: ContinuousReceiptAction.NavigateToLogin → ContinuousReceiptAction.kt

    Returns:
        {"exact": クラスdict or None, "subclasses": [クラスdict...]}
    """
    base_name = target_file.replace(".kt", "")
    exact = None
    subclasses = []
    for cls in all_classes:
        cn = cls["class_name"]
        # 完全一致
        if cn == base_name:
            exact = cls
        # サブクラス（ClassName.SubClass 形式）
        elif cn.startswith(f"{base_name}."):
            subclasses.append(cls)
    return {"exact": exact, "subclasses": subclasses}


def aggregate_coverage(classes: list, all_classes_raw: dict) -> Optional[int]:
    """複数クラスのカバレッジを命令数ベースで集約する

    index.htmlからmissed/coveredの命令数を取得して正確に計算する。
    取得できない場合は単純平均で代替する。
    """
    if not classes:
        return None
    if len(classes) == 1:
        return classes[0]["coverage_percent"]

    # 各クラスの命令数情報がある場合はそれを使う
    total_missed = 0
    total_covered = 0
    has_instruction_data = False

    for cls in classes:
        key = f"{cls['package']}:{cls['class_name']}"
        if key in all_classes_raw:
            missed, covered = all_classes_raw[key]
            total_missed += missed
            total_covered += covered
            has_instruction_data = True

    if has_instruction_data and (total_missed + total_covered) > 0:
        return round(total_covered / (total_missed + total_covered) * 100)

    # フォールバック: 単純平均
    return round(sum(c["coverage_percent"] for c in classes) / len(classes))


def extract_instruction_counts(index_html: Path) -> dict:
    """パッケージindex.htmlからクラスごとの命令数（missed, covered）を抽出する"""
    content = index_html.read_text(encoding="utf-8")
    package_name = index_html.parent.name
    results = {}

    # barセルからmissed/covered命令数を抽出
    # <a ...>ClassName</a> ... <td class="bar" ...>
    #   <img ... title="MISSED" .../><img ... title="COVERED" .../>
    # </td>
    row_pattern = re.compile(
        r'<a\s+href="[^"]*?\.html"\s+class="el_class">([^<]+)</a>'
        r'.*?'
        r'<td\s+class="bar"\s+id="[^"]*">(.*?)</td>',
        re.DOTALL,
    )

    for match in row_pattern.finditer(content):
        class_name = match.group(1).strip()
        bar_cell = match.group(2)

        # title属性から命令数を抽出
        img_pattern = re.compile(r'title="(\d+)"')
        counts = img_pattern.findall(bar_cell)

        if len(counts) == 2:
            missed = int(counts[0])
            covered = int(counts[1])
            key = f"{package_name}:{class_name}"
            results[key] = (missed, covered)
        elif len(counts) == 1:
            # 1つのバーのみ（100% or 0%）
            # redbar のみ → 全部missed、greenbar のみ → 全部covered
            if "redbar" in bar_cell and "greenbar" not in bar_cell:
                key = f"{package_name}:{class_name}"
                results[key] = (int(counts[0]), 0)
            elif "greenbar" in bar_cell and "redbar" not in bar_cell:
                key = f"{package_name}:{class_name}"
                results[key] = (0, int(counts[0]))

    return results


def analyze(report_dir: str, target_files: Optional[list] = None) -> dict:
    """JaCoCoレポートを解析してカバレッジ情報を返す"""
    report_path = Path(report_dir).resolve()

    if not report_path.exists():
        return {"success": False, "error": f"レポートディレクトリが見つかりません: {report_path}"}

    index_files = find_package_index_files(report_path)
    if not index_files:
        # html/ サブディレクトリにフォールバック
        html_dir = report_path / "html"
        if html_dir.exists():
            for index_html in html_dir.glob("*/index.html"):
                if index_html.parent.name != "html":
                    index_files.append(index_html)

    if not index_files:
        return {"success": False, "error": "JaCoCoレポートのindex.htmlが見つかりません"}

    # 全クラスのカバレッジを抽出
    all_classes = []
    all_classes_raw = {}
    for index_html in index_files:
        all_classes.extend(extract_coverage_from_index(index_html))
        all_classes_raw.update(extract_instruction_counts(index_html))

    if not all_classes:
        return {"success": False, "error": "カバレッジデータが見つかりません"}

    # 対象ファイルが指定されていない場合は全クラスを返す
    if not target_files:
        return {
            "success": True,
            "report_dir": str(report_path),
            "files": [
                {
                    "file": f"{c['class_name']}.kt",
                    "package": c["package"],
                    "coverage_percent": c["coverage_percent"],
                }
                for c in sorted(all_classes, key=lambda x: x["class_name"])
            ],
            "not_found": [],
        }

    # 対象ファイルごとにマッチング
    results = []
    not_found = []

    for target in target_files:
        match_result = match_file_to_classes(target, all_classes)
        exact = match_result["exact"]
        subclasses = match_result["subclasses"]

        if exact or subclasses:
            # メインクラスがあればその値を優先（HTMLレポート表示と一致）
            if exact:
                coverage = exact["coverage_percent"]
                package = exact["package"]
            else:
                # メインクラスがない場合のみサブクラスを集約
                coverage = aggregate_coverage(subclasses, all_classes_raw)
                package = subclasses[0]["package"]

            results.append({
                "file": target,
                "package": package,
                "coverage_percent": coverage,
                "subclasses": [
                    {"name": c["class_name"], "coverage_percent": c["coverage_percent"]}
                    for c in subclasses
                ] if subclasses else None,
            })
        else:
            not_found.append(target)

    return {
        "success": True,
        "report_dir": str(report_path),
        "files": results,
        "not_found": not_found,
    }


def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            "success": False,
            "error": "引数が不足しています",
            "usage": "python3 jacoco_coverage_extractor.py <report_dir> [file1.kt file2.kt ...]",
        }, ensure_ascii=False))
        sys.exit(1)

    report_dir = sys.argv[1]
    target_files = sys.argv[2:] if len(sys.argv) > 2 else None

    try:
        result = analyze(report_dir, target_files)
    except Exception as e:
        result = {"success": False, "error": str(e)}

    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not result.get("success"):
        sys.exit(1)


if __name__ == "__main__":
    main()
