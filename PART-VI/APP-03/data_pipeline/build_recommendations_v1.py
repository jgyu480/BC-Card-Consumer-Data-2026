"""
단일 상권 추천(recommendations[]) + 브랜드 요약(dna_summary) 생성 스크립트 v1
=====================================================

"""

import os
import json
from pathlib import Path

import numpy as np
import pandas as pd

try:
    from pyproj import Transformer
except ImportError:
    raise SystemExit("pyproj가 필요합니다: pip install pyproj --break-system-packages")


# =========================================================
# CONFIG
# =========================================================

# 이 파일의 실제 위치: PART-VI/APP-03/data_pipeline/build_recommendations_v1.py
# (PORTFOLIO-01/scripts가 아님 — 이 스크립트는 APP-03 전용 화면 매핑 로직)
SCRIPT_DIR = Path(__file__).resolve().parent               # .../PART-VI/APP-03/data_pipeline
ROOT = SCRIPT_DIR.parents[2]                                 # 리포 루트


MODEL01_DIR = ROOT / "PART-III" / "MODEL-01" / "outputs" / "final_model_v3_1"
DATA02_DIR = ROOT / "PART-II" / "DATA-02" / "outputs"

MODEL01_RECS_PATH = MODEL01_DIR / "model01_final_recommendations_v3_1.parquet"
AREA_MASTER_PATH = DATA02_DIR / "area_feature_master.parquet"

OUTPUT_DIR = SCRIPT_DIR.parent / "outputs"
OUTPUT_PATH = OUTPUT_DIR / "recommendations_output_v1.json"

MAX_RECOMMENDATIONS_PER_BRAND = 20

# 기존 동일 브랜드 매장과의 거리를 0~100 위험점수로 바꿀 때 기준(m)
PROXIMITY_MIN_RISK_DISTANCE_M = 500   # 이 미만이면 위험 최대(100)
PROXIMITY_SAFE_DISTANCE_M = 2000      # 이 이상이면 위험 없음(0)

AGE_LABELS = {
    1: "20대 이하", 2: "20대", 3: "30대", 4: "40대", 5: "50대", 6: "60대 이상",
}

# positive_drivers 코드 -> 문장 (실제 데이터에서 확인된 전체 코드)
POSITIVE_DRIVER_SENTENCES = {
    "brand_environment_fit": "브랜드가 선호하는 소비 환경과 잘 맞음",
    "brand_specific_advantage": "다른 브랜드 대비 이 상권에서의 차별적 강점이 있음",
    "market_opportunity": "제과 시장 규모 자체가 큰 상권",
    "low_competition_risk": "경쟁 리스크가 낮은 상권",
}

# caution_flags 코드 -> 문장 (None이면 문장 생성 안 함 = 특이사항 없음)
CAUTION_FLAG_SENTENCES = {
    "profile_stability_moderate": "브랜드 입점 패턴 데이터가 중간 수준으로 안정적 — 참고용으로 확인 필요",
    "no_model_level_caution_flag": None,
    "competition_risk_elevated_but_below_exclusion": "경쟁 수준이 다소 높으나 제외 기준 이하",
    "competition_risk_moderate": "경쟁 수준이 중간 정도로 존재함",
    "same_brand_distance_750m_to_1000m_review": "기존 동일 브랜드 매장과 750~1000m 거리로 근접 검토 필요",
}

RISK_REVIEW_FLAG_SENTENCES = {
    "profile_stability_moderate__confirm_local_site_conditions": "현장에서 실제 입지 여건 확인 필요",
    "no_model_level_high_risk_flag": None,
}

# profile_stability -> (coverage_score, confidence_label)
PROFILE_STABILITY_MAP = {
    "high_profile_stability": (90, "높음"),
    "moderate_profile_stability": (65, "보통"),
    "low_profile_stability": (40, "낮음"),  # 실제 데이터엔 없었지만 대비용으로 남겨둠
}


# =========================================================
# 1. 데이터 로드 + 결합
# =========================================================

