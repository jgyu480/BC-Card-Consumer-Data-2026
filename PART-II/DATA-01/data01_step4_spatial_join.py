"""
DATA-01 : 4단계 (서울 상권 경계 폴리곤에 매장 좌표 공간조인)

입력:
- store_match_with_status.parquet (1~3단계 결과)
- Datasets/b. External Public Data/06_seoul_area_boundary/
    서울시 상권분석서비스(영역-상권)/서울시 상권분석서비스(영역-상권).shp

처리:
1) 서울 소재 매장만 대상 (그 외 지역은 spatial_join_status="not_applicable_non_seoul")
2) 매장 좌표(WGS84 경도/위도) -> EPSG:5181(shapefile과 동일 좌표계)로 변환
3) 변환된 점이 어느 상권 폴리곤 안에 있는지 공간조인 (geopandas sjoin)
4) 상권코드/상권명/상권유형을 매장에 부여

출력:
- store_match_final.parquet (area_id, area_name, area_type, spatial_join_status 컬럼 추가)
"""

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

INPUT_PATH = "store_match_with_status.parquet"
BOUNDARY_PATH = "Datasets/b. External Public Data/06_seoul_area_boundary/서울시 상권분석서비스(영역-상권)/서울시 상권분석서비스(영역-상권).shp"
OUTPUT_PATH = "store_match_final.parquet"


def spatial_join_with_areas(stores_df: pd.DataFrame, boundary_gdf: gpd.GeoDataFrame) -> pd.DataFrame:
    stores_df = stores_df.copy()
    stores_df["area_id"] = None
    stores_df["area_name"] = None
    stores_df["area_type"] = None
    stores_df["spatial_join_status"] = None

    seoul_mask = stores_df["시도명"] == "서울특별시"
    non_seoul_idx = stores_df[~seoul_mask].index
    stores_df.loc[non_seoul_idx, "spatial_join_status"] = "not_applicable_non_seoul"

    seoul_df = stores_df[seoul_mask].copy()

    no_coord_mask = seoul_df["경도"].isna() | seoul_df["위도"].isna()
    no_coord_idx = seoul_df[no_coord_mask].index
    stores_df.loc[no_coord_idx, "spatial_join_status"] = "no_coordinates"

    valid_df = seoul_df[~no_coord_mask].copy()
    valid_df["경도"] = valid_df["경도"].astype(float)
    valid_df["위도"] = valid_df["위도"].astype(float)

    geometry = [Point(xy) for xy in zip(valid_df["경도"], valid_df["위도"])]
    points_gdf = gpd.GeoDataFrame(valid_df, geometry=geometry, crs="EPSG:4326")

    # 매장 좌표(WGS84) -> shapefile과 동일 좌표계(EPSG:5181)로 변환
    points_gdf = points_gdf.to_crs(boundary_gdf.crs)

    joined = gpd.sjoin(points_gdf, boundary_gdf[["TRDAR_CD", "TRDAR_CD_N", "TRDAR_SE_1", "geometry"]],
                        how="left", predicate="within")

    # within으로 못 잡힌 점들은 좌표 오차/경계선 문제일 수 있으므로,
    # 가장 가까운 상권(폴리곤 경계까지 거리)으로 재시도
    joined = joined[~joined.index.duplicated(keep="first")]
    still_unmatched = joined[joined["TRDAR_CD"].isna()]

    if not still_unmatched.empty:
        nearest = gpd.sjoin_nearest(
            points_gdf.loc[still_unmatched.index],
            boundary_gdf[["TRDAR_CD", "TRDAR_CD_N", "TRDAR_SE_1", "geometry"]],
            how="left", distance_col="nearest_dist_m"
        )
        nearest = nearest[~nearest.index.duplicated(keep="first")]

        # 너무 멀리 떨어진 경우까지 억지로 붙이지 않음
        # (임계값 300m: 실제 분포 확인 결과 중앙값 202m, 75%가 340m 이내였고,
        #  DATA-02에서도 500m를 경쟁 분석의 의미 있는 반경 단위로 사용하고 있어
        #  그보다 보수적인 300m를 절충안으로 채택)
        NEAREST_MAX_DIST_M = 300
        close_enough = nearest[nearest["nearest_dist_m"] <= NEAREST_MAX_DIST_M]

        joined.loc[close_enough.index, "TRDAR_CD"] = close_enough["TRDAR_CD"]
        joined.loc[close_enough.index, "TRDAR_CD_N"] = close_enough["TRDAR_CD_N"]
        joined.loc[close_enough.index, "TRDAR_SE_1"] = close_enough["TRDAR_SE_1"]
        joined.loc[close_enough.index, "_matched_via_nearest"] = True

    matched_mask = joined["TRDAR_CD"].notna()

    stores_df.loc[joined[matched_mask].index, "area_id"] = joined.loc[matched_mask, "TRDAR_CD"]
    stores_df.loc[joined[matched_mask].index, "area_name"] = joined.loc[matched_mask, "TRDAR_CD_N"]
    stores_df.loc[joined[matched_mask].index, "area_type"] = joined.loc[matched_mask, "TRDAR_SE_1"]

    matched_via_nearest = joined.get("_matched_via_nearest")
    if matched_via_nearest is not None:
        nearest_idx = joined[matched_via_nearest.fillna(False)].index
        stores_df.loc[nearest_idx, "spatial_join_status"] = "matched_nearest_300m"
        exact_idx = joined[matched_mask & ~matched_via_nearest.fillna(False)].index
        stores_df.loc[exact_idx, "spatial_join_status"] = "matched"
    else:
        stores_df.loc[joined[matched_mask].index, "spatial_join_status"] = "matched"

    unmatched_idx = joined[~matched_mask].index
    stores_df.loc[unmatched_idx, "spatial_join_status"] = "failed_out_of_boundary"

    return stores_df


if __name__ == "__main__":
    print("store_match_with_status.parquet 로딩...")
    stores_df = pd.read_parquet(INPUT_PATH)
    print(f"  -> {len(stores_df)}건 로딩 완료")

    print("\n서울 상권 경계 shapefile 로딩...")
    boundary_gdf = gpd.read_file(BOUNDARY_PATH)
    print(f"  -> 상권 {len(boundary_gdf)}개 로딩 완료 (CRS: {boundary_gdf.crs})")

    print("\n공간조인 수행...")
    result_df = spatial_join_with_areas(stores_df, boundary_gdf)

    print("\nspatial_join_status 분포:")
    print(result_df["spatial_join_status"].value_counts())

    result_df.to_parquet(OUTPUT_PATH, index=False)
    print(f"\n-> {OUTPUT_PATH} 저장 완료")
