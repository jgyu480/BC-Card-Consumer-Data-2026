"""
최종 조립 스크립트 (assemble_result_v3.py) (최종)
=====================================================

역할
----
build_recommendations_v3.py의 결과(recommendations[], dna_summary)와
build_portfolios_v3.py의 결과(portfolios[])를 브랜드 기준으로 합치고,
- decision_summary (LLM 불필요, 고정 템플릿)
- brand_type (재료가 없어서 상위 추천 상권 소비자 구성으로 잠정 분류 — provisional)
- 정적 필드(schema_version, is_mock, reference_period, display_disclaimer,
  service_context, ui_copy)
를 추가해서 result_schema.json에 맞는 최종 result.json 하나로 만든다.

디렉토리
--------
PART-VI/APP-03/data_pipeline/assemble_result_v3.py

입력
----
1. PART-VI/APP-03/outputs/recommendations_output_v3.json   (build_recommendations_v3.py 결과)
2. PART-VI/PORTFOLIO-01/outputs/portfolios_output_v3.json   (build_portfolios_v3.py 결과)

출력
----
PART-VI/APP-03/outputs/result.json
-> 이걸 utils/data_loader.py가 읽어서 화면에 뿌림 (mock_recommendations.json 대체)

실행
----
    python assemble_result_v3.py
(어느 위치에서 실행하든 경로는 자동으로 찾음. 단, 1번·2번 입력 파일이
 먼저 생성돼 있어야 함 — build_recommendations_v3.py, build_portfolios_v3.py를
 먼저 실행할 것)
"""

import json
from pathlib import Path


def eun_neun(word):
    """한글 단어 뒤에 '은'/'는' 중 맞는 조사를 붙여 반환할 때 쓸 마지막 글자 받침 판정"""
    if not word:
        return "는"
    last_char = word[-1]
    code = ord(last_char)
    if 0xAC00 <= code <= 0xD7A3:  # 완성형 한글 범위
        has_batchim = (code - 0xAC00) % 28 != 0
        return "은" if has_batchim else "는"
    return "는"  # 한글이 아닌 문자로 끝나면 기본값


# =========================================================
# CONFIG — 경로
# =========================================================

SCRIPT_DIR = Path(__file__).resolve().parent                 # .../PART-VI/APP-03/data_pipeline
APP03_DIR = SCRIPT_DIR.parent                                  # .../PART-VI/APP-03
ROOT = SCRIPT_DIR.parents[2]                                    # 리포 루트

RECOMMENDATIONS_PATH = APP03_DIR / "outputs" / "recommendations_output_v3.json"
PORTFOLIOS_PATH = ROOT / "PART-VI" / "PORTFOLIO-01" / "outputs" / "portfolios_output_v3.json"
LLM01_DIR = ROOT / "PART-V" / "LLM-01" / "scripts"

OUTPUT_PATH = APP03_DIR / "outputs" / "result_v3.json"


# =========================================================
# CONFIG — 사용자가 확인/결정해야 할 값
# =========================================================

SCHEMA_VERSION = "1.1.0"
# TODO: MODEL-01이 실제로 어떤 기준월(STRD_YYMM) 데이터로 학습/추론했는지
# A에게 확인 후 정확한 값으로 교체 (지금은 데이터 레이아웃 문서 기준 추정치)
REFERENCE_PERIOD = "2026H1"

DISPLAY_DISCLAIMER = (
    "본 결과는 브랜드의 기존 입점환경과 서울 후보 상권의 소비·경쟁 특성을 "
    "비교한 의사결정용 적합도이며, 예상 매출이나 출점 성공 확률을 의미하지 않습니다."
)

SERVICE_CONTEXT = {
    "target_user": "베이커리 프랜차이즈 본사 사업개발팀",
    "primary_job": "이번 분기에 함께 검토할 서울 출점 후보 조합 선정",
    "analyzed_population": "BC카드 이용 소비자 집계",
    "user_inputs": [
        {"field": "brand_id", "label": "브랜드", "required": True},
        {
            "field": "desired_store_count", "label": "희망 출점 수",
            "allowed_values": [1, 2, 3], "required": True,
        },
    ],
    "decision_flow": [
        "브랜드와 희망 출점 수 선택",
        "추천 포트폴리오 확인",
        "구성 상권과 추천 근거 비교",
        "긍정 요인·위험 요인·데이터 신뢰도 확인",
        "임대료·공실·현장 유동 등 추가 검토",
    ],
}

UI_COPY = {
    # v3: service_title/portfolio_section_title/area_section_title/risk_section_title/
    # disclaimer는 실제로 화면 어디서도 안 읽고 있었음 (각 컴포넌트 파일이 비슷한
    # 문구를 직접 하드코딩해서 씀 — 예: tab2_portfolio.py의 "추천 포트폴리오").
    # disclaimer는 최상위 display_disclaimer 필드와 완전히 중복이기도 함.
    # 실제로 쓰이는 portfolio_score_note만 남기고 정리함.
    "portfolio_score_note": (
        "점수는 선택하신 출점 수 안에서의 순위입니다. "
        "출점 수가 다른 옵션끼리 점수를 직접 비교하지 마세요."
    ),
}

# glossary.json 경로 (지표 용어 툴팁용, top-level로 그대로 실어 보냄)
GLOSSARY_PATH = LLM01_DIR / "glossary.json"


# =========================================================
# 1. 로드
# =========================================================