def load_and_join():
    """
    참고: model01_brand_availability_v3_1.csv는 여기서 안 씁니다 —
    available_recommendation_count, profile_stability가
    recommendations parquet에 이미 들어있어서 중복 merge가 오히려
    컬럼명 충돌(_x/_y)을 만듭니다. availability csv는 팀 차원의
    브랜드 요약용으로 따로 확인할 때만 쓰면 됩니다.
    """
    recs = pd.read_parquet(MODEL01_RECS_PATH)
    area_master = pd.read_parquet(AREA_MASTER_PATH)

    recs["area_id"] = recs["area_id"].astype(str)
    area_master["area_id"] = area_master["area_id"].astype(str)

    recs = recs.merge(
        area_master[["area_id", "ccg_nm", "bakery_franchise_store_share",
                      "centroid_x_epsg5181", "centroid_y_epsg5181"]],
        on="area_id", how="left"
    )

    transformer = Transformer.from_crs("EPSG:5181", "EPSG:4326", always_xy=True)
    lon, lat = transformer.transform(
        recs["centroid_x_epsg5181"].values, recs["centroid_y_epsg5181"].values
    )
    recs["centroid_longitude"] = lon
    recs["centroid_latitude"] = lat
    return recs


# =========================================================
# 2. 근접 위험 점수 (재료만 있고 완성품이 없던 유일한 값)
# =========================================================

def proximity_risk_score(distance_m):
    if pd.isna(distance_m):
        return None
    if distance_m <= PROXIMITY_MIN_RISK_DISTANCE_M:
        return 100.0
    if distance_m >= PROXIMITY_SAFE_DISTANCE_M:
        return 0.0
    span = PROXIMITY_SAFE_DISTANCE_M - PROXIMITY_MIN_RISK_DISTANCE_M
    return round(100.0 * (PROXIMITY_SAFE_DISTANCE_M - distance_m) / span, 1)


# =========================================================
# 3. 코드 문자열 파싱 -> 문장
# =========================================================

def parse_pipe_string(s):
    """'key1=val1 | key2=val2' 또는 'code1 | code2' 형태를 리스트로 분리"""
    if pd.isna(s) or not s:
        return []
    return [p.strip() for p in s.split("|") if p.strip()]


def positive_drivers_to_sentences(raw):
    sentences = []
    for part in parse_pipe_string(raw):
        key = part.split("=")[0].strip()
        sentence = POSITIVE_DRIVER_SENTENCES.get(key)
        if sentence:
            sentences.append(sentence)
    return sentences


def caution_flags_to_sentences(raw):
    sentences = []
    for code in parse_pipe_string(raw):
        sentence = CAUTION_FLAG_SENTENCES.get(code)
        if sentence:
            sentences.append(sentence)
    if not sentences:
        sentences.append("특별히 확인된 위험 요인 없음")
    return sentences


def risk_flag_to_checks(raw):
    checks = []
    sentence = RISK_REVIEW_FLAG_SENTENCES.get(raw)
    if sentence:
        checks.append(sentence)
    checks.append("후보별 임대료와 예상 고정비 비교")
    checks.append("현장 유동과 접근성 확인")
    return checks


# =========================================================
# 4. 소비자 구성 -> 서술형 분류
# =========================================================

def classify_consumer_profile(row, avg_ticket_percentile):
    age_cols = {i: row.get(f"bc_age_cd_{i}_share_amt", 0) or 0 for i in range(1, 7)}
    primary_age_code = max(age_cols, key=age_cols.get)
    primary_segment = AGE_LABELS[primary_age_code]

    female_share = row.get("bc_female_share_amt", 0.5) or 0.5
    if female_share >= 0.55:
        demand_context = f"{primary_segment} 여성 고객 비중이 높은 상권"
    elif female_share <= 0.45:
        demand_context = f"{primary_segment} 남성 고객 비중이 높은 상권"
    else:
        demand_context = f"{primary_segment} 고객이 성별 구분 없이 고르게 분포"

    if avg_ticket_percentile >= 0.66:
        avg_ticket_band = "객단가 상위권"
    elif avg_ticket_percentile <= 0.33:
        avg_ticket_band = "객단가 하위권"
    else:
        avg_ticket_band = "객단가 중간 수준"

    return {
        "primary_segment": primary_segment,
        "demand_context": demand_context,
        "avg_ticket_band": avg_ticket_band,
    }


# =========================================================
# 5. 추천 라벨
# =========================================================

def recommendation_label(final_rank):
    if final_rank <= 3:
        return "최우선 검토"
    if final_rank <= 10:
        return "우선 검토"
    return "비교 후보"


# =========================================================
# 6. 브랜드별 recommendations[] + dna_summary 생성
# =========================================================

