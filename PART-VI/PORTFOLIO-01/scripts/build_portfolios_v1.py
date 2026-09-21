"""
포트폴리오(복수 출점 조합) 생성 스크립트 v1 
=====================================================

필요한 입력 파일
----------------
1. PART-III/MODEL-01/outputs/final_model_v3_1/model01_final_recommendations_v3_1.parquet
2. PART-III/MODEL-01/outputs/final_model_v3_1/model01_brand_availability_v3_1.csv
3. PART-II/DATA-02/outputs/area_feature_master.parquet

"""

import itertools
import math
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd

try:
    from pyproj import Transformer
except ImportError:
    raise SystemExit("pyproj가 필요합니다: pip install pyproj --break-system-packages")


# =========================================================
# CONFIG — 사용자가 결정해야 할 값
# =========================================================

# 이 파일의 실제 위치: PART-VI/PORTFOLIO-01/scripts/build_portfolios_v1.py
SCRIPT_DIR = Path(__file__).resolve().parent               # .../PART-VI/PORTFOLIO-01/scripts
ROOT = SCRIPT_DIR.parents[2]                                 # 리포 루트
# scripts -> PORTFOLIO-01 -> PART-VI -> root, 총 3단계라 parents[2]

MODEL01_DIR = ROOT / "PART-III" / "MODEL-01" / "outputs" / "final_model_v3_1"
DATA02_DIR = ROOT / "PART-II" / "DATA-02" / "outputs"

MODEL01_RECS_PATH = MODEL01_DIR / "model01_final_recommendations_v3_1.parquet"
MODEL01_AVAIL_PATH = MODEL01_DIR / "model01_brand_availability_v3_1.csv"
AREA_MASTER_PATH = DATA02_DIR / "area_feature_master.parquet"

# 결과 저장 위치: outputs는 scripts와 형제 폴더(PORTFOLIO-01/outputs/)다.
OUTPUT_DIR = SCRIPT_DIR.parent / "outputs"
OUTPUT_PATH = OUTPUT_DIR / "portfolios_output_v1.json"

# portfolio_score 가중치 (desired_store_count >= 2 일 때만 적용, 합 1.0 아니어도 됨 — overlap은 감점)
WEIGHTS = {
    "avg_area_score": 0.65,        # 개별 적합도를 압도적으로 우선 — MODEL-01 설계 철학(위험은 약한 신호)과 맞춤
    "geographic_diversification": 0.25,
    "overlap_risk_penalty": 0.10,  # 세게 깎지 않음 — 0.10만 반영
}

TOP_N_CANDIDATES_PER_BRAND = 15

# 자치구 분산 + 거리를 합쳐 geographic_diversification_score를 만들 때 내부 비중
GEO_SUB_WEIGHTS = {"district_diversity": 0.5, "distance": 0.5}
MIN_DISTANCE_M = 800       # 이 미만이면 근접 위험 최대
FULL_SCORE_DISTANCE_M = 3000  # 이 이상이면 거리 문제 없음

PORTFOLIO_SIZES = [1, 2, 3]
TOP_K_PER_SIZE = 3

CONSUMER_PROFILE_COLS = [
    "bc_age_cd_1_share_amt", "bc_age_cd_2_share_amt", "bc_age_cd_3_share_amt",
    "bc_age_cd_4_share_amt", "bc_age_cd_5_share_amt", "bc_age_cd_6_share_amt",
    "bc_female_share_amt",
]


# =========================================================
# 1. 데이터 로드 + 결합
# =========================================================