def load_json(path):
    if not path.exists():
        raise SystemExit(
            f"[에러] {path} 가 없습니다. "
            f"build_recommendations_v3.py / build_portfolios_v3.py를 먼저 실행하세요."
        )
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# =========================================================
# 2. brand_type — v2에서는 build_recommendations_v3.py가 이미 계산해서
#    넘겨줌 (기존 매장 기반, 더 정확함). 여기서 재계산하지 않고 그대로 통과.
# =========================================================



# =========================================================
# 3. decision_summary (LLM 불필요, 고정 템플릿)
# =========================================================

def build_decision_summary(brand_name, brand_type, recommendations, portfolios):
    if not recommendations:
        return {
            "headline": "추천 가능한 상권이 부족합니다",
            "best_single_area": None,
            "best_two_area_portfolio": None,
            "key_risk": "추천 가능한 상권이 부족합니다",
            "recommended_action": "후보 상권 재검토가 필요합니다",
        }

    best_single = recommendations[0]

    two_store = [
        p for p in portfolios
        if p["desired_store_count"] == 2 and p["portfolio_rank"] == 1
    ]
    best_two = two_store[0] if two_store else None

    # key_risk: 단일 상권과 2개 조합 중 risk_factors가 있는 쪽에서 첫 항목
    key_risk = None
    if best_single["risk_factors"]:
        key_risk = best_single["risk_factors"][0]
    elif best_two and best_two["risk_factors"]:
        key_risk = best_two["risk_factors"][0]
    else:
        key_risk = "모델 기준 특이 위험 요인 없음 (현장 확인은 별도 권장)"

    if best_two:
        recommended_action = (
            f"{brand_name}{eun_neun(brand_name)} {best_single['area_name']}을(를) 최우선 검토 대상으로 "
            f"보되, {' + '.join(best_two['area_names'])} 조합도 함께 비교 검토할 것을 권장합니다."
        )
    else:
        recommended_action = (
            f"{brand_name}{eun_neun(brand_name)} {best_single['area_name']}을(를) 우선 검토 대상으로 권장합니다. "
            f"(2개 조합 후보는 현재 부족)"
        )

    return {
        "headline": f"{brand_type} DNA를 기준으로 {best_single['area_name']}을(를) 최우선 후보로 검토",
        "best_single_area": best_single["area_name"],
        "best_two_area_portfolio": (
            best_two["area_names"] if best_two else None
        ),
        "key_risk": key_risk,
        "recommended_action": recommended_action,
    }


# =========================================================
# 4. 브랜드 단위 조립
# =========================================================

def assemble_brand(brand_id, rec_data, portfolio_data):
    brand_name = rec_data["brand_name"]
    recommendations = rec_data["recommendations"]
    dna_summary = rec_data["dna_summary"]
    portfolios = portfolio_data["portfolios"] if portfolio_data else []

    return {
        "brand_id": brand_id,
        "brand_name": brand_name,
        "brand_type": rec_data["brand_type"],  # build_recommendations_v3.py가 이미 계산
        # v3: 브랜드 전체를 뭉친 ai_explanation 필드는 제거함.
        # 대신 recommendations[]마다 area_explanation이 상권 단위로 이미 들어있음
        # (Phase 9 "상권 클릭 시 개별 설명" 요구사항에 맞춰 v3에서 설계 변경).
        "dna_summary": dna_summary,
        "decision_summary": build_decision_summary(brand_name, rec_data["brand_type"], recommendations, portfolios),
        "recommendations": recommendations,
        "portfolios": portfolios,
    }


# =========================================================
# 5. 전체 실행
# =========================================================

def main():
    rec_all = load_json(RECOMMENDATIONS_PATH)
    portfolio_all = load_json(PORTFOLIOS_PATH)
    with open(GLOSSARY_PATH, encoding="utf-8") as f:
        glossary = json.load(f)

    brands = []
    missing_portfolio_brands = []
    low_coverage_brands = []
    for brand_id, rec_data in rec_all.items():
        portfolio_data = portfolio_all.get(brand_id)
        if portfolio_data is None:
            missing_portfolio_brands.append(rec_data["brand_name"])

        recs = rec_data["recommendations"]
        with_expl = sum(1 for r in recs if r.get("area_explanation"))
        if recs and with_expl < len(recs):
            low_coverage_brands.append(
                f"{rec_data['brand_name']}({with_expl}/{len(recs)})"
            )

        brands.append(assemble_brand(brand_id, rec_data, portfolio_data))

    if missing_portfolio_brands:
        print(f"[경고] 포트폴리오 결과가 없는 브랜드: {missing_portfolio_brands}")
    if low_coverage_brands:
        print(f"[참고] area_explanation이 일부 상권에 없는 브랜드(설명 있는 상권/전체 상권): {low_coverage_brands}")

    result = {
        "schema_version": SCHEMA_VERSION,
        "is_mock": False,
        "reference_period": REFERENCE_PERIOD,
        "display_disclaimer": DISPLAY_DISCLAIMER,
        "service_context": SERVICE_CONTEXT,
        "ui_copy": UI_COPY,
        "glossary": glossary,  # 지표 용어 툴팁용 (B가 만든 label/description 그대로)
        "brands": brands,
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)

    print(f"브랜드 {len(brands)}개 조립 완료 -> {OUTPUT_PATH}")
    return result


if __name__ == "__main__":
    main()