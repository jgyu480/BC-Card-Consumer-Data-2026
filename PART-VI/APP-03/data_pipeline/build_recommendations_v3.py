"""
단일 상권 추천(recommendations[]) + 브랜드 요약(dna_summary) 생성 스크립트 v3 (최종)
=====================================================


필요한 입력 파일
----------------
1. PART-III/MODEL-01/outputs/final_model_v3_1/model01_final_recommendations_v3_1.parquet
2. PART-II/DATA-02/outputs/area_feature_master.parquet
3. PART-II/DATA-01/brand_area_presence.parquet
4. PART-V/LLM-01/scripts/code_to_text_mapping.json
5. PART-V/LLM-01/scripts/llm01_final_explanations.json        (B의 1~3위, 원본 그대로)
6. PART-V/LLM-01/scripts/llm01_explanations_api_4to20.json    (C의 4~20위 확장분)
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
LLM_TOP3_PATH = LLM01_DIR / "llm01_final_explanations.json"
LLM_4TO20_PATH = LLM01_DIR / "llm01_explanations_api_4to20.json"

OUTPUT_DIR = APP03_DIR / "outputs"
OUTPUT_PATH = OUTPUT_DIR / "recommendations_output_v3.json"

MAX_RECOMMENDATIONS_PER_BRAND = 20

PROXIMITY_MIN_RISK_DISTANCE_M = 500
PROXIMITY_SAFE_DISTANCE_M = 2000

AGE_LABELS = {1: "20대 이하", 2: "20대", 3: "30대", 4: "40대", 5: "50대", 6: "60대 이상"}

CORPORATE_SHARE_THRESHOLD = 0.6746
FOREIGN_SHARE_THRESHOLD = 0.5794

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

AGE_TO_BRAND_TYPE = {
    "20대 이하": "젊은층 중심형", "20대": "젊은층 중심형", "30대": "젊은층 중심형",
    "40대": "중장년층 중심형", "50대": "중장년층 중심형",
    "60대 이상": "시니어 중심형",
}
DEFAULT_BRAND_TYPE = "복합형"

# 1위-2위 연령대 비중 차이가 이 값 미만이면 "확실한 우세"로 안 보고
# 복합형으로 처리 (더베이크 사례: 기존 매장 6개, 1위 50대 12.0% vs
# 2위 30대 11.4%, 차이 0.6%p처럼 사실상 거의 균등한 경우)
BRAND_TYPE_MIN_MARGIN = 0.02

AREA_AGE_SHARE_COLS = [
    "bakery_age_10_share_amt", "bakery_age_20_share_amt", "bakery_age_30_share_amt",
    "bakery_age_40_share_amt", "bakery_age_50_share_amt", "bakery_age_60_above_share_amt",
]
AREA_AGE_COL_TO_LABEL = dict(zip(AREA_AGE_SHARE_COLS, AGE_LABELS.values()))

RISK_REVIEW_FLAG_CHECKS = {
    "profile_stability_moderate__confirm_local_site_conditions": "현장에서 실제 입지 여건 확인 필요",
    "no_model_level_high_risk_flag": None,
}

# 브랜드 개요(overview) 페이지의 강점/주의점 "태그"용 짧은 문구.
# positive_factors/risk_factors(area detail용 완전한 문장)와는 별도로 관리함 —
# 태그는 pill 모양이라 문장 통째로 넣으면 줄바꿈이 길게 늘어짐. 짧은 핵심어만.
SHORT_POSITIVE_LABEL = {
    "brand_environment_fit": "소비환경 적합",
    "brand_specific_advantage": "브랜드 강점",
    "market_opportunity": "시장 규모",
    "low_competition_risk": "경쟁 우위",
}

SHORT_CAUTION_LABEL = {
    "competition_risk_elevated_but_below_exclusion": "경쟁 다소 높음",
    "competition_risk_moderate": "경쟁 보통",
    "no_model_level_caution_flag": None,
    "profile_stability_moderate": "데이터 안정성 보통",
    "same_brand_distance_750m_to_1000m_review": "기존 매장 근접",
}


# =========================================================
# 0. B(LLM-01)의 실제 매핑/설명 파일 로드
# =========================================================

def load_llm01_assets():
    with open(CODE_MAPPING_PATH, encoding="utf-8") as f:
        mapping = json.load(f)
    positive_templates = mapping["positive_drivers"]
    caution_sentences = mapping["caution_flags"]

    with open(LLM_TOP3_PATH, encoding="utf-8") as f:
        top3_raw = json.load(f)
    top3_by_brand_area = {}
    for entry in top3_raw:
        if entry.get("status") != "success" or not entry.get("explanation"):
            continue
        brand_name = entry["brand_name"]
        area_names = [a["area_name"] for a in entry["facts"]["areas"]]
        paragraphs = [p.strip() for p in entry["explanation"].split("\n\n") if p.strip()]
        for para in paragraphs[1:]:
            for area_name in area_names:
                if para.startswith(area_name):
                    top3_by_brand_area[(brand_name, area_name)] = para
                    break

    ext_by_brand_area = {}
    if LLM_4TO20_PATH.exists():
        with open(LLM_4TO20_PATH, encoding="utf-8") as f:
            ext_raw = json.load(f)
        for entry in ext_raw:
            if entry.get("status") == "success" and entry.get("explanation"):
                key = (entry["brand_name"], entry["facts"]["area_name"])
                ext_by_brand_area[key] = entry["explanation"]
    else:
        print(f"[경고] {LLM_4TO20_PATH} 없음 — 4~20위는 area_explanation이 null로 나갑니다.")

    return positive_templates, caution_sentences, top3_by_brand_area, ext_by_brand_area


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
# 3. 코드 문자열 파싱 -> 문장
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
        sentences.append("특별히 확인된 위험 요인 없음")
    return sentences


def positive_drivers_to_short_tags(raw, row):
    """dna_summary 태그용 짧은 문구. 완전한 문장(positive_drivers_to_sentences)과
    별도로 관리 — pill 모양 태그에 긴 문장을 넣으면 줄바꿈이 늘어지는 문제가 있었음."""
    tags = []
    for part in parse_pipe_string(raw):
        code = part.split("=")[0].strip()
        short_label = SHORT_POSITIVE_LABEL.get(code)
        pct_col = FACTOR_PERCENTILE_COL.get(code)
        if not short_label or not pct_col or pd.isna(row.get(pct_col)):
            continue
        pct = (1 - float(row[pct_col])) * 100
        tags.append(f"{short_label} 상위 {pct:.0f}%")
    return tags


def caution_flags_to_short_tags(raw):
    tags = []
    for code in parse_pipe_string(raw):
        tag = SHORT_CAUTION_LABEL.get(code)
        if tag:
            tags.append(tag)
    return tags


# =========================================================
# 4. 소비자 구성 서술 (v3: 법인/외국인 비중 반영)
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

    extras = []
    corp = row.get("bc_corporate_share_amt")
    foreign = row.get("bc_foreign_share_amt")
    if pd.notna(corp) and corp >= CORPORATE_SHARE_THRESHOLD:
        extras.append("법인 수요 비중 높음")
    if pd.notna(foreign) and foreign >= FOREIGN_SHARE_THRESHOLD:
        extras.append("외국인 방문객 비중 높음")
    if extras:
        demand_context += f" ({', '.join(extras)})"

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
# 6. next_checks (v3: risk_review_flag 반영해서 상권마다 다르게)
# =========================================================

def build_next_checks(risk_review_flag):
    checks = ["후보별 임대료와 예상 고정비 비교", "현장 유동과 접근성 확인"]
    extra = RISK_REVIEW_FLAG_CHECKS.get(risk_review_flag)
    if extra:
        checks.append(extra)
    return checks


# =========================================================
# 7. brand_type 분류 (v2와 동일 — 기존 매장 기반, 없으면 폴백)
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

    sorted_ages = sorted(weighted.items(), key=lambda x: x[1], reverse=True)
    dominant_age, top_value = sorted_ages[0]
    second_value = sorted_ages[1][1] if len(sorted_ages) > 1 else 0

    # 1위-2위 비중 차이가 2%p 미만이면 "복합형"으로 처리.
    # (더베이크 사례: 기존 매장 6개뿐이라 1위 50대 12.0% vs 2위 30대 11.4%로
    # 사실상 균등한데 "중장년층 중심형"이라고 단정적으로 표시되던 문제 수정)
    if (top_value - second_value) < BRAND_TYPE_MIN_MARGIN:
        return DEFAULT_BRAND_TYPE

    return AGE_TO_BRAND_TYPE.get(dominant_age, DEFAULT_BRAND_TYPE)


def classify_brand_type_fallback(recommendations):
    if not recommendations:
        return DEFAULT_BRAND_TYPE
    contexts = " ".join(r["consumer_profile"]["demand_context"] for r in recommendations[:3])
    if "20대" in contexts or "30대" in contexts:
        return "젊은층 중심형"
    if "50대" in contexts or "60대" in contexts:
        return "중장년층 중심형"
    return DEFAULT_BRAND_TYPE


# =========================================================
# 8. 브랜드별 recommendations[] + dna_summary
# =========================================================

def build_for_brand(brand_id, brand_df, positive_templates, caution_sentences,
                     top3_by_brand_area, ext_by_brand_area):
    brand_df = brand_df.copy()
    brand_df["_avg_ticket_pct"] = brand_df["bakery_avg_ticket"].rank(pct=True)

    cap = brand_df["available_recommendation_count"].iloc[0]
    cap = int(cap) if pd.notna(cap) else MAX_RECOMMENDATIONS_PER_BRAND
    n = min(cap, MAX_RECOMMENDATIONS_PER_BRAND)

    eligible = brand_df[
        (brand_df["risk_pass"] == True) & (brand_df["eligible_new_opening"] == True)
    ].sort_values("final_rank").head(n)

    brand_name = brand_df["brand_name"].iloc[0]

    recommendations = []
    short_tags_by_area = {}  # area_id -> (positive_tags, risk_tags), dna_summary 태그용
    for _, row in eligible.iterrows():
        suitability = round(float(row["final_suitability_score"]) * 100, 1)
        final_rank = int(row["final_rank"])
        area_name = row["area_name"]

        if final_rank <= 3:
            area_explanation = top3_by_brand_area.get((brand_name, area_name))
        else:
            area_explanation = ext_by_brand_area.get((brand_name, area_name))

        rec = {
            "area_id": row["area_id"],
            "area_name": area_name,
            "district_nm": row.get("ccg_nm"),
            "centroid_latitude": row.get("centroid_latitude"),
            "centroid_longitude": row.get("centroid_longitude"),
            "rank": final_rank,
            "recommendation_label": recommendation_label(final_rank),
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
                "monthly_sales_amt": row.get("bakery_thsmon_selng_amt"),
                "monthly_transaction_count": row.get("bakery_thsmon_selng_co"),
                "competitor_count_500m": row.get("bakery_competitor_count_500m_excl_brand"),
                "competitor_count_1000m": row.get("bakery_competitor_count_1000m_excl_brand"),
                "nearest_competitor_m": row.get("bakery_competitor_nearest_m_excl_brand"),
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
            "next_checks": build_next_checks(row.get("risk_review_flag")),
            "area_explanation": area_explanation,
        }
        recommendations.append(rec)
        short_tags_by_area[row["area_id"]] = (
            positive_drivers_to_short_tags(row.get("positive_drivers"), row),
            caution_flags_to_short_tags(row.get("caution_flags")),
        )

    dna_summary = build_dna_summary(eligible, recommendations, short_tags_by_area)
    return recommendations, dna_summary


def build_dna_summary(eligible_df, recommendations, short_tags_by_area):
    if not recommendations:
        return {"headline": "추천 가능한 상권이 부족합니다", "strengths": [], "cautions": [], "evidence_store_count": 0}

    top = recommendations[:5]
    strength_pool = [
        tag for r in top for tag in short_tags_by_area.get(r["area_id"], ([], []))[0]
    ]
    caution_pool = [
        tag for r in top for tag in short_tags_by_area.get(r["area_id"], ([], []))[1]
    ]

    # "경쟁 다소 높음"/"경쟁 보통"은 상권 하나에는 둘 중 하나만 붙는 값인데,
    # 여기선 상위 5개 상권을 모아서 태그를 뽑다 보니 상권마다 다른 값이면
    # 둘 다 같이 뜨는 문제가 있었음(브랜드 하나가 모순돼 보임). 둘 다 있으면
    # 더 심각한 쪽("경쟁 다소 높음")만 남기고 "경쟁 보통"은 제거.
    if "경쟁 다소 높음" in caution_pool and "경쟁 보통" in caution_pool:
        caution_pool = [t for t in caution_pool if t != "경쟁 보통"]

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
# 9. 전체 실행
# =========================================================

def main():
    recs = load_and_join()
    presence_df = load_brand_presence()
    positive_templates, caution_sentences, top3_by_brand_area, ext_by_brand_area = load_llm01_assets()

    fallback_used = []
    no_explanation_areas = []
    result = {}
    for brand_id, brand_df in recs.groupby("brand_id"):
        brand_name = brand_df["brand_name"].iloc[0]
        recommendations, dna_summary = build_for_brand(
            brand_id, brand_df, positive_templates, caution_sentences,
            top3_by_brand_area, ext_by_brand_area
        )

        brand_type = classify_brand_type_from_presence(brand_id, presence_df)
        if brand_type is None:
            brand_type = classify_brand_type_fallback(recommendations)
            fallback_used.append(brand_name)

        for r in recommendations:
            if r["area_explanation"] is None:
                no_explanation_areas.append((brand_name, r["area_name"], r["rank"]))

        result[brand_id] = {
            "brand_name": brand_name,
            "brand_type": brand_type,
            "recommendations": recommendations,
            "dna_summary": dna_summary,
        }
        with_expl = sum(1 for r in recommendations if r["area_explanation"])
        print(f"[{brand_name}] 추천 {len(recommendations)}건 (설명 {with_expl}건) | 유형: {brand_type}")

    if fallback_used:
        print(f"\n[참고] brand_type 폴백 사용된 브랜드: {fallback_used}")
    if no_explanation_areas:
        print(f"[참고] area_explanation 없는 상권 {len(no_explanation_areas)}건 (예: {no_explanation_areas[:3]})")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)

    print(f"\n완료 -> {OUTPUT_PATH}")
    return result


if __name__ == "__main__":
    main()