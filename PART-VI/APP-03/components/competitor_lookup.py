"""
상권별 경쟁 브랜드 집계 로직.

DATA-01 산출물(brand_area_presence.parquet, brand_name_mapping.csv)을 읽어서,
실제 서울시 상권 코드(area_id)를 주면 그 상권에 있는 브랜드 목록을 돌려준다.

주의: 여기서 쓰는 area_id는 DATA-01/DATA-02가 쓰는 실제 서울시 상권 코드다.
result_v3.json의 area_id가 정확히 이 체계라 바로 연결 가능하다.
"""

from pathlib import Path
import pandas as pd
from functools import lru_cache

DATA_DIR = Path(__file__).resolve().parents[3] / "PART-II" / "DATA-01"
# components -> APP-03 -> PART-VI -> root, 총 3단계 -> parents[3]가 PART-II/DATA-01의 부모(root)


@lru_cache(maxsize=1)
def load_competitor_data(data_dir: Path = DATA_DIR):
    presence = pd.read_parquet(data_dir / "brand_area_presence.parquet")
    mapping = pd.read_csv(data_dir / "brand_name_mapping.csv")


    brand_names = (
        mapping[["brand_id", "brand_name_raw"]]
        .drop_duplicates(subset="brand_id", keep="first")
        .rename(columns={"brand_name_raw": "brand_name"})
    )

    merged = presence.merge(brand_names, on="brand_id", how="left")

    merged["brand_name"] = merged["brand_name"].fillna(merged["brand_id"])

    return merged


def get_competitors(area_id: str, exclude_brand_id: str | None = None, active_only: bool = True):
    """특정 상권(area_id)에 있는 경쟁 브랜드 목록을 store_cnt 내림차순으로 반환한다.

    Args:
        area_id: 실제 서울시 상권 코드 (예: "3001491")
        exclude_brand_id: 조회 중인 브랜드 자신은 경쟁사 목록에서 빼고 싶을 때 그 brand_id
        active_only: True면 현재 영업 중인(currently_active=True) 매장만 집계

    Returns:
        [{"brand_id": ..., "brand_name": ..., "store_cnt": ...}, ...]
        해당 상권에 매칭된 브랜드가 없으면 빈 리스트.
    """
    data = load_competitor_data()

    subset = data[data["area_id"] == area_id]
    if active_only:
        subset = subset[subset["currently_active"]]
    if exclude_brand_id:
        subset = subset[subset["brand_id"] != exclude_brand_id]

    subset = subset.sort_values("store_cnt", ascending=False)

    return subset[["brand_id", "brand_name", "store_cnt"]].to_dict(orient="records")


if __name__ == "__main__":
    sample_area_id = "3001491"
    result = get_competitors(sample_area_id)
    print(f"상권 {sample_area_id} 경쟁 브랜드 {len(result)}개:")
    for r in result:
        print(f"  - {r['brand_name']} (매장 {r['store_cnt']}개)")