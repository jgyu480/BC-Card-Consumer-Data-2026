# -*- coding: utf-8 -*-
"""
model01_final_recommendations_v3_1.parquet 을 읽어서,
브랜드별 상위 3개 상권(동점 처리 포함) 자연어 설명 문단을 생성한다.
"""
import json
from collections import defaultdict

import pandas as pd

PARQUET_PATH = r"C:\Users\lucy0\Documents\YONSEI\YBIGTA\공모전\BC-Card-Consumer-Data-2026\PART-III\MODEL-01\outputs\final_model_v3_1\model01_final_recommendations_v3_1.parquet"
MAPPING_PATH = "code_to_text_mapping.json"

TIE_THRESHOLD = 0.003
TOP_N = 3
MIN_PCT_DISPLAY = 0.01  # 백분위가 이보다 작으면 이 값으로 올려서 표시 ("상위 0.00%" 방지)

FIT_ORDER = ["brand_environment_fit", "brand_specific_advantage", "market_opportunity"]
COMPETITION_DRIVER = "low_competition_risk"
COMPETITION_CAUTION_CODES = {"competition_risk_moderate", "competition_risk_elevated_but_below_exclusion"}

POSITIVE_CONNECTORS = ["또한", "아울러"]
CAUTION_CONNECTORS = ["또한", "그리고"]

with open(MAPPING_PATH, "r", encoding="utf-8") as f:
    MAP = json.load(f)


def has_final_consonant(syllable: str) -> bool:
    """한글 한 글자에 받침(종성)이 있는지 판별. 한글이 아니면 False."""
    code = ord(syllable)
    if not (0xAC00 <= code <= 0xD7A3):
        return False
    return (code - 0xAC00) % 28 != 0


def josa_ika(word: str) -> str:
    """단어 끝 글자의 받침 여부에 따라 '이' 또는 '가'를 붙인다."""
    if not word:
        return "가"
    last_char = word[-1]
    return "이" if has_final_consonant(last_char) else "가"


def join_korean_list(items: list[str]) -> str:
    """['A','B','C'] -> 'A, B와 C' / ['A','B'] -> 'A와 B' / ['A'] -> 'A'"""
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    last = items[-1]
    connector = "와" if not has_final_consonant(last[-1]) is False else "과"
    # 마지막 단어 앞 글자(연결되는 앞 단어)의 받침 여부로 와/과 결정해야 하므로 아래에서 재계산
    head = items[:-1]
    prev_word = head[-1]
    connector = "와" if has_final_consonant(prev_word[-1]) else "과"
    # 국립국어원 규정: 받침 있으면 '과', 받침 없으면 '와'가 자연스러움 -> 위 조건 반대로 수정
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


def join_sentences(sentences: list[str], connectors: list[str]) -> str:
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
    """percentile을 뒤집어 '상위 X%'로 표시할 값을 계산. 너무 작으면 하한선 적용."""
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


def compute_adjusted_ranks(rows: list[dict], threshold: float = TIE_THRESHOLD):
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


def build_summary_line(brand: str, ranked_top: list[tuple]) -> str:
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


def build_brand_explanation(brand: str, group_rows: list[dict]) -> str:
    ranked = compute_adjusted_ranks(group_rows)
    top_n = ranked[:TOP_N]

    summary = build_summary_line(brand, top_n)
    area_paragraphs = [build_area_paragraph(row, rank) for rank, row in top_n]

    return summary + "\n\n" + "\n\n".join(area_paragraphs)


if __name__ == "__main__":
    df = pd.read_parquet(PARQUET_PATH)

    for brand, group in df.groupby("brand_name"):
        rows = group.to_dict("records")
        explanation = build_brand_explanation(brand, rows)
        print(explanation)
        print("\n" + "=" * 70 + "\n")