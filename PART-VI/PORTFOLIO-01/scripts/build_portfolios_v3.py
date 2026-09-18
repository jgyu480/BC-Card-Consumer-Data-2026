"""
포트폴리오(복수 출점 조합) 생성 스크립트 v3(최종)
=====================================================

역할
-------------
MODEL-01 v3.1이 브랜드별로 이미 계산해둔 "개별 상권 적합도"를 재료로,
1~3개 상권을 묶은 조합을 만들고 점수를 매겨 브랜드별·출점 희망 개수별
상위 3개 조합을 뽑는다. 미래 매출이나 성공 확률을 예측하지 않는다 —
전부 MODEL-01이 이미 검증해둔 값을 규칙으로 조합할 뿐이다.

점수 구성
---------
- average_area_score: 조합 내 상권들의 final_suitability_score 평균
- geographic_diversification_score: 자치구 분산 + 상권 간 최소 거리를 합친
  지표 
- consumer_diversification_score / overlap_risk_score: 상권 간 소비자
  구성(연령대·성별 비중) 코사인 유사도를 기준으로 한 반대쌍 지표
- portfolio_score = 위 점수들의 가중합. 


필요한 입력 파일
----------------
1. PART-III/MODEL-01/outputs/final_model_v3_1/model01_final_recommendations_v3_1.parquet
2. PART-III/MODEL-01/outputs/final_model_v3_1/model01_brand_availability_v3_1.csv
3. PART-II/DATA-02/outputs/area_feature_master.parquet

사용자가 결정해야 할 값 (CONFIG 섹션)
--------------------------------------------
- WEIGHTS: 4가지 기준을 몇 대 몇으로 섞을지 (지금은 임시값, A 확인 후 조정 권장)
- TOP_N_CANDIDATES_PER_BRAND: 브랜드당 조합을 만들 때 상위 몇 개 상권까지 후보로 볼지
- MIN_DISTANCE_M / FULL_SCORE_DISTANCE_M: 상권 간 거리 판정 기준
- PORTFOLIO_SIZES: 몇 개짜리 조합을 만들지 (1/2/3)
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

# 이 파일의 실제 위치: PART-VI/PORTFOLIO-01/scripts/build_portfolios_v3.py
SCRIPT_DIR = Path(__file__).resolve().parent               # .../PART-VI/PORTFOLIO-01/scripts
ROOT = SCRIPT_DIR.parents[2]                                 # 리포 루트
# scripts -> PORTFOLIO-01 -> PART-VI -> root, 총 3단계라 parents[2]

MODEL01_DIR = ROOT / "PART-III" / "MODEL-01" / "outputs" / "final_model_v3_1"
DATA02_DIR = ROOT / "PART-II" / "DATA-02" / "outputs"

MODEL01_RECS_PATH = MODEL01_DIR / "model01_final_recommendations_v3_1.parquet"
MODEL01_AVAIL_PATH = MODEL01_DIR / "model01_brand_availability_v3_1.csv"
AREA_MASTER_PATH = DATA02_DIR / "area_feature_master.parquet"

OUTPUT_DIR = SCRIPT_DIR.parent / "outputs"
OUTPUT_PATH = OUTPUT_DIR / "portfolios_output_v3.json"


WEIGHTS = {
    "avg_area_score": 0.65,        
    "geographic_diversification": 0.15,  
    "overlap_risk_penalty": 0.20,        
}

TOP_N_CANDIDATES_PER_BRAND = 15

# v3 신규: 1~2위 포트폴리오 점수차가 이 값 이내면 둘 다 "최우선 추천"으로 표시.
# 사이즈별로 기준을 다르게 잡음 
# 아래 값은 각 사이즈 그룹 1~2위 격차의 실측 25분위값 기준(대략 하위 25%만 동점
# 처리되게) — B가 개별 상권 동점 임계값(0.003)을 실측 분포로 정한 것과 같은 방식.
# 브랜드 풀이나 가중치가 바뀌면 재검토 필요.
TIE_GAP_THRESHOLD_BY_SIZE = {1: 1.0, 2: 0.5, 3: 0.2}

GEO_SUB_WEIGHTS = {"district_diversity": 0.5, "distance": 0.5}
MIN_DISTANCE_M = 800       # 이 미만이면 근접 위험 최대
FULL_SCORE_DISTANCE_M = 5000  # 이 이상이면 거리 문제 없음


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

def score_combo_raw(areas_df, desired_store_count):
    """
    원본(raw) 컴포넌트만 계산. portfolio_score는 여기서 안 만든다 —
    overlap_risk를 브랜드 내 상대값으로 정규화한 다음에 최종 점수를 매겨야
    하기 때문 (아래 finalize_portfolio_score 참고).
    """
    avg_area_score = float(areas_df["final_suitability_score"].mean()) * 100

    if desired_store_count == 1:
        return {
            "average_area_score": round(avg_area_score, 2),
            "geographic_diversification_score": None,
            "overlap_risk_raw": None,
        }, None

    district_div = district_diversity_0to1(areas_df)
    min_dist_m = min_pairwise_distance_m(areas_df)
    dist_score = distance_score_0to1(min_dist_m)
    geo_div_0to1 = (
        GEO_SUB_WEIGHTS["district_diversity"] * district_div
        + GEO_SUB_WEIGHTS["distance"] * dist_score
    )
    overlap_0to1 = overlap_risk_0to1(areas_df)

    return {
        "average_area_score": round(avg_area_score, 2),
        "geographic_diversification_score": round(geo_div_0to1 * 100, 2),
        "overlap_risk_raw": round(overlap_0to1 * 100, 2),  # 화면에 보여줄 절대값(정규화 전)
    }, min_dist_m


def normalize_overlap_for_scoring(raw_overlap_list):
    """
    overlap_risk의 절대값 자체가 원래 전체적으로 높게(평균 85 근처) 나와서,
    이걸 그대로 가중치에 곱하면 "순위를 가르는" 게 아니라 "전부 다 같이
    끌어내리는" 일괄 감점이 돼버림 (실측: 2개조합 평균 84.9, 최소도 60.9).
    그래서 점수 계산에는 "같은 브랜드·같은 조합크기 후보군 안에서 상대적으로
    얼마나 겹치는 편인가"로 min-max 정규화한 값을 쓴다. 화면에 보여주는
    overlap_risk_score(절대값)는 안 건드리고 그대로 둔다.
    """
    valid = [v for v in raw_overlap_list if v is not None]
    if not valid:
        return {}
    lo, hi = min(valid), max(valid)
    if hi - lo < 1e-9:
        return {v: 50.0 for v in valid}
    return {v: (v - lo) / (hi - lo) * 100 for v in valid}


def finalize_portfolio_score(raw, overlap_norm_map):
    if raw["overlap_risk_raw"] is None:
        return round(raw["average_area_score"], 2)

    overlap_for_scoring = overlap_norm_map.get(raw["overlap_risk_raw"], 50.0)
    portfolio_score = (
        WEIGHTS["avg_area_score"] * raw["average_area_score"]
        + WEIGHTS["geographic_diversification"] * raw["geographic_diversification_score"]
        - WEIGHTS["overlap_risk_penalty"] * overlap_for_scoring
    )
    return round(float(portfolio_score), 2)






# =========================================================
# 4. 근거 문장 / 체크리스트 
# =========================================================

def build_rationale_facts(areas_df, avg_area_score, overlap_risk_raw, desired_store_count, min_dist_m):
    facts = [f"선택 상권의 평균 적합도 {avg_area_score:.1f}점"]
    if desired_store_count >= 2:
        facts.append(f"상권 간 최소 거리 {min_dist_m/1000:.1f}km")
        n_unique = areas_df["ccg_nm"].nunique()
        facts.append(f"{n_unique}개 자치구로 분산")
        if overlap_risk_raw is not None and overlap_risk_raw >= 90:
            facts.append("상권 간 소비자 구성이 유사해 고객 잠식 위험 존재")
    return facts


def build_risk_factors(overlap_risk_raw):
    risks = []
    if overlap_risk_raw is not None and overlap_risk_raw >= 90:
        risks.append("상권 간 고객층 중복 가능성 — 잠식 위험 검토 필요")
    if not risks:
        risks.append("특별히 확인된 위험 요인 없음")
    return risks


def build_next_checks(desired_store_count):
    checks = ["후보별 임대료와 예상 고정비 비교", "현장 유동과 접근성 확인"]
    if desired_store_count >= 2:
        checks.append("출점 순서와 운영인력 배치 검토")
    return checks


# =========================================================
# 5. 브랜드별 portfolios 리스트 생성 
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

        # 1단계: 이 브랜드·이 조합크기의 모든 후보에 대해 raw 컴포넌트부터 계산
        raw_entries = []
        for combo_idx in itertools.combinations(eligible.index, size):
            combo_df = eligible.loc[list(combo_idx)]
            raw, min_dist_m = score_combo_raw(combo_df, size)
            raw_entries.append({
                "combo_df": combo_df, "raw": raw, "min_dist_m": min_dist_m,
            })

        # 2단계: overlap_risk를 이 후보군 안에서 상대값으로 정규화
        overlap_norm_map = normalize_overlap_for_scoring(
            [e["raw"]["overlap_risk_raw"] for e in raw_entries]
        )

        # 3단계: 정규화된 값으로 최종 portfolio_score 계산
        scored = []
        for e in raw_entries:
            combo_df, raw, min_dist_m = e["combo_df"], e["raw"], e["min_dist_m"]
            portfolio_score = finalize_portfolio_score(raw, overlap_norm_map)
            overlap_raw = raw["overlap_risk_raw"]
            scored.append({
                "desired_store_count": size,
                "area_ids": combo_df["area_id"].tolist(),
                "area_names": combo_df["area_name"].tolist(),
                "portfolio_score": portfolio_score,
                "score_components": {
                    "average_area_score": raw["average_area_score"],
                    "geographic_diversification_score": raw["geographic_diversification_score"],
                    "consumer_diversification_score": (
                        round(100 - overlap_raw, 2) if overlap_raw is not None else None
                    ),
                    "overlap_risk_score": overlap_raw,
                },
                "rationale_facts": build_rationale_facts(
                    combo_df, raw["average_area_score"], overlap_raw, size, min_dist_m
                ),
                "risk_factors": build_risk_factors(overlap_raw),
                "next_checks": build_next_checks(size),
            })

        scored.sort(key=lambda x: x["portfolio_score"], reverse=True)
        top = scored[:TOP_K_PER_SIZE]
        for i, p in enumerate(top, start=1):
            p["portfolio_rank"] = i


        threshold = TIE_GAP_THRESHOLD_BY_SIZE.get(size, 0.5)
        is_top = [False] * len(top)
        if top:
            is_top[0] = True
            if len(top) >= 2 and (top[0]["portfolio_score"] - top[1]["portfolio_score"]) <= threshold:
                is_top[1] = True

        top_score = top[0]["portfolio_score"] if top else None
        gap_tier = []
        for p in top:
            if p is top[0] and is_top[0]:
                gap_tier.append("top")
            else:
                gap = top_score - p["portfolio_score"]
                gap_tier.append("close" if gap <= threshold * 2 else "alternative")

        for p, flag, tier in zip(top, is_top, gap_tier):
            p["is_top_recommendation"] = flag
            p["gap_tier"] = tier  

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