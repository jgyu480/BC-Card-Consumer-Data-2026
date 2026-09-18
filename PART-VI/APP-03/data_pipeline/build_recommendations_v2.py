"""
단일 상권 추천(recommendations[]) + 브랜드 요약(dna_summary) 생성 스크립트 v2
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
# CONFIG — 경로
# =========================================================

SCRIPT_DIR = Path(__file__).resolve().parent               # .../PART-VI/APP-03/data_pipeline
APP03_DIR = SCRIPT_DIR.parent
ROOT = SCRIPT_DIR.parents[2]

MODEL01_DIR = ROOT / "PART-III" / "MODEL-01" / "outputs" / "final_model_v3_1"
DATA01_DIR = ROOT / "PART-II" / "DATA-01"
DATA02_DIR = ROOT / "PART-II" / "DATA-02" / "outputs"
LLM01_DIR = ROOT / "PART-V" / "LLM-01" / "scripts"

MODEL01_RECS_PATH = MODEL01_DIR / "model01_final_recommendations_v3_1.parquet"
AREA_MASTER_PATH = DATA02_DIR / "area_feature_master.parquet"
BRAND_PRESENCE_PATH = DATA01_DIR / "brand_area_presence.parquet"
CODE_MAPPING_PATH = LLM01_DIR / "code_to_text_mapping.json"
LLM_EXPLANATIONS_PATH = LLM01_DIR / "llm01_final_explanations.json"

OUTPUT_DIR = APP03_DIR / "outputs"
OUTPUT_PATH = OUTPUT_DIR / "recommendations_output_v2.json"

MAX_RECOMMENDATIONS_PER_BRAND = 20

PROXIMITY_MIN_RISK_DISTANCE_M = 500
PROXIMITY_SAFE_DISTANCE_M = 2000

AGE_LABELS = {1: "20대 이하", 2: "20대", 3: "30대", 4: "40대", 5: "50대", 6: "60대 이상"}

# positive_drivers 코드 -> MODEL-01 percentile 컬럼 (템플릿에 값 채울 때 씀)
FACTOR_PERCENTILE_COL = {
    "brand_environment_fit": "absolute_fit_percentile",
    "brand_specific_advantage": "brand_specificity_percentile",
    "market_opportunity": "market_opportunity_percentile",
    "low_competition_risk": "low_competition_risk_percentile",
}

PROFILE_STABILITY_MAP = {
    "high_profile_stability": (90, "높음"),
    "moderate_profile_stability": (65, "보통"),
    "low_profile_stability": (40, "낮음"),
}

# brand_type 분류: 연령대 -> 유형 라벨
AGE_TO_BRAND_TYPE = {
    "20대 이하": "젊은층 중심형", "20대": "젊은층 중심형", "30대": "젊은층 중심형",
    "40대": "중장년층 중심형", "50대": "중장년층 중심형",
    "60대 이상": "시니어 중심형",
}
DEFAULT_BRAND_TYPE = "복합형"

AREA_AGE_SHARE_COLS = [
    "bakery_age_10_share_amt", "bakery_age_20_share_amt", "bakery_age_30_share_amt",
    "bakery_age_40_share_amt", "bakery_age_50_share_amt", "bakery_age_60_above_share_amt",
]
AREA_AGE_COL_TO_LABEL = dict(zip(AREA_AGE_SHARE_COLS, AGE_LABELS.values()))


# =========================================================
# 0. B(LLM-01)의 실제 매핑/설명 파일 로드
# =========================================================

def load_llm01_assets():
    with open(CODE_MAPPING_PATH, encoding="utf-8") as f:
        mapping = json.load(f)
    positive_templates = mapping["positive_drivers"]   # {code: {"template": "..."}}
    caution_sentences = mapping["caution_flags"]         # {code: "..." | null}

    with open(LLM_EXPLANATIONS_PATH, encoding="utf-8") as f:
        explanations = json.load(f)
    # brand_name 기준 lookup (B 쪽에 brand_id가 없어서 이름으로 join)
    explanation_by_brand = {e["brand_name"]: e for e in explanations if e.get("status") == "success"}

    return positive_templates, caution_sentences, explanation_by_brand


# =========================================================
# 1. 데이터 로드 + 결합
# =========================================================

def load_and_join():
    recs = pd.read_parquet(MODEL01_RECS_PATH)
    area_master = pd.read_parquet(AREA_MASTER_PATH)

    recs["area_id"] = recs["area_id"].astype(str)
    area_master["area_id"] = area_master["area_id"].astype(str)

    join_cols = ["area_id", "ccg_nm", "bakery_franchise_store_share",
                 "centroid_x_epsg5181", "centroid_y_epsg5181"] + AREA_AGE_SHARE_COLS
    recs = recs.merge(area_master[join_cols], on="area_id", how="left")

    transformer = Transformer.from_crs("EPSG:5181", "EPSG:4326", always_xy=True)
    lon, lat = transformer.transform(
        recs["centroid_x_epsg5181"].values, recs["centroid_y_epsg5181"].values
    )
    recs["centroid_longitude"] = lon
    recs["centroid_latitude"] = lat
    return recs


def load_brand_presence():
    presence = pd.read_parquet(BRAND_PRESENCE_PATH)
    area_master = pd.read_parquet(AREA_MASTER_PATH)
    presence["area_id"] = presence["area_id"].astype(str)
    area_master["area_id"] = area_master["area_id"].astype(str)

    active = presence[presence["currently_active"] == True].copy()
    merged = active.merge(area_master[["area_id"] + AREA_AGE_SHARE_COLS], on="area_id", how="left")
    return merged


# =========================================================
# 2. 근접 위험 점수
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
# 3. 코드 문자열 파싱 -> B의 실제 문장/템플릿으로 변환
# =========================================================

def parse_pipe_string(s):
    if pd.isna(s) or not s:
        return []
    return [p.strip() for p in s.split("|") if p.strip()]


def positive_drivers_to_sentences(raw, row, positive_templates):
    sentences = []
    for part in parse_pipe_string(raw):
        code = part.split("=")[0].strip()
        template_info = positive_templates.get(code)
        pct_col = FACTOR_PERCENTILE_COL.get(code)
        if not template_info or not pct_col or pd.isna(row.get(pct_col)):
            continue
        pct = (1 - float(row[pct_col])) * 100
        sentence = template_info["template"].format(pct=pct, area=row["area_name"])
        sentences.append(sentence)
    return sentences


def caution_flags_to_sentences(raw, caution_sentences):
    sentences = []
    for code in parse_pipe_string(raw):
        sentence = caution_sentences.get(code)
        if sentence:
            sentences.append(sentence)
    if not sentences:
        # 빈 배열이면 화면 코드가 risk_factors[0]을 가정하고 접근하는 곳에서
        # IndexError가 남 (v1에서 실제로 확인된 버그). B의 LLM-01 문서와 같은
        # 원칙으로 최소 1개는 채워서 내보냄.
        sentences.append("특별히 확인된 위험 요인 없음")
    return sentences


# =========================================================
# 4. 소비자 구성 서술 (v1과 동일)
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
# 5. 추천 라벨 (v1과 동일)
# =========================================================

def recommendation_label(final_rank):
    if final_rank <= 3:
        return "최우선 검토"
    if final_rank <= 10:
        return "우선 검토"
    return "비교 후보"


# =========================================================
# 6. brand_type 분류 v2 — 실제 기존 매장 기준, 없으면 추천 상권 기준 폴백
# =========================================================

def classify_brand_type_from_presence(brand_id, presence_df):
    g = presence_df[presence_df["brand_id"] == brand_id]
    if g.empty or g["store_cnt"].sum() == 0:
        return None
    w = g["store_cnt"]
    weighted = {}
    for col in AREA_AGE_SHARE_COLS:
        vals = g[col].fillna(0)
        if vals.isna().all():
            continue
        weighted[AREA_AGE_COL_TO_LABEL[col]] = (vals * w).sum() / w.sum()
    if not weighted:
        return None
    dominant_age = max(weighted, key=weighted.get)
    return AGE_TO_BRAND_TYPE.get(dominant_age, DEFAULT_BRAND_TYPE)


def classify_brand_type_fallback(recommendations):
    """기존 매장 데이터가 없는 브랜드용 v1 방식 폴백 (추천 상권 기준)."""
    if not recommendations:
        return DEFAULT_BRAND_TYPE
    contexts = " ".join(r["consumer_profile"]["demand_context"] for r in recommendations[:3])
    if "20대" in contexts or "30대" in contexts:
        return "젊은층 중심형"
    if "50대" in contexts or "60대" in contexts:
        return "중장년층 중심형"
    return DEFAULT_BRAND_TYPE


# =========================================================
# 7. 브랜드별 recommendations[] + dna_summary + ai_explanation
# =========================================================

def build_for_brand(brand_id, brand_df, positive_templates, caution_sentences):
    brand_df = brand_df.copy()
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
            "positive_factors": positive_drivers_to_sentences(
                row.get("positive_drivers"), row, positive_templates
            ),
            "risk_factors": caution_flags_to_sentences(row.get("caution_flags"), caution_sentences),
            "next_checks": ["후보별 임대료와 예상 고정비 비교", "현장 유동과 접근성 확인"],
        }
        recommendations.append(rec)

    dna_summary = build_dna_summary(eligible, recommendations)
    return recommendations, dna_summary


def build_dna_summary(eligible_df, recommendations):
    if not recommendations:
        return {"headline": "추천 가능한 상권이 부족합니다", "strengths": [], "cautions": [], "evidence_store_count": 0}

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
# 8. 전체 실행
# =========================================================

def main():
    recs = load_and_join()
    presence_df = load_brand_presence()
    positive_templates, caution_sentences, explanation_by_brand = load_llm01_assets()

    fallback_used = []
    result = {}
    for brand_id, brand_df in recs.groupby("brand_id"):
        brand_name = brand_df["brand_name"].iloc[0]
        recommendations, dna_summary = build_for_brand(
            brand_id, brand_df, positive_templates, caution_sentences
        )

        brand_type = classify_brand_type_from_presence(brand_id, presence_df)
        if brand_type is None:
            brand_type = classify_brand_type_fallback(recommendations)
            fallback_used.append(brand_name)

        explanation_entry = explanation_by_brand.get(brand_name)
        ai_explanation = explanation_entry["explanation"] if explanation_entry else None

        result[brand_id] = {
            "brand_name": brand_name,
            "brand_type": brand_type,
            "recommendations": recommendations,
            "dna_summary": dna_summary,
            "ai_explanation": ai_explanation,
        }
        print(f"[{brand_name}] 추천 {len(recommendations)}건 | 유형: {brand_type} | "
              f"AI설명: {'있음' if ai_explanation else '없음(top3 밖 범위이거나 미매칭)'}")

    if fallback_used:
        print(f"\n[참고] brand_type 폴백(기존 매장 데이터 없음) 사용된 브랜드: {fallback_used}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)

    print(f"\n완료 -> {OUTPUT_PATH}")
    return result


if __name__ == "__main__":
    main()