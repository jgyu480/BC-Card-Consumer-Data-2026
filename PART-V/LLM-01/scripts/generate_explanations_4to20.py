import json
from pathlib import Path
from collections import defaultdict

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
OUTPUT_PATH = SCRIPT_DIR / "llm01_explanations_rule_based_4to20.json"

TIE_THRESHOLD = 0.003
TOP_N = 20  # 동점 순위 계산은 20위까지 기준으로 해야 정확함 (아래 START_RANK로 출력만 자름)
START_RANK = 4  # B가 이미 1~3위(원본 final_rank 기준)는 처리함 -> 출력에서 제외
MIN_PCT_DISPLAY = 0.01

FIT_ORDER = ["brand_environment_fit", "brand_specific_advantage", "market_opportunity"]
COMPETITION_DRIVER = "low_competition_risk"
COMPETITION_CAUTION_CODES = {"competition_risk_moderate", "competition_risk_elevated_but_below_exclusion"}

POSITIVE_CONNECTORS = ["또한", "아울러"]
CAUTION_CONNECTORS = ["또한", "그리고"]

with open(MAPPING_PATH, "r", encoding="utf-8") as f:
    MAP = json.load(f)


# =========================================================
# 아래부터는 B의 원본 로직 그대로 (수정 없음)
# =========================================================

def has_final_consonant(syllable: str) -> bool:
    code = ord(syllable)
    if not (0xAC00 <= code <= 0xD7A3):
        return False
    return (code - 0xAC00) % 28 != 0


def josa_ika(word: str) -> str:
    if not word:
        return "가"
    last_char = word[-1]
    return "이" if has_final_consonant(last_char) else "가"


def join_korean_list(items: list) -> str:
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    last = items[-1]
    connector = "와" if not has_final_consonant(last[-1]) is False else "과"
    head = items[:-1]
    prev_word = head[-1]
    connector = "와" if has_final_consonant(prev_word[-1]) else "과"
    connector = "과" if has_final_consonant(prev_word[-1]) else "와"
    return ", ".join(head) + f"{connector} {last}"


def parse_kv_pipe(raw: str):
    if not raw:
        return []
    return [tuple(p.strip() for p in chunk.partition("=")[::2]) for chunk in raw.split(" | ")]


def parse_flags(raw: str):
    if not raw:
        return []
    return [c.strip() for c in raw.split(" | ")]


def join_sentences(sentences: list, connectors: list) -> str:
    if not sentences:
        return ""
    if len(sentences) == 1:
        return sentences[0] + "."
    parts = [sentences[0]]
    for i, s in enumerate(sentences[1:]):
        conn = connectors[i % len(connectors)]
        parts.append(f"{conn} {s}")
    return ". ".join(parts) + "."


def format_pct(pct_raw: float) -> float:
    pct = (1 - pct_raw) * 100
    return max(pct, MIN_PCT_DISPLAY)


def build_fit_paragraph(positive_raw: str, area: str) -> str:
    items = dict(parse_kv_pipe(positive_raw))
    sentences = []
    for key in FIT_ORDER:
        if key in items:
            pct = format_pct(float(items[key]))
            template = MAP["positive_drivers"][key]["template"]
            sentences.append(template.format(pct=pct, area=area))
    return join_sentences(sentences, POSITIVE_CONNECTORS)


def build_competition_paragraph(positive_raw: str, caution_raw: str, area: str) -> str:
    items = dict(parse_kv_pipe(positive_raw))
    caution_codes = parse_flags(caution_raw)
    comp_caution_codes = [c for c in caution_codes if c in COMPETITION_CAUTION_CODES]

    positive_sentence = None
    if COMPETITION_DRIVER in items:
        pct = format_pct(float(items[COMPETITION_DRIVER]))
        template = MAP["positive_drivers"][COMPETITION_DRIVER]["template"]
        positive_sentence = template.format(pct=pct, area=area)

    comp_caution_texts = [
        MAP["caution_flags"][c] for c in comp_caution_codes if MAP["caution_flags"].get(c)
    ]

    if positive_sentence and comp_caution_texts:
        return positive_sentence + " 다만, " + join_sentences(comp_caution_texts, CAUTION_CONNECTORS)
    elif positive_sentence:
        return positive_sentence + "."
    elif comp_caution_texts:
        return join_sentences(comp_caution_texts, CAUTION_CONNECTORS)
    else:
        return ""


