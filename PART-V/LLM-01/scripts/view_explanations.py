# -*- coding: utf-8 -*-
"""
llm01_final_explanations.json 파일에서 각 브랜드의 explanation만
줄바꿈 그대로 살려서 터미널에 보기 좋게 출력한다.
"""
import json

INPUT_PATH = "llm01_final_explanations.json"

with open(INPUT_PATH, "r", encoding="utf-8") as f:
    results = json.load(f)

for item in results:
    brand = item["brand_name"]
    explanation = item.get("explanation")
    status = item.get("status")

    print("=" * 70)
    print(f"[{brand}]  (status: {status})")
    print("=" * 70)
    if explanation:
        print(explanation)
    else:
        print("(설명 없음 - 에러 발생)")
    print()