import pandas as pd

df = pd.read_parquet(r"C:\Users\lucy0\Documents\YONSEI\YBIGTA\공모전\BC-Card-Consumer-Data-2026\PART-III\MODEL-01\outputs\final_model_v3_1\model01_final_recommendations_v3_1.parquet")

# caution_flags 전체 고유 코드
caution_unique = sorted(df['caution_flags'].str.split(r' \| ').explode().unique())
print("=== caution_flags 전체 코드 ===")
for c in caution_unique:
    print(c)

# positive_drivers의 요인명(key)만 추출
driver_keys = sorted(df['positive_drivers'].str.split(r' \| ').explode().str.split('=').str[0].unique())
print("\n=== positive_drivers 요인명 ===")
for d in driver_keys:
    print(d)

# store_size_status, context_quality 등 다른 코드성 컬럼도 궁금하면 같이 확인 가능
print("\n=== profile_stability 값 ===")
print(df['profile_stability'].unique())

print("\n=== context_quality 값 ===")
print(df['context_quality'].unique())