def build_other_caution_paragraph(caution_raw: str) -> str:
    codes = parse_flags(caution_raw)
    other_codes = [c for c in codes if c not in COMPETITION_CAUTION_CODES]
    texts = [MAP["caution_flags"][c] for c in other_codes if MAP["caution_flags"].get(c)]
    if not texts:
        return ""
    return "다만, " + join_sentences(texts, CAUTION_CONNECTORS) + " 출점 전 참고가 필요합니다."


def build_area_paragraph(row: dict, adjusted_rank: int) -> str:
    area = row["area_name"]
    score = row["final_suitability_score"] * 100

    lines = [f"[{area}] {adjusted_rank}위 · 최종 적합도 {score:.2f}점"]

    fit_para = build_fit_paragraph(row["positive_drivers"], area)
    if fit_para:
        lines.append(fit_para)

    comp_para = build_competition_paragraph(row["positive_drivers"], row["caution_flags"], area)
    if comp_para:
        lines.append(comp_para)

    other_caution = build_other_caution_paragraph(row["caution_flags"])
    if other_caution:
        lines.append(other_caution)

    return "\n".join(lines)


def compute_adjusted_ranks(rows: list, threshold: float = TIE_THRESHOLD):
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


def build_summary_line(brand: str, ranked_top: list) -> str:
    rank_to_areas = defaultdict(list)
    for rank, row in ranked_top:
        rank_to_areas[rank].append(row["area_name"])

    parts = []
    for rank in sorted(rank_to_areas):
        areas = rank_to_areas[rank]
        areas_str = join_korean_list(areas)
        josa = josa_ika(areas[-1])
        parts.append(f"{areas_str}{josa} {rank}위")

    return f"'{brand}' 브랜드는 " + ", ".join(parts) + "로 추천됩니다."


# =========================================================
# 수정된 부분: 상권별로 따로 캡처 + 파일 저장
# =========================================================

def build_brand_result(brand: str, group_rows: list) -> dict:
    ranked = compute_adjusted_ranks(group_rows)
    top_n = ranked[:TOP_N]

    summary = build_summary_line(brand, top_n)

    areas_out = []
    for rank, row in top_n:
        if int(row["final_rank"]) < START_RANK:
            continue  # B가 이미 처리한 1~3위(원본 순위 기준)는 건너뜀
        areas_out.append({
            "area_id": row["area_id"],
            "area_name": row["area_name"],
            "adjusted_rank": rank,          # 동점 보정된 순위 (B 원본 로직, 1~20 전체 기준으로 계산됨)
            "final_rank": int(row["final_rank"]),  # 원본 raw 순위 (recommendations[].rank와 매칭용)
            "final_score_100": round(row["final_suitability_score"] * 100, 2),
            "explanation": build_area_paragraph(row, rank),  # 상권 하나짜리 독립 문단
        })

    return {
        "brand_name": brand,
        "summary": summary,          # 참고용: 1~20위 전체를 요약한 문장 (B의 top3 요약과는 별개)
        "areas": areas_out,          # 실제로 쓸 데이터: 4~20위만 들어있음
    }


if __name__ == "__main__":
    df = pd.read_parquet(PARQUET_PATH)

    results = []
    for brand, group in df.groupby("brand_name"):
        rows = group.to_dict("records")
        results.append(build_brand_result(brand, rows))
        print(f"[{brand}] {len(results[-1]['areas'])}개 상권 처리 완료")

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n완료 -> {OUTPUT_PATH}")