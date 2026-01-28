#!/usr/bin/env python3
"""
因子水準の組み合わせパターン生成スクリプト

使用方法:
    python3 generate_combinations.py '<factors_json>' [--max-combinations 300]

入力形式:
    {
        "因子A": ["A1", "A2", "A3"],
        "因子B": ["B1", "B2"],
        "ワンパス": ["D1", "D2", "D3"],
        "期待値": ["E1", "E2"]
    }

出力形式:
    {
        "success": true,
        "factorNames": ["因子A", "因子B"],
        "combinations": [["A1", "B1"], ["A1", "B2"], ...],
        "onepassCases": [{"factor": "ワンパス", "level": "D1"}, ...],
        "excludedFactors": ["期待値"],
        "totalCount": 15,
        "warning": null
    }

除外ルール:
    - 因子名に「OS」を含む場合: excludedFactors に分類（組み合わせ対象外）
    - 因子名に「期待値」を含む場合: excludedFactors に分類（組み合わせ対象外）
    - 因子名に「ワンパス」を含む場合: onepassCases に分類（個別テスト項目）
"""

import argparse
import json
import sys
from itertools import product
from typing import Any


def parse_factors(factors_json: str) -> list[dict]:
    """因子JSONをパースする

    入力形式: {"因子名": ["水準1", "水準2"], ...}
    出力形式: [{"name": "因子名", "levels": ["水準1", "水準2"]}, ...]
    """
    try:
        data = json.loads(factors_json)
        if not isinstance(data, dict):
            raise ValueError("JSONオブジェクトである必要があります")

        # シンプル形式を内部形式に変換（定義順を保持）
        factors = []
        for name, levels in data.items():
            if not isinstance(levels, list):
                raise ValueError(f"因子 '{name}' の水準はリストである必要があります")
            factors.append({"name": name, "levels": levels})

        return factors
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON解析エラー: {e}")


def categorize_factors(factors: list[dict]) -> tuple[list[dict], list[dict], list[dict]]:
    """因子を通常因子、ワンパス因子、除外因子に分類する"""
    normal_factors = []
    onepass_factors = []
    excluded_factors = []

    for factor in factors:
        name = factor.get("name", "")
        levels = factor.get("levels", [])

        if "期待値" in name or "OS" in name:
            excluded_factors.append(factor)
        elif "ワンパス" in name:
            onepass_factors.append(factor)
        else:
            normal_factors.append(factor)

    return normal_factors, onepass_factors, excluded_factors


def generate_cartesian_product(factors: list[dict]) -> list[list[str]]:
    """通常因子の直積（定義順）を生成する"""
    if not factors:
        return []

    # 各因子の水準リストを取得
    levels_list = [factor.get("levels", []) for factor in factors]

    # 空の水準リストがある場合は除外
    levels_list = [levels for levels in levels_list if levels]

    if not levels_list:
        return []

    # 直積を生成（定義順を保持）
    combinations = list(product(*levels_list))

    # タプルをリストに変換
    return [list(combo) for combo in combinations]


def generate_onepass_cases(factors: list[dict]) -> list[dict]:
    """ワンパス因子のケースを生成する"""
    cases = []
    for factor in factors:
        name = factor.get("name", "")
        levels = factor.get("levels", [])
        for level in levels:
            cases.append({"factor": name, "level": level})
    return cases


def generate_combinations(
    factors_json: str,
    max_combinations: int = 300
) -> dict[str, Any]:
    """
    因子水準データから組み合わせパターンを生成する

    Args:
        factors_json: 因子水準データのJSON文字列
        max_combinations: 組み合わせの上限数（デフォルト: 300）

    Returns:
        組み合わせ結果の辞書
    """
    try:
        # JSONをパース（シンプル形式から内部形式に変換）
        factors = parse_factors(factors_json)

        # 因子を分類
        normal_factors, onepass_factors, expected_factors = categorize_factors(factors)

        # 通常因子の直積を生成
        combinations = generate_cartesian_product(normal_factors)

        # ワンパスケースを生成
        onepass_cases = generate_onepass_cases(onepass_factors)

        # 総件数を計算
        total_count = len(combinations) + len(onepass_cases)

        # 警告メッセージ
        warning = None

        # 上限チェック
        if total_count > max_combinations:
            warning = f"組み合わせ数 ({total_count}) が上限 ({max_combinations}) を超えています。切り詰めました。"

            # 通常の組み合わせを優先して切り詰め
            remaining = max_combinations
            if len(combinations) > remaining:
                combinations = combinations[:remaining]
                onepass_cases = []
            else:
                remaining -= len(combinations)
                onepass_cases = onepass_cases[:remaining]

            total_count = len(combinations) + len(onepass_cases)

        # 除外された因子名を取得
        excluded_factor_names = [f.get("name", "") for f in expected_factors]

        # 因子名リストを取得（組み合わせの順序を示す）
        factor_names = [f.get("name", "") for f in normal_factors]

        return {
            "success": True,
            "factorNames": factor_names,
            "combinations": combinations,
            "onepassCases": onepass_cases,
            "excludedFactors": excluded_factor_names,
            "totalCount": total_count,
            "warning": warning
        }

    except ValueError as e:
        return {
            "success": False,
            "error": str(e),
            "factorNames": [],
            "combinations": [],
            "onepassCases": [],
            "excludedFactors": [],
            "totalCount": 0,
            "warning": None
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"予期しないエラー: {e}",
            "factorNames": [],
            "combinations": [],
            "onepassCases": [],
            "excludedFactors": [],
            "totalCount": 0,
            "warning": None
        }


def main():
    parser = argparse.ArgumentParser(
        description="因子水準の組み合わせパターンを生成"
    )
    parser.add_argument(
        "factors_json",
        help="因子水準データのJSON文字列"
    )
    parser.add_argument(
        "--max-combinations",
        type=int,
        default=300,
        help="組み合わせの上限数（デフォルト: 300）"
    )

    args = parser.parse_args()

    result = generate_combinations(
        args.factors_json,
        args.max_combinations
    )

    # JSON出力（UTF-8対応）
    print(json.dumps(result, ensure_ascii=False, indent=2))

    # エラー時は非ゼロで終了
    if not result.get("success"):
        sys.exit(1)


if __name__ == "__main__":
    main()