def build_for_brand(brand_df):
    brand_df = brand_df.copy()
    # avg_ticket 백분위는 브랜드 내 상대 비교로 계산 (절대 기준이 없어서)
    brand_df["_avg_ticket_pct"] = brand_df["bakery_avg_ticket"].rank(pct=True)

    cap = brand_df["available_recommendation_count"].iloc[0]
    cap = int(cap) if pd.notna(cap) else MAX_RECOMMENDATIONS_PER_BRAND
    n = min(cap, MAX_RECOMMENDATIONS_PER_BRAND)

    eligible = brand_df[
        (brand_df["risk_pass"] == True) & (brand_df["eligible_new_opening"] == True)
    ].sort_values("final_rank").head(n)

    recommendations = []
    for _, row in eligible.iterrows():
        suitability = round(float(row["final_suitability_score"]) * 100, 1)
        rec = {
            "area_id": row["area_id"],
            "area_name": row["area_name"],
            "district_nm": row.get("ccg_nm"),
            "centroid_latitude": row.get("centroid_latitude"),
            "centroid_longitude": row.get("centroid_longitude"),
            "rank": int(row["final_rank"]),
            "recommendation_label": recommendation_label(int(row["final_rank"])),
            "suitability_score": suitability,
            "score_components": {
                "dna_match_score": round(float(row["absolute_fit_percentile"]) * 100, 1),
                "market_score": round(float(row["market_opportunity_percentile"]) * 100, 1),
                "proximity_risk_score": proximity_risk_score(row.get("same_brand_nearest_distance_m")),
                "competition_attractiveness_score": round(float(row["low_competition_risk_percentile"]) * 100, 1),
            },
            "facts": {
                "min_distance_to_existing_store_m": row.get("same_brand_nearest_distance_m"),
                "bakery_franchise_share": row.get("bakery_franchise_store_share"),
            },
            "consumer_profile": classify_consumer_profile(row, row["_avg_ticket_pct"]),
            "data_quality": dict(zip(
                ["coverage_score", "confidence_label"],
                PROFILE_STABILITY_MAP.get(row.get("profile_stability"), (50, "알수없음"))
            )) | {"is_mock": False},
            "positive_factors": positive_drivers_to_sentences(row.get("positive_drivers")),
            "risk_factors": caution_flags_to_sentences(row.get("caution_flags")),
            "next_checks": risk_flag_to_checks(row.get("risk_review_flag")),
        }
        recommendations.append(rec)

    dna_summary = build_dna_summary(eligible, recommendations)
    return recommendations, dna_summary


def build_dna_summary(eligible_df, recommendations):
    if not recommendations:
        return {
            "headline": "추천 가능한 상권이 부족합니다",
            "strengths": [], "cautions": [], "evidence_store_count": 0,
        }

    top = recommendations[:5]
    strength_pool = [s for r in top for s in r["positive_factors"]]
    caution_pool = [s for r in top for s in r["risk_factors"]]

    def top_unique(pool, k=3):
        seen, out = set(), []
        for s in pool:
            if s not in seen:
                out.append(s)
                seen.add(s)
            if len(out) >= k:
                break
        return out

    evidence_store_count = int(eligible_df["profile_area_count"].iloc[0]) \
        if "profile_area_count" in eligible_df.columns and pd.notna(eligible_df["profile_area_count"].iloc[0]) \
        else len(eligible_df)

    best = recommendations[0]
    headline = f"{best['area_name']} 등 {best['consumer_profile']['primary_segment']} 중심 상권에서 강점"

    return {
        "headline": headline,
        "strengths": top_unique(strength_pool),
        "cautions": top_unique(caution_pool),
        "evidence_store_count": evidence_store_count,
    }


# =========================================================
# 7. 전체 실행
# =========================================================

def main():
    recs = load_and_join()

    result = {}
    for brand_id, brand_df in recs.groupby("brand_id"):
        brand_name = brand_df["brand_name"].iloc[0]
        recommendations, dna_summary = build_for_brand(brand_df)
        result[brand_id] = {
            "brand_name": brand_name,
            "recommendations": recommendations,
            "dna_summary": dna_summary,
        }
        print(f"[{brand_name}] 추천 상권 {len(recommendations)}건 생성")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)

    print(f"\n완료 -> {OUTPUT_PATH}")
    return result


if __name__ == "__main__":
    main()