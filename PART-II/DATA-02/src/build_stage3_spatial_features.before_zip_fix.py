from __future__ import annotations

import json
import math
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from pyproj import Transformer
from scipy.spatial import cKDTree


ROOT = Path.cwd().resolve()
BASE = ROOT / "PART-II/DATA-02"
CONFIG_PATH = BASE / "config/data02_config.json"
INTERMEDIATE = BASE / "intermediate"
OUTPUTS = BASE / "outputs"
REPORTS = BASE / "reports"

AREA_BASE_PATH = INTERMEDIATE / "area_base_features_20262.parquet"
SPATIAL_PATH = INTERMEDIATE / "seoul_spatial_competition_features_202606.parquet"
POINTS_PATH = INTERMEDIATE / "seoul_relevant_store_points_202606.parquet"
MASTER_PATH = OUTPUTS / "area_feature_master.parquet"

RADII_M = (250, 500, 1000)
DECAY_SCALE_M = 300.0
DECAY_CUTOFF_M = 2000.0
CATEGORY_MAP = {
    "빵/도넛": "bakery",
    "카페": "cafe",
    "떡/한과": "rice_cake",
}


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        raise SystemExit(f"설정 파일이 없습니다: {CONFIG_PATH}")
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


CONFIG = load_config()


def input_path(key: str, fallback: str) -> Path:
    rel = CONFIG.get("input_paths", {}).get(key, fallback)
    path = ROOT / rel
    if not path.exists():
        raise SystemExit(f"입력 파일이 없습니다: {path}")
    return path


SMALL_ZIP_PATH = input_path(
    "small_business_zip",
    "Datasets/b. External Public Data/02_small_business_stores/소상공인시장진흥공단_상가(상권)정보_20260630.zip",
)


def read_seoul_points() -> tuple[pd.DataFrame, dict]:
    usecols = [
        "상가업소번호", "상호명", "지점명", "상권업종소분류명",
        "시군구코드", "시군구명", "경도", "위도",
    ]
    with zipfile.ZipFile(SMALL_ZIP_PATH) as archive:
        members = [
            name for name in archive.namelist()
            if name.lower().endswith(".csv") and "서울" in name
        ]
        if len(members) != 1:
            raise SystemExit(f"서울 CSV를 하나로 특정하지 못했습니다: {members}")
        member = members[0]
        with archive.open(member) as stream:
            raw = pd.read_csv(
                stream,
                encoding="utf-8-sig",
                dtype={"상가업소번호": str, "시군구코드": str},
                usecols=usecols,
                low_memory=False,
            )

    original_rows = len(raw)
    points = raw.loc[raw["상권업종소분류명"].isin(CATEGORY_MAP)].copy()
    relevant_rows = len(points)
    points["longitude"] = pd.to_numeric(points["경도"], errors="coerce")
    points["latitude"] = pd.to_numeric(points["위도"], errors="coerce")
    valid = (
        points.longitude.between(126.70, 127.30)
        & points.latitude.between(37.40, 37.75)
    )
    invalid_coordinate_rows = int((~valid).sum())
    points = points.loc[valid].copy()

    before_dedup = len(points)
    points = points.drop_duplicates("상가업소번호", keep="first")
    duplicate_store_ids = before_dedup - len(points)
    points["category"] = points["상권업종소분류명"].map(CATEGORY_MAP)
    points["ccg_id"] = (
        points["시군구코드"].fillna("").astype(str)
        .str.replace(r"\.0$", "", regex=True).str.zfill(5)
    )

    transformer = Transformer.from_crs("EPSG:4326", "EPSG:5181", always_xy=True)
    x, y = transformer.transform(points.longitude.to_numpy(), points.latitude.to_numpy())
    points["x_epsg5181"] = x
    points["y_epsg5181"] = y
    points = points.rename(columns={
        "상가업소번호": "store_source_id",
        "상호명": "store_name",
        "지점명": "branch_name",
        "상권업종소분류명": "source_subcategory",
        "시군구명": "ccg_nm",
    })[
        [
            "store_source_id", "store_name", "branch_name", "category",
            "source_subcategory", "ccg_id", "ccg_nm", "longitude", "latitude",
            "x_epsg5181", "y_epsg5181",
        ]
    ].sort_values(["category", "store_source_id"])
    points.to_parquet(POINTS_PATH, index=False)

    stats = {
        "zip_member": member,
        "seoul_all_rows": original_rows,
        "relevant_before_coordinate_filter": relevant_rows,
        "invalid_coordinate_rows": invalid_coordinate_rows,
        "duplicate_store_ids": duplicate_store_ids,
        "final_relevant_points": len(points),
        "category_counts": points.category.value_counts().to_dict(),
    }
    return points, stats


