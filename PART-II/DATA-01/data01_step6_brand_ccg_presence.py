"""
DATA-01 : brand_ccg_presence.parquet 생성

brand_store_master.parquet에 이미 ccg_id가 포함되어 있으므로,
원본 CSV를 다시 읽지 않고 바로 집계한다.

출력: brand_ccg_presence.parquet
  - brand_id, ccg_id, ccg_nm, store_cnt, brand_total_store_cnt, share, data_ref_date
"""

import pandas as pd

MASTER_PATH = "brand_store_master.parquet"
OUTPUT_PATH = "brand_ccg_presence.parquet"
DATA_REF_DATE = "2026-06-30"


def build_brand_ccg_presence(master_df: pd.DataFrame) -> pd.DataFrame:
    # 현재 유효한(제외되지 않은) 매장만 대상 -> "현재 입점 현황"을 왜곡하지 않기 위해
    active = master_df[master_df["store_status"] != "제외"].copy()

    grouped = active.groupby(["brand_id", "ccg_id", "ccg_nm"]).size().reset_index(name="store_cnt")

    brand_totals = grouped.groupby("brand_id")["store_cnt"].sum().reset_index(name="brand_total_store_cnt")
    grouped = grouped.merge(brand_totals, on="brand_id", how="left")
    grouped["share"] = grouped["store_cnt"] / grouped["brand_total_store_cnt"]

    grouped["data_ref_date"] = DATA_REF_DATE

    return grouped[["brand_id", "ccg_id", "ccg_nm", "store_cnt", "brand_total_store_cnt", "share", "data_ref_date"]]


if __name__ == "__main__":
    print("brand_store_master.parquet 로딩...")
    master_df = pd.read_parquet(MASTER_PATH)
    print(f"  -> {len(master_df)}건 로딩 완료")

    print("\nbrand_id x ccg_id 집계 수행...")
    result_df = build_brand_ccg_presence(master_df)
    print(f"  -> {len(result_df)}개 브랜드-시군구 조합 생성")
    print(f"  -> 고유 브랜드 수: {result_df['brand_id'].nunique()}개")
    print(f"  -> 고유 시군구 수: {result_df['ccg_id'].nunique()}개")

    print("\n샘플 5개:")
    print(result_df.sample(5, random_state=1).to_string())

    result_df.to_parquet(OUTPUT_PATH, index=False)
    print(f"\n-> {OUTPUT_PATH} 저장 완료")
