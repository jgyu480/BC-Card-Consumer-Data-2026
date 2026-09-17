# -*- coding: utf-8 -*-
"""
24개 브랜드의 상위 3개 상권(TOP_N=3)에서, 동점 그룹 패턴을 집계한다.
- 1위 그룹 크기 (1위인 상권이 몇 개인지)
- 2위 그룹 크기
- 3위 그룹 크기
- 전체 몇 개 브랜드가 순수 "1,2,3위 각각 1개씩"(동점 없음)인지
"""
import pandas as pd
from collections import Counter

PARQUET_PATH = r"C:\Users\lucy0\Documents\YONSEI\YBIGTA\공모전\BC-Card-Consumer-Data-2026\PART-III\MODEL-01\outputs\final_model_v3_1\model01_final_recommendations_v3_1.parquet"

TIE_THRESHOLD = 0.003
TOP_N = 3


def compute_adjusted_ranks(rows, threshold=TIE_THRESHOLD):
    rows_sorted = sorted(rows, key=lambda r: -r["final_suitability_score"])
    result = []
    current_rank = 1
    for idx, row in enumerate(rows_sorted):
        if idx == 0:
            result.append((current_rank, row))
            continue
        prev_score = rows_sorted[idx - 1]["final_suitability_score"]
        this_score = row["final_suitability_score"]
        if abs(prev_score - this_score) > threshold:
            current_rank += 1
        result.append((current_rank, row))
    return result


df = pd.read_parquet(PARQUET_PATH)

no_tie_count = 0
tie_1_count = 0   # 1위 그룹 크기 >= 2
tie_2_count = 0   # 2위 그룹 크기 >= 2
tie_3_count = 0   # 3위 그룹 크기 >= 2 (자른 3개 안에서)
all_same_rank_count = 0  # 상위 3개가 전부 같은 순위(=1위)인 경우

detail_rows = []

for brand, group in df.groupby("brand_name"):
    rows = group.to_dict("records")
    ranked = compute_adjusted_ranks(rows)
    top3 = ranked[:TOP_N]

    rank_counts = Counter(r for r, _ in top3)

    has_tie_1 = rank_counts.get(1, 0) >= 2
    has_tie_2 = rank_counts.get(2, 0) >= 2
    has_tie_3 = rank_counts.get(3, 0) >= 2
    all_same = len(rank_counts) == 1

    if has_tie_1:
        tie_1_count += 1
    if has_tie_2:
        tie_2_count += 1
    if has_tie_3:
        tie_3_count += 1
    if all_same:
        all_same_rank_count += 1
    if not has_tie_1 and not has_tie_2 and not has_tie_3:
        no_tie_count += 1

    detail_rows.append({
        "brand": brand,
        "rank_pattern": dict(sorted(rank_counts.items())),
    })

print("=== 브랜드별 순위 그룹 패턴 ===")
for d in detail_rows:
    print(f"{d['brand']}: {d['rank_pattern']}")

print("\n=== 집계 ===")
print(f"총 브랜드 수: 24")
print(f"동점 전혀 없음 (1,2,3위 각 1개): {no_tie_count}개")
print(f"1위 그룹에 동점 있음: {tie_1_count}개")
print(f"2위 그룹에 동점 있음: {tie_2_count}개")
print(f"3위 그룹에 동점 있음: {tie_3_count}개")
print(f"상위 3개가 전부 같은 순위(전부 1위): {all_same_rank_count}개")