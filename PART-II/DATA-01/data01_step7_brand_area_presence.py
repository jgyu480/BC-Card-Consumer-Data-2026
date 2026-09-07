"""
DATA-01 : brand_area_presence.parquet 생성

목적: 브랜드 x 서울 상권 단위로, 어느 상권에 몇 개 점포가 있는지 집계.
      MODEL-01이 "이미 입점한 상권"을 확인하고 추천에서 제외/검증하는 데 사용.

입력: brand_store_master.parquet (area_id가 4단계 공간조인으로 이미 채워져 있음)

출력: brand_area_presence.parquet
  - brand_id, area_id, area_name, district_cd, store_cnt, currently_active, data_ref_date
"""

import pandas as pd

MASTER_PATH = "brand_store_master.parquet"
OUTPUT_PATH = "brand_area_presence.parquet"
DATA_REF_DATE = "2026-06-30"


def build_brand_area_presence(master_df: pd.DataFrame) -> pd.DataFrame:
    # area_id가 있는 것만 대상 (서울 + 공간조인 성공한 매장만)
    seoul_matched = master_df[master_df["area_id"].notna()].copy()

    # 현재 유효한(제외되지 않은) 매장만 "현재 입점"으로 집계
    active = seoul_matched[seoul_matched["store_status"] != "제외"].copy()

    grouped = active.groupby(
        ["brand_id", "area_id", "area_name", "district_cd"]
    ).size().reset_index(name="store_cnt")

    grouped["currently_active"] = True  # 이 테이블에 있는 조합은 모두 현재 입점 확인된 것
    grouped["data_ref_date"] = DATA_REF_DATE

    return grouped[[
        "brand_id", "area_id", "area_name", "district_cd",
        "store_cnt", "currently_active", "data_ref_date"
    ]]


if __name__ == "__main__":
    print("brand_store_master.parquet 로딩...")
    master_df = pd.read_parquet(MASTER_PATH)
    print(f"  -> {len(master_df)}건 로딩 완료")

    print("\nbrand_id x area_id 집계 수행...")
    result_df = build_brand_area_presence(master_df)
    print(f"  -> {len(result_df)}개 브랜드-상권 조합 생성")
    print(f"  -> 고유 브랜드 수: {result_df['brand_id'].nunique()}개")
    print(f"  -> 고유 상권 수: {result_df['area_id'].nunique()}개")

    print("\n샘플 5개:")
    print(result_df.sample(5, random_state=1).to_string())

    result_df.to_parquet(OUTPUT_PATH, index=False)
    print(f"\n-> {OUTPUT_PATH} 저장 완료")