def load_and_join():

    recs = pd.read_parquet(MODEL01_RECS_PATH)
    area_master = pd.read_parquet(AREA_MASTER_PATH)

    recs["area_id"] = recs["area_id"].astype(str)
    area_master["area_id"] = area_master["area_id"].astype(str)

    area_cols = ["area_id", "ccg_nm", "centroid_x_epsg5181", "centroid_y_epsg5181",
                 "bakery_franchise_store_share"]
    recs = recs.merge(area_master[area_cols], on="area_id", how="left")

    missing_coords = recs["centroid_x_epsg5181"].isna().sum()
    if missing_coords:
        print(f"[경고] 좌표가 안 붙은 행 {missing_coords}건 — area_id 불일치 가능성, 확인 필요")

    transformer = Transformer.from_crs("EPSG:5181", "EPSG:4326", always_xy=True)
    lon, lat = transformer.transform(
        recs["centroid_x_epsg5181"].values, recs["centroid_y_epsg5181"].values
    )
    recs["centroid_longitude"] = lon
    recs["centroid_latitude"] = lat
    return recs


# =========================================================
# 2. 거리 / 분산 / 중복 계산 (0~1 스케일로 통일, 마지막에 x100)
# =========================================================

def haversine_m(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def min_pairwise_distance_m(areas_df):
    coords = areas_df[["centroid_latitude", "centroid_longitude"]].values
    dists = [
        haversine_m(*coords[i], *coords[j])
        for i, j in itertools.combinations(range(len(coords)), 2)
    ]
    return min(dists)


def distance_score_0to1(min_dist_m):
    if min_dist_m >= FULL_SCORE_DISTANCE_M:
        return 1.0
    if min_dist_m <= MIN_DISTANCE_M:
        return 0.0
    return (min_dist_m - MIN_DISTANCE_M) / (FULL_SCORE_DISTANCE_M - MIN_DISTANCE_M)


def district_diversity_0to1(areas_df):
    n = len(areas_df)
    n_unique = areas_df["ccg_nm"].nunique()
    return (n_unique - 1) / (n - 1)


def cosine_sim(v1, v2):
    v1, v2 = np.array(v1, dtype=float), np.array(v2, dtype=float)
    denom = np.linalg.norm(v1) * np.linalg.norm(v2)
    return float(np.dot(v1, v2) / denom) if denom else 0.0


def overlap_risk_0to1(areas_df):
    vectors = areas_df[CONSUMER_PROFILE_COLS].fillna(0).values
    sims = [
        cosine_sim(vectors[i], vectors[j])
        for i, j in itertools.combinations(range(len(vectors)), 2)
    ]
    return float(np.mean(sims))


# =========================================================
# 3. 조합 하나에 대한 점수 (mock 스키마 키 이름 그대로)
# =========================================================

def score_combo(areas_df, desired_store_count):
    avg_area_score = float(areas_df["final_suitability_score"].mean()) * 100

    if desired_store_count == 1:
        # mock과 동일: 비교 대상이 없는 지표는 전부 null, portfolio_score는 재계산 없이 그대로
        return {
            "portfolio_score": round(avg_area_score, 2),
            "average_area_score": round(avg_area_score, 2),
            "geographic_diversification_score": None,
            "consumer_diversification_score": None,
            "overlap_risk_score": None,
        }, None

    district_div = district_diversity_0to1(areas_df)
    min_dist_m = min_pairwise_distance_m(areas_df)
    dist_score = distance_score_0to1(min_dist_m)
    geo_div_0to1 = (
        GEO_SUB_WEIGHTS["district_diversity"] * district_div
        + GEO_SUB_WEIGHTS["distance"] * dist_score
    )
    overlap_0to1 = overlap_risk_0to1(areas_df)

    portfolio_score = (
        WEIGHTS["avg_area_score"] * avg_area_score
        + WEIGHTS["geographic_diversification"] * geo_div_0to1 * 100
        - WEIGHTS["overlap_risk_penalty"] * overlap_0to1 * 100
    )

    scores = {
        "portfolio_score": round(float(portfolio_score), 2),
        "average_area_score": round(avg_area_score, 2),
        "geographic_diversification_score": round(geo_div_0to1 * 100, 2),
        "consumer_diversification_score": round((1 - overlap_0to1) * 100, 2),
        "overlap_risk_score": round(overlap_0to1 * 100, 2),
    }
    return scores, min_dist_m






# =========================================================
# 4. 근거 문장 / 체크리스트 (템플릿, 나중에 LLM-01로 교체 가능)
# =========================================================

def build_rationale_facts(areas_df, scores, desired_store_count, min_dist_m):
    facts = [f"선택 상권의 평균 적합도 {scores['average_area_score']:.1f}점"]
    if desired_store_count >= 2:
        facts.append(f"상권 간 최소 거리 {min_dist_m/1000:.1f}km")
        n_unique = areas_df["ccg_nm"].nunique()
        facts.append(f"{n_unique}개 자치구로 분산")
        if scores["overlap_risk_score"] is not None and scores["overlap_risk_score"] >= 90:
            facts.append("상권 간 소비자 구성이 유사해 고객 잠식 위험 존재")
    return facts


def build_risk_factors(areas_df, scores):
    risks = []
    if scores["overlap_risk_score"] is not None and scores["overlap_risk_score"] >= 90:
        risks.append("상권 간 고객층 중복 가능성 — 잠식 위험 검토 필요")
    if not risks:
        # 화면 코드가 risk_factors[0]을 가정하고 접근하는 곳이 있어
        # 빈 배열을 그대로 내보내면 IndexError가 남 (build_recommendations_v1.py와
        # 동일한 이유로 최소 1개는 채워서 내보냄)
        risks.append("특별히 확인된 위험 요인 없음")
    return risks


def build_next_checks(desired_store_count):
    checks = ["후보별 임대료와 예상 고정비 비교", "현장 유동과 접근성 확인"]
    if desired_store_count >= 2:
        checks.append("출점 순서와 운영인력 배치 검토")
    return checks


# =========================================================
# 5. 브랜드별 portfolios 리스트 생성 (flat list, mock과 동일 구조)
# =========================================================

def build_portfolios_for_brand(brand_df):
    eligible = brand_df[
        (brand_df["risk_pass"] == True) & (brand_df["eligible_new_opening"] == True)
    ].copy()
    eligible = eligible.sort_values("final_rank").head(TOP_N_CANDIDATES_PER_BRAND)

    if eligible.empty:
        return []

    all_portfolios = []
    for size in PORTFOLIO_SIZES:
        if size > len(eligible):
            continue

        scored = []
        for combo_idx in itertools.combinations(eligible.index, size):
            combo_df = eligible.loc[list(combo_idx)]
            scores, min_dist_m = score_combo(combo_df, size)
            scored.append({
                "desired_store_count": size,
                "area_ids": combo_df["area_id"].tolist(),
                "area_names": combo_df["area_name"].tolist(),
                "portfolio_score": scores["portfolio_score"],
                "score_components": {
                    "average_area_score": scores["average_area_score"],
                    "geographic_diversification_score": scores["geographic_diversification_score"],
                    "consumer_diversification_score": scores["consumer_diversification_score"],
                    "overlap_risk_score": scores["overlap_risk_score"],
                },
                "rationale_facts": build_rationale_facts(combo_df, scores, size, min_dist_m),
                "risk_factors": build_risk_factors(combo_df, scores),
                "next_checks": build_next_checks(size),
            })

        scored.sort(key=lambda x: x["portfolio_score"], reverse=True)
        top = scored[:TOP_K_PER_SIZE]
        for i, p in enumerate(top, start=1):
            p["portfolio_rank"] = i
        all_portfolios.extend(top)

    return all_portfolios


# =========================================================
# 6. 전체 실행
# =========================================================

def main():
    recs = load_and_join()

    result = {}
    for brand_id, brand_df in recs.groupby("brand_id"):
        brand_name = brand_df["brand_name"].iloc[0]
        portfolios = build_portfolios_for_brand(brand_df)
        result[brand_id] = {"brand_name": brand_name, "portfolios": portfolios}

        by_size = {}
        for p in portfolios:
            by_size[p["desired_store_count"]] = by_size.get(p["desired_store_count"], 0) + 1
        print(f"[{brand_name}] " + ", ".join(f"{k}개:{v}건" for k, v in sorted(by_size.items())))

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n완료 -> {OUTPUT_PATH}")
    return result


if __name__ == "__main__":
    main()