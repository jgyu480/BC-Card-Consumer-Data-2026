import pandas as pd

df = pd.read_parquet('store_match_candidates.parquet')
review = df[df['review_needed']].sort_values(['match_confidence', 'brand_name_raw'])
review[[
    'brand_name_raw', '상호명', '지점명', '시도명', '시군구명',
    'match_method', 'match_confidence', 'review_reason'
]].to_csv('review_needed_full.csv', index=False, encoding='utf-8-sig')

print(f"저장 완료: review_needed_full.csv ({len(review)}건)")
