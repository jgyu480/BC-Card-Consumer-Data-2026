import pandas as pd

df = pd.read_parquet('store_match_candidates.parquet')
matched = df[df['match_confidence'].isin(['high', 'medium'])]
counts = matched.groupby('brand_name_raw').size().sort_values()

print("=== 매칭 건수 적은 순 (0~5건, 확인 필요) ===")
print(counts[counts <= 5].to_string())
print()
print("전체 매칭된 브랜드 수:", counts.shape[0])
print("전체 브랜드 수(178개) 중 매칭 0건인 브랜드도 있는지 별도 확인 필요")
