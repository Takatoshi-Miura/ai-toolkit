#!/usr/bin/env python3
"""食事記録の栄養計算スクリプト

Usage:
    python3 calc_nutrition.py --input meals.json

meals.json の形式:
[
  {"name": "白米 中盛り", "calorie": 350, "protein": 6, "fat": 1, "carb": 78},
  ...
]
（各食品の栄養値はClaudeが一般的な栄養成分表に基づき事前に見積もり、
 このJSONに変換した上でスクリプトに渡す）

出力: 合計カロリー・PFC（g）・PFCエネルギー比率（%）
"""

import argparse
import json
import sys


def parse_args():
    parser = argparse.ArgumentParser(description="食事記録から栄養合計を計算")
    parser.add_argument("--input", required=True, help="食品リストのJSONファイルパス")
    return parser.parse_args()


def main():
    args = parse_args()

    with open(args.input, encoding="utf-8") as f:
        items = json.load(f)

    total_calorie = sum(item.get("calorie", 0) for item in items)
    total_protein = sum(item.get("protein", 0) for item in items)
    total_fat = sum(item.get("fat", 0) for item in items)
    total_carb = sum(item.get("carb", 0) for item in items)

    # PFCの各エネルギー換算（たんぱく質4kcal/g、脂質9kcal/g、炭水化物4kcal/g）
    protein_kcal = total_protein * 4
    fat_kcal = total_fat * 9
    carb_kcal = total_carb * 4
    pfc_total_kcal = protein_kcal + fat_kcal + carb_kcal

    def ratio(kcal: float) -> float:
        return round(kcal / pfc_total_kcal * 100, 1) if pfc_total_kcal else 0.0

    result = {
        "success": True,
        "totalCalorie": round(total_calorie, 1),
        "totalProteinG": round(total_protein, 1),
        "totalFatG": round(total_fat, 1),
        "totalCarbG": round(total_carb, 1),
        "pfcRatio": {
            "proteinPercent": ratio(protein_kcal),
            "fatPercent": ratio(fat_kcal),
            "carbPercent": ratio(carb_kcal),
        },
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
