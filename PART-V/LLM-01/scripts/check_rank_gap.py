# -*- coding: utf-8 -*-
"""
24개 브랜드 각각의 1~3위 final_suitability_score를 뽑아서
순위 간 점수 차이(gap)의 분포를 확인하는 스크립트.
"""
import pandas as pd

PARQUET_PATH = r"C:\Users\lucy0\Documents\YONSEI\YBIGTA\공모전\BC-Card-Consumer-Data-2026\PART-III\MODEL-01\outputs\final_model_v3_1\model01_final_recommendations_v3_1.parquet"

df = pd.read_parquet(PARQUET_PATH)

rows = []
for brand, group in df.groupby("brand_name"):
    top3 = group.sort_values("final_rank").head(3)
    scores = top3["final_suitability_score"].tolist()
    ranks = [int(r) for r in top3["final_rank"].tolist()]  # 1.0 -> 1 로 변환
    areas = top3["area_name"].tolist()

    row = {"brand_name": brand}
    for i in range(len(scores)):
        row[f"rank{ranks[i]}_score"] = scores[i]
        row[f"rank{ranks[i]}_area"] = areas[i]
    if len(scores) >= 2:
        row["gap_1_2"] = scores[0] - scores[1]
    if len(scores) >= 3:
        row["gap_2_3"] = scores[1] - scores[2]
    rows.append(row)

result_df = pd.DataFrame(rows)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)

# 혹시 rank1/2/3 컬럼이 없는 브랜드가 있을 수 있으니, 존재하는 컬럼만 안전하게 선택
cols_to_show = ["brand_name"] + [
    c for c in ["rank1_score", "rank2_score", "rank3_score", "gap_1_2", "gap_2_3"]
    if c in result_df.columns
]
print(result_df[cols_to_show])

if "gap_1_2" in result_df.columns:
    print("\n=== gap_1_2 통계 ===")
    print(result_df["gap_1_2"].describe())

if "gap_2_3" in result_df.columns:
    print("\n=== gap_2_3 통계 ===")
    print(result_df["gap_2_3"].describe())