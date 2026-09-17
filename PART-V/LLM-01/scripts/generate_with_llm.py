# -*- coding: utf-8 -*-
"""
규칙 기반으로 만든 재료를 바탕으로, OpenAI API를 호출해서
24개 브랜드 전체의 최종 자연어 설명을 생성하고 파일로 저장한다.
"""
import json
import os
import time
from collections import defaultdict

import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

PARQUET_PATH = r"C:\Users\lucy0\Documents\YONSEI\YBIGTA\공모전\BC-Card-Consumer-Data-2026\PART-III\MODEL-01\outputs\final_model_v3_1\model01_final_recommendations_v3_1.parquet"
MAPPING_PATH = "code_to_text_mapping.json"
OUTPUT_PATH = "llm01_final_explanations_v2.json"

TIE_THRESHOLD = 0.003
TOP_N = 3
MIN_PCT_DISPLAY = 0.01

FIT_ORDER = ["brand_environment_fit", "brand_specific_advantage", "market_opportunity"]
COMPETITION_DRIVER = "low_competition_risk"
COMPETITION_CAUTION_CODES = {"competition_risk_moderate", "competition_risk_elevated_but_below_exclusion"}

MODEL_NAME = "gpt-4o-mini"

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

with open(MAPPING_PATH, "r", encoding="utf-8") as f:
    MAP = json.load(f)


def parse_kv_pipe(raw: str):
    if not raw:
        return []
    return [tuple(p.strip() for p in chunk.partition("=")[::2]) for chunk in raw.split(" | ")]


def parse_flags(raw: str):
    if not raw:
        return []
    return [c.strip() for c in raw.split(" | ")]


def format_pct(pct_raw: float) -> float:
    pct = (1 - pct_raw) * 100
    return max(pct, MIN_PCT_DISPLAY)


def compute_adjusted_ranks(rows, threshold=TIE_THRESHOLD):
    rows_sorted = sorted(rows, key=lambda r: -r["final_suitability_score"])
    result = []
    current_rank = 1
    for idx, row in enumerate(rows_sorted):
        if idx == 0:
            result.append((current_rank, row))
            continue
        prev_score = rows_sorted[idx - 1]["final_suitability_score"]
        this_score = row["final_suitability_score"]
        if abs(prev_score - this_score) > threshold:
            current_rank += 1
        result.append((current_rank, row))
    return result


def build_facts_for_area(row: dict, adjusted_rank: int) -> dict:
    area = row["area_name"]
    score = round(row["final_suitability_score"] * 100, 2)

    items = dict(parse_kv_pipe(row["positive_drivers"]))
    caution_codes = parse_flags(row["caution_flags"])

    positive_facts = []
    for key in FIT_ORDER + [COMPETITION_DRIVER]:
        if key in items:
            pct = round(format_pct(float(items[key])), 2)
            positive_facts.append({"factor": key, "top_percent": pct})

    caution_facts = [
        MAP["caution_flags"][c] for c in caution_codes if MAP["caution_flags"].get(c)
    ]

    return {
        "area_name": area,
        "rank": adjusted_rank,
        "final_score_100": score,
        "positive_facts": positive_facts,
        "caution_facts": caution_facts,
    }


def build_brand_facts(brand: str, group_rows: list[dict]) -> dict:
    ranked = compute_adjusted_ranks(group_rows)
    top_n = ranked[:TOP_N]
    areas_facts = [build_facts_for_area(row, rank) for rank, row in top_n]
    return {"brand_name": brand, "areas": areas_facts}


