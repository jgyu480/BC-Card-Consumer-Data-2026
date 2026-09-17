# -*- coding: utf-8 -*-
import pandas as pd

PARQUET_PATH = r"C:\Users\lucy0\Documents\YONSEI\YBIGTA\공모전\BC-Card-Consumer-Data-2026\PART-III\MODEL-01\outputs\final_model_v3_1\model01_final_recommendations_v3_1.parquet"

df = pd.read_parquet(PARQUET_PATH)

sample = df[df["brand_name"] == "빵굼터"][
    ["area_name", "absolute_fit_percentile", "brand_specificity_percentile", "low_competition_risk_percentile"]
]

pd.set_option("display.float_format", lambda x: f"{x:.15f}")
pd.set_option("display.max_rows", None)
print(sample)