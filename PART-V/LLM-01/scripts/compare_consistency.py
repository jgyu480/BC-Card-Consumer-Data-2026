# -*- coding: utf-8 -*-
"""
같은 입력에 대해 API를 두 번 호출한 결과를 비교해서 일관성을 확인한다.
"""
import json

FILE_1 = "llm01_final_explanations_v1.json"
FILE_2 = "llm01_final_explanations_v2.json"

with open(FILE_1, "r", encoding="utf-8") as f:
    results_1 = {r["brand_name"]: r["explanation"] for r in json.load(f)}

with open(FILE_2, "r", encoding="utf-8") as f:
    results_2 = {r["brand_name"]: r["explanation"] for r in json.load(f)}

identical_count = 0
different_count = 0

for brand in results_1:
    exp1 = results_1.get(brand)
    exp2 = results_2.get(brand)
    same = exp1 == exp2

    if same:
        identical_count += 1
    else:
        different_count += 1

    print(f"[{brand}] 완전히 동일: {same}")

print(f"\n=== 요약 ===")
print(f"완전히 동일한 브랜드: {identical_count}/{len(results_1)}")
print(f"표현이 달라진 브랜드: {different_count}/{len(results_1)}")

# 차이가 있는 브랜드 중 하나만 예시로 자세히 비교
for brand in results_1:
    exp1 = results_1.get(brand)
    exp2 = results_2.get(brand)
    if exp1 != exp2:
        print(f"\n=== 예시: [{brand}] 1차 vs 2차 ===")
        print("--- 1차 ---")
        print(exp1)
        print("\n--- 2차 ---")
        print(exp2)
        break