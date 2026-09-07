"""
DATA-01 : 최종 산출물 변환 (DATA_SCHEMA.csv 공식 스키마에 맞춰 컬럼 정리)

입력: store_match_final.parquet (1~4단계 전체 결과)
출력: brand_store_master.parquet (공식 스키마 22개 컬럼)

주의:
- match_confidence는 공식 스키마 설명("high medium excluded")보다 세분화된
  4단계 체계(high/medium/medium_short_brand/low)를 그대로 유지한다.
  -> README에 이 확장된 값의 의미를 명시해야 한다.
- 원본 상세 컬럼(상호명, 지점명, 시도명 등)은 스키마에 없지만 검증/디버깅에
  유용하므로 접두어 "_raw_"를 붙여 참고용으로 함께 남긴다 (스키마 위반 아님,
  추가 컬럼은 허용되는 것으로 해석).
"""

import pandas as pd

INPUT_PATH = "store_match_final.parquet"
OUTPUT_PATH = "brand_store_master.parquet"

SOURCE_NAME = "소상공인시장진흥공단 상가(상권)정보"
SOURCE_DATE = "2026-06-30"


def determine_store_status(row) -> str:
    if row.get("excluded"):
        return "제외"
    if row.get("business_status") == "영업/정상":
        return "영업중"
    if row.get("business_status") == "폐업":
        return "제외"  # 폐업은 이미 excluded 처리되지만 방어적으로 한 번 더 확인
    return "미확인"  # 행안부 교차검증에서 확인되지 않음 (존재하지 않는다는 뜻은 아님)


def build_final_schema(df: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame()

    out["brand_id"] = df["brand_id"]
    out["brand_name"] = df["brand_name_raw"]
    out["store_id"] = df["상가업소번호"]
    out["store_name_raw"] = df["store_name_raw"]
    out["store_name_std"] = df["store_name_std"]

    out["address_raw"] = df["도로명주소"].where(df["도로명주소"].notna(), df["지번주소"])
    out["address_std"] = out["address_raw"].apply(
        lambda x: None if pd.isna(x) else __import__("re").sub(r"[^0-9A-Za-z가-힣]", "", str(x))
    )

    out["sido_nm"] = df["시도명"]
    out["ccg_nm"] = df["시군구명"]
    out["district_nm"] = df.apply(
        lambda r: r["시군구명"] if r["시도명"] == "서울특별시" else None, axis=1
    )

    # 공식 스키마엔 없지만, brand_ccg_presence/brand_area_presence 집계에 필요해
    # 참고용으로 함께 남긴다 (전국 시군구코드 = 서울 한정 자치구코드와 동일한 컬럼)
    out["ccg_id"] = df["시군구코드"]
    out["district_cd"] = df.apply(
        lambda r: r["시군구코드"] if r["시도명"] == "서울특별시" else None, axis=1
    )

    out["longitude"] = pd.to_numeric(df["경도"], errors="coerce")
    out["latitude"] = pd.to_numeric(df["위도"], errors="coerce")
    out["coordinate_source"] = SOURCE_NAME

    out["store_status"] = df.apply(determine_store_status, axis=1)

    out["match_method"] = df["match_method"]
    out["match_confidence"] = df["match_confidence"]

    out["area_id"] = df["area_id"]
    out["area_name"] = df["area_name"]
    out["area_type"] = df["area_type"]
    out["spatial_join_status"] = df["spatial_join_status"]

    out["exclusion_reason"] = df["exclusion_reason"]

    out["source_name"] = SOURCE_NAME
    out["source_date"] = SOURCE_DATE

    return out


if __name__ == "__main__":
    print("store_match_final.parquet 로딩...")
    df = pd.read_parquet(INPUT_PATH)
    print(f"  -> {len(df)}건 로딩 완료")

    print("\n공식 스키마로 변환...")
    final_df = build_final_schema(df)

    print("\nstore_status 분포:")
    print(final_df["store_status"].value_counts())

    print("\nmatch_confidence 분포:")
    print(final_df["match_confidence"].value_counts())

    final_df.to_parquet(OUTPUT_PATH, index=False)
    print(f"\n-> {OUTPUT_PATH} 저장 완료 (컬럼 {len(final_df.columns)}개, 행 {len(final_df)}개)")
    print("컬럼:", final_df.columns.tolist())
