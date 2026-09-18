# -*- coding: utf-8 -*-
"""
실행 전 필요한 것
----------------
- pip install openai python-dotenv --break-system-packages
- 환경변수 OPENAI_API_KEY 설정 (또는 .env 파일)
- 비용 감안: 24개 브랜드 x 최대 17개 상권 = 최대 약 395건 호출.
  DRY_RUN=True로 먼저 facts만 만들어보고 확인 후 DRY_RUN=False로 재실행 권장.
"""
import json
import os
import time
from pathlib import Path

import pandas as pd

# =========================================================
# 경로 (수정된 부분)
# =========================================================

SCRIPT_DIR = Path(__file__).resolve().parent                # .../PART-V/LLM-01/scripts
ROOT = SCRIPT_DIR.parents[2]

PARQUET_PATH = (
    ROOT / "PART-III" / "MODEL-01" / "outputs" / "final_model_v3_1"
    / "model01_final_recommendations_v3_1.parquet"
)
MAPPING_PATH = SCRIPT_DIR / "code_to_text_mapping.json"
OUTPUT_PATH = SCRIPT_DIR / "llm01_explanations_api_4to20.json"

TIE_THRESHOLD = 0.003
MAX_RANK = 20
START_RANK = 4  # B가 이미 1~3위는 처리함
MIN_PCT_DISPLAY = 0.01

FIT_ORDER = ["brand_environment_fit", "brand_specific_advantage", "market_opportunity"]
COMPETITION_DRIVER = "low_competition_risk"

MODEL_NAME = "gpt-4o-mini"
TEMPERATURE = 0.3

# True면 API 호출 없이 facts만 만들어서 저장 (비용 0원, 먼저 검증용)
DRY_RUN = False

with open(MAPPING_PATH, "r", encoding="utf-8") as f:
    MAP = json.load(f)


# =========================================================
# 아래는 B의 원본 로직 그대로 (수정 없음)
# =========================================================

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


# =========================================================
# 수정된 부분: 상권 단위 시스템 프롬프트 (B의 규칙 1~7,9는 그대로, 8번만 제거)
# =========================================================

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

6. 이 상권(area)에 대한 문단은 반드시 아래 형식으로 시작해라:
   "[area_name]은 [rank]위이며, 최종 적합도 [final_score_100]점입니다."
   예: "약수역은 1위이며, 최종 적합도 71.02점입니다."
   "최종 적합도"라는 표현을 반드시 포함해서, 이 점수가 무엇에 대한 점수인지 명확히 해라.

7. 결과는 한국어로, 간결하고 담백한 문단으로 작성해라. 과장된 감탄이나 강조를 쓰지 마라.

8. 절대로 JSON 형식이나 코드, 마크다운 기호를 출력하지 말고, 순수한 한국어 설명 텍스트만 출력해라.
   상권 하나에 대한 문단 하나만 출력해라 (다른 상권 언급 금지).
"""


def call_llm(client, area_facts: dict) -> str:
    user_content = json.dumps(area_facts, ensure_ascii=False, indent=2)
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        temperature=TEMPERATURE,
    )
    return response.choices[0].message.content.strip()


# =========================================================
# 전체 실행
# =========================================================

def collect_targets():
    df = pd.read_parquet(PARQUET_PATH)
    targets = []  # [(brand_name, area_id, facts), ...]
    for brand, group in df.groupby("brand_name"):
        rows = group.to_dict("records")
        ranked = compute_adjusted_ranks(rows)
        for adjusted_rank, row in ranked[:MAX_RANK]:
            if int(row["final_rank"]) < START_RANK:
                continue
            facts = build_facts_for_area(row, adjusted_rank)
            targets.append((brand, row["area_id"], facts))
    return targets


def main():
    targets = collect_targets()
    print(f"확장 대상: {len(targets)}건 (브랜드 x 4~{MAX_RANK}위 상권)")

    if DRY_RUN:
        print("DRY_RUN=True -> API 호출 없이 facts만 저장합니다.")
        preview = [
            {"brand_name": b, "area_id": aid, "facts": facts}
            for b, aid, facts in targets
        ]
        preview_path = OUTPUT_PATH.with_suffix(".facts_preview.json")
        with open(preview_path, "w", encoding="utf-8") as f:
            json.dump(preview, f, ensure_ascii=False, indent=2)
        print(f"완료 -> {preview_path}")
        return preview

    from openai import OpenAI
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    results = []
    for idx, (brand, area_id, facts) in enumerate(targets, start=1):
        print(f"[{idx}/{len(targets)}] {brand} / {facts['area_name']} 처리 중...")
        try:
            explanation = call_llm(client, facts)
            status = "success"
        except Exception as e:
            explanation = None
            status = f"error: {e}"
            print(f"  !! 에러: {e}")

        results.append({
            "brand_name": brand,
            "area_id": area_id,
            "facts": facts,
            "explanation": explanation,
            "status": status,
        })
        time.sleep(0.3)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    success_count = sum(1 for r in results if r["status"] == "success")
    print(f"\n완료: {success_count}/{len(targets)} 성공 -> {OUTPUT_PATH}")
    return results


if __name__ == "__main__":
    main()