SYSTEM_PROMPT = """너는 프랜차이즈 출점 추천 결과를 설명하는 어시스턴트다.
아래 규칙을 반드시 지켜라.

1. 오직 사용자가 제공한 JSON 데이터(사실)만 사용해서 문장을 작성해라.
   JSON에 없는 숫자, 예상 매출, 생존 확률, 인과관계, 매장 규모 추천 등은
   절대로 새로 만들어내지 마라.

2. positive_facts의 "factor" 값은 반드시 아래 한글 명칭으로 표현해라 (영어 그대로 쓰지 말 것):
   - brand_environment_fit → "소비환경과의 적합도"
   - brand_specific_advantage → "다른 브랜드 대비 상대적 강점"
   - market_opportunity → "제과 시장 규모" (절대 "시장 기회"라고 쓰지 마라)
   - low_competition_risk → "경쟁 우위"

3. "top_percent"는 "상위 X% 수준"이라는 의미의 숫자다.
   이 숫자에 대해 "높다/낮다/양호하다/우수하다/다소 낮다" 같은
   너의 자체적인 등급 평가나 형용사를 절대로 붙이지 마라.
   그냥 "상위 X% 수준입니다"처럼 숫자만 담백하게 전달해라.

4. positive_facts는 모두 긍정적인 강점을 나열하는 내용이므로,
   문장들을 "또한", "아울러" 같은 순접 접속어로 자연스럽게 이어라.
   "그러나", "하지만" 같은 역접 접속어를 positive_facts 사이에 절대 쓰지 마라.

5. caution_facts는 앞의 positive_facts와 대비되는 내용이므로,
   caution_facts로 넘어갈 때는 "다만" 이라는 접속어로 시작해라.
   caution_facts가 없으면(빈 리스트) "특별히 확인된 주의 요인은 없습니다"라고 써라.
   caution_facts가 여러 상권에서 같은 문장으로 반복되더라도,
   상권마다 어순이나 문장 구조를 조금씩 다르게 써서 기계적 반복을 피해라. (의미는 유지)

6. 각 상권(area)에 대한 문단은 반드시 아래 형식으로 시작해라:
   "[area_name]은 [rank]위이며, 최종 적합도 [final_score_100]점입니다."
   예: "약수역은 1위이며, 최종 적합도 71.02점입니다."
   "최종 적합도"라는 표현을 반드시 포함해서, 이 점수가 무엇에 대한 점수인지 명확히 해라.
   이 형식은 앞의 요약 문장과 별개로, 각 상권 문단마다 반드시 다시 명시해야 한다.

7. 결과는 한국어로, 간결하고 담백한 문단으로 작성해라. 과장된 감탄이나 강조를 쓰지 마라.

8. 브랜드 하나에 대해, 가장 먼저 전체 추천 상권을 한 줄로 요약해라.
   이 요약 문장에는 각 상권의 순위(rank)를 반드시 포함해라.
   예: "OO 브랜드는 A가 1위, B와 C가 2위로 추천됩니다."
   (여러 상권이 같은 순위(rank)를 가지면 동률로 묶어서 표현해라.)
   요약 문장 다음에, 각 상권마다 한 문단씩 설명을 작성해라.

9. 절대로 JSON 형식이나 코드, 마크다운 기호를 출력하지 말고, 순수한 한국어 설명 텍스트만 출력해라.
"""


def call_llm(brand_facts: dict) -> str:
    user_content = json.dumps(brand_facts, ensure_ascii=False, indent=2)

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        temperature=0.3,
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    df = pd.read_parquet(PARQUET_PATH)
    brands = sorted(df["brand_name"].unique())

    results = []
    total = len(brands)

    for idx, brand in enumerate(brands, start=1):
        print(f"[{idx}/{total}] {brand} 처리 중...")
        group = df[df["brand_name"] == brand]
        rows = group.to_dict("records")
        facts = build_brand_facts(brand, rows)

        try:
            explanation = call_llm(facts)
            status = "success"
        except Exception as e:
            explanation = None
            status = f"error: {e}"
            print(f"  !! 에러 발생: {e}")

        results.append({
            "brand_name": brand,
            "facts": facts,
            "explanation": explanation,
            "status": status,
        })

        time.sleep(0.5)  # API 호출 간 짧은 간격

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    success_count = sum(1 for r in results if r["status"] == "success")
    print(f"\n완료: {success_count}/{total} 성공")
    print(f"결과 파일: {OUTPUT_PATH}")