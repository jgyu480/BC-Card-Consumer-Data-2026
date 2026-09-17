# -*- coding: utf-8 -*-
"""
absolute_fit_percentile 등이 실제로 순위/후보수 형태로 딱딱 끊어지는지 확인.
"""
import pandas as pd

PARQUET_PATH = r"C:\Users\lucy0\Documents\YONSEI\YBIGTA\공모전\BC-Card-Consumer-Data-2026\PART-III\MODEL-01\outputs\final_model_v3_1\model01_final_recommendations_v3_1.parquet"

df = pd.read_parquet(PARQUET_PATH)

# 곤트란쉐리에 브랜드만 뽑아서 확인 (available_recommendation_count=20)
sample = df[df["brand_name"] == "곤트란쉐리에(Gontran Cherrier)"][
    ["area_name", "absolute_fit_percentile", "available_recommendation_count"]
].head(10)

pd.set_option("display.float_format", lambda x: f"{x:.10f}")
print(sample)

print("\n=== 1/20, 2/20 ... 배수와 비교 ===")
n = 20
for i in range(1, 6):
    print(f"{i}/{n} = {i/n}")