def category_features(
    centers: np.ndarray, points: pd.DataFrame, category: str
) -> pd.DataFrame:
    subset = points.loc[points.category.eq(category)]
    prefix = category
    if subset.empty:
        raise SystemExit(f"소진공에서 {category} 점포를 찾지 못했습니다.")
    coordinates = subset[["x_epsg5181", "y_epsg5181"]].to_numpy(dtype=float)
    tree = cKDTree(coordinates)
    result: dict[str, np.ndarray] = {}

    for radius in RADII_M:
        neighbor_lists = tree.query_ball_point(centers, r=radius)
        result[f"{prefix}_count_{radius}m"] = np.fromiter(
            (len(indices) for indices in neighbor_lists), dtype=np.int64
        )

    nearest_distance, _ = tree.query(centers, k=1)
    result[f"{prefix}_nearest_distance_m"] = nearest_distance.astype(float)

    decay_neighbors = tree.query_ball_point(centers, r=DECAY_CUTOFF_M)
    pressure = np.empty(len(centers), dtype=float)
    for row_number, indices in enumerate(decay_neighbors):
        if not indices:
            pressure[row_number] = 0.0
            continue
        delta = coordinates[np.asarray(indices)] - centers[row_number]
        distances = np.sqrt(np.square(delta).sum(axis=1))
        pressure[row_number] = np.exp(-distances / DECAY_SCALE_M).sum()
    result[f"{prefix}_exp_decay_pressure_300m"] = pressure

    return pd.DataFrame(result)


def build_spatial_features(points: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    if not AREA_BASE_PATH.exists():
        raise SystemExit(f"2단계 결과가 없습니다: {AREA_BASE_PATH}")
    area = pd.read_parquet(AREA_BASE_PATH)
    required = ["area_id", "centroid_x_epsg5181", "centroid_y_epsg5181"]
    missing = [col for col in required if col not in area.columns]
    if missing:
        raise SystemExit(f"상권 기본 특성 필수 컬럼 누락: {missing}")
    if area.duplicated("area_id").any():
        raise SystemExit("상권 기본 특성 area_id 중복")

    centers_frame = area[required].copy()
    centers_frame["centroid_x_epsg5181"] = pd.to_numeric(
        centers_frame["centroid_x_epsg5181"], errors="coerce"
    )
    centers_frame["centroid_y_epsg5181"] = pd.to_numeric(
        centers_frame["centroid_y_epsg5181"], errors="coerce"
    )
    if centers_frame[["centroid_x_epsg5181", "centroid_y_epsg5181"]].isna().any().any():
        raise SystemExit("상권 중심점 좌표에 결측이 있습니다.")
    centers = centers_frame[["centroid_x_epsg5181", "centroid_y_epsg5181"]].to_numpy(float)

    spatial = centers_frame[["area_id"]].reset_index(drop=True)
    for category in CATEGORY_MAP.values():
        features = category_features(centers, points, category)
        spatial = pd.concat([spatial, features], axis=1)

    area_km2_500m = math.pi * 0.5**2
    spatial["bakery_density_500m_per_km2"] = spatial["bakery_count_500m"] / area_km2_500m
    local_food_count = spatial["bakery_count_500m"] + spatial["cafe_count_500m"] + spatial["rice_cake_count_500m"]
    spatial["bakery_share_relevant_food_500m"] = np.where(
        local_food_count > 0, spatial["bakery_count_500m"] / local_food_count, np.nan
    )
    spatial["bakery_to_cafe_count_ratio_500m"] = (
        spatial["bakery_count_500m"] / (spatial["cafe_count_500m"] + 1.0)
    )
    spatial["source_snapshot"] = "202606"
    spatial["distance_crs"] = "EPSG:5181"
    if spatial.duplicated("area_id").any():
        raise SystemExit("공간 특성 area_id 중복")
    spatial.to_parquet(SPATIAL_PATH, index=False)

    master = area.merge(spatial, on="area_id", how="left", validate="1:1")
    master["feature_snapshot"] = "BC_202601_202606__SEOUL_20262__SMALL_202606"
    master.to_parquet(MASTER_PATH, index=False)
    return spatial, master


def validate(
    spatial: pd.DataFrame, master: pd.DataFrame, points: pd.DataFrame
) -> list[str]:
    errors = []
    if len(spatial) != 1650:
        errors.append(f"공간 특성 행 수가 1,650이 아님: {len(spatial)}")
    if len(master) != 1650:
        errors.append(f"마스터 행 수가 1,650이 아님: {len(master)}")
    if master.duplicated("area_id").any():
        errors.append("마스터 area_id 중복")
    for category in CATEGORY_MAP.values():
        c250 = spatial[f"{category}_count_250m"]
        c500 = spatial[f"{category}_count_500m"]
        c1000 = spatial[f"{category}_count_1000m"]
        if not ((c250 <= c500) & (c500 <= c1000)).all():
            errors.append(f"{category} 반경별 점포 수 단조성 위반")
        if (spatial[f"{category}_nearest_distance_m"] < 0).any():
            errors.append(f"{category} 최근접 거리 음수")
    if points.duplicated("store_source_id").any():
        errors.append("점포 원천 ID 중복")
    share = spatial["bakery_share_relevant_food_500m"].dropna()
    if ((share < 0) | (share > 1)).any():
        errors.append("관련 음식점 중 제과점 비중 범위 위반")
    return errors


def correlations(master: pd.DataFrame) -> tuple[float, float, int]:
    columns = ["bakery_similr_induty_stor_co", "bakery_count_500m"]
    observed = master.loc[
        master.get("bakery_store_observed", False).fillna(False), columns
    ].dropna()
    if len(observed) < 3:
        return float("nan"), float("nan"), len(observed)
    pearson = observed.corr(method="pearson").iloc[0, 1]
    spearman = observed.corr(method="spearman").iloc[0, 1]
    return float(pearson), float(spearman), len(observed)


def write_report(
    points: pd.DataFrame,
    point_stats: dict,
    spatial: pd.DataFrame,
    master: pd.DataFrame,
    errors: list[str],
) -> None:
    pearson, spearman, comparison_n = correlations(master)
    counts = point_stats["category_counts"]
    report = f"""# DATA-02 3단계 공간 특성 품질 보고서

- 생성시각(UTC): `{datetime.now(timezone.utc).isoformat()}`
- 거리 좌표계: `EPSG:5181`
- 소진공 기준시점: `202606`

## 1. 입력 점포

- 서울 전체 원시 행: {point_stats['seoul_all_rows']:,}행
- 대상 업종 좌표 필터 전: {point_stats['relevant_before_coordinate_filter']:,}행
- 유효하지 않은 좌표 제외: {point_stats['invalid_coordinate_rows']:,}행
- 중복 점포 ID 제거: {point_stats['duplicate_store_ids']:,}행
- 최종 좌표 점포: {point_stats['final_relevant_points']:,}행
- 빵/도넛: {counts.get('bakery', 0):,}개
- 카페: {counts.get('cafe', 0):,}개
- 떡/한과: {counts.get('rice_cake', 0):,}개

## 2. 생성 특성

- 후보 상권: {len(spatial):,}개
- 반경별 점포 수: 250m, 500m, 1,000m
- 최근접 점포 거리
- 지수 거리감쇠 압력: `exp(-거리/300m)`, 최대 탐색거리 2,000m
- 500m 제과점 밀도와 인접 음식업종 대비 비중

## 3. 외부 지표 교차검증

서울시 상권 내부 전체 제과점 수와 소진공 중심점 500m 반경 제과점 수는 공간 정의가 다르므로 같을 필요는 없지만, 방향이 일치하는지 상관계수로 확인합니다.

- 비교 상권 수: {comparison_n:,}개
- Pearson 상관계수: {pearson:.4f}
- Spearman 상관계수: {spearman:.4f}

## 4. 무결성 검증

- 결과 상권 수: {len(master):,}개
- 상권 ID 중복: {int(master.duplicated('area_id').sum()):,}행
- 검증 오류: {errors if errors else '없음'}

## 5. 해석 주의

- 반경 지표는 상권 경계를 넘어 가까운 경쟁점을 반영하기 위한 것으로, 서울시 상권 내부 점포 수를 대체하지 않습니다.
- 거리감쇠 값은 점포가 가까울수록 큰 가중치를 주지만 매출이나 점포 규모를 의미하지 않습니다.
- 소진공에 프랜차이즈 여부가 없으므로 모든 빵/도넛 점포를 물리적 경쟁점으로 동일하게 취급합니다.
- 데이터 누수를 막기 위해 로그 변환·표준화·결측치 대체는 MODEL-01의 학습 분할 이후 수행합니다.
"""
    (REPORTS / "stage3_quality_report.md").write_text(report, encoding="utf-8")


def update_readme() -> None:
    path = BASE / "README.md"
    old = path.read_text(encoding="utf-8") if path.exists() else "# DATA-02\n"
    start = "<!-- STAGE3_METHOD_START -->"
    end = "<!-- STAGE3_METHOD_END -->"
    section = f"""{start}
## 3단계 공간 경쟁지표 방법론

행정구역 기준일 차이로 전남·광주의 기존 시도명은 경계가 유지된 시군구명을 기준으로 2026년 7월 신설 코드에 연결했습니다. 인천의 옛 중구·동구·서구는 새 제물포구·영종구·서해구·검단구와 일대일 대응하지 않으므로, BC 소비액을 임의 분할하지 않고 3개 지역을 전국 시군구 프로필에서 제외했습니다. 최종 연결률은 252/255(98.82%)입니다.

소진공 서울 점포의 WGS84 경위도를 서울 상권 중심점과 동일한 EPSG:5181로 변환합니다. 동일 업종은 `빵/도넛`, 인접 업종은 `카페`와 `떡/한과`로 분리하며, 동일 점포 ID는 한 번만 사용합니다.

경쟁 강도는 250m·500m·1,000m의 다중 반경 점포 수, 최근접 점포 거리, `exp(-거리/300m)` 지수 거리감쇠 합으로 표현합니다. 단일 반경만 사용하면 경계 바로 밖의 점포에 결과가 급변하므로 여러 반경과 연속형 거리감쇠를 함께 보존합니다. 최근접 거리는 주변 점포가 적은 후보 사이의 차이를 보완합니다.

상권 폴리곤 내부 점포 수만 다시 계산하는 방식은 채택하지 않습니다. 서울시 점포 자료가 이미 상권 내부 점포 수를 제공하고, 폴리곤 방식은 경계 바로 밖의 경쟁점을 놓치기 때문입니다. KDE의 대역폭 자동 최적화도 단일 시점 자료에서 과적합 위험이 있어 보류합니다. 대신 해석 가능한 원시 공간 특성을 만들고, 실제 선택할 반경과 변환은 MODEL-01 교차검증에서 결정합니다.

서울시 상권 내부 점포 수와 소진공 중심점 반경 점포 수의 상관을 교차검증으로 기록합니다. 두 값은 공간 정의가 달라 일치 여부가 아니라 전반적 방향의 일관성을 확인하는 용도입니다.
{end}
"""
    if start in old and end in old:
        old = old.split(start)[0] + section + old.split(end, 1)[1]
    else:
        old = old.rstrip() + "\n\n" + section
    path.write_text(old.rstrip() + "\n", encoding="utf-8")


def write_manifest(point_stats: dict, spatial: pd.DataFrame) -> None:
    manifest = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_snapshot": "202606",
        "distance_crs": "EPSG:5181",
        "radii_m": list(RADII_M),
        "decay_scale_m": DECAY_SCALE_M,
        "decay_cutoff_m": DECAY_CUTOFF_M,
        "categories": CATEGORY_MAP,
        "input_point_stats": point_stats,
        "output_rows": len(spatial),
        "outputs": [
            str(POINTS_PATH.relative_to(ROOT)),
            str(SPATIAL_PATH.relative_to(ROOT)),
            str(MASTER_PATH.relative_to(ROOT)),
        ],
    }
    (REPORTS / "stage3_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def main() -> None:
    print("[3/4-1] 소진공 서울 점포 추출·중복 제거·좌표 변환")
    points, point_stats = read_seoul_points()
    print("[3/4-2] 다중 반경·최근접 거리·거리감쇠 특성 계산")
    spatial, master = build_spatial_features(points)
    print("[3/4-3] 공간 특성 무결성·외부 지표 교차검증")
    errors = validate(spatial, master, points)
    write_report(points, point_stats, spatial, master, errors)
    write_manifest(point_stats, spatial)
    if errors:
        raise SystemExit(f"3단계 품질검사 실패: {errors}")
    print("[3/4-4] README 방법론 기록")
    update_readme()
    print("[DATA-02 3/4 완료]")
    print(f"보고서: {REPORTS / 'stage3_quality_report.md'}")


if __name__ == "__main__":
    main()
