# -*- coding: utf-8 -*-
"""
code_to_text_mapping.json 을 실제 데이터 행에 적용해서
완성된 자연어 문단을 만드는 테스트 스크립트.
"""
import json

with open("code_to_text_mapping.json", "r", encoding="utf-8") as f:
    MAP = json.load(f)

# positive_sentences를 이어붙일 때 쓸 접속어 (첫 문장 다음부터 순환 사용)
POSITIVE_CONNECTORS = ["게다가", "아울러", "더불어"]
# caution_sentences를 이어붙일 때 쓸 접속어
CAUTION_CONNECTORS = ["또한", "그리고"]


def parse_positive_drivers(raw: str):
    items = []
    for chunk in raw.split(" | "):
        key, _, val = chunk.partition("=")
        items.append((key.strip(), float(val.strip())))
    return items


def parse_caution_flags(raw: str):
    return [c.strip() for c in raw.split(" | ")]


def render_positive_drivers(raw: str, use_short=False) -> list[str]:
    sentences = []
    for key, pct_raw in parse_positive_drivers(raw):
        entry = MAP["positive_drivers"].get(key)
        if entry is None:
            continue
        template = entry["template_short"] if use_short else entry["template"]
        pct_exact = (1 - pct_raw) * 100
        sentences.append(template.format(pct=pct_exact))
    return sentences


def render_caution_flags(raw: str) -> list[str]:
    sentences = []
    for code in parse_caution_flags(raw):
        text = MAP["caution_flags"].get(code, None)
        if text:
            sentences.append(text)
    return sentences


def join_with_connectors(sentences: list[str], connectors: list[str]) -> str:
    """첫 문장은 그대로 두고, 이후 문장 앞에 접속어를 순환하며 붙인다."""
    if not sentences:
        return ""
    if len(sentences) == 1:
        return sentences[0] + "."
    parts = [sentences[0]]
    for i, s in enumerate(sentences[1:]):
        connector = connectors[i % len(connectors)]
        parts.append(f"{connector} {s}")
    return ". ".join(parts) + "."


def build_explanation(row: dict) -> str:
    brand = row["brand_name"]
    area = row["area_name"]
    rank = row["final_rank"]
    score = row["final_suitability_score"]

    pos_sentences = render_positive_drivers(row["positive_drivers"])
    caution_sentences = render_caution_flags(row["caution_flags"])

    lines = []
    lines.append(
        f"[{area}]은 '{brand}' 브랜드의 추천 상권 중 {int(rank)}위이며, "
        f"최종 적합도 점수는 {score}입니다."
    )

    if pos_sentences:
        lines.append(
            "이 상권이 추천된 주요 이유는 다음과 같습니다. "
            + join_with_connectors(pos_sentences, POSITIVE_CONNECTORS)
        )

    if caution_sentences:
        lines.append(
            "다만, "
            + join_with_connectors(caution_sentences, CAUTION_CONNECTORS)
            + " 출점 전 참고가 필요합니다."
        )
    else:
        lines.append("현재까지 특별히 확인된 주의 요인은 없습니다.")

    return "\n".join(lines)


if __name__ == "__main__":
    sample_row = {
        "brand_name": "곤트란쉐리에(Gontran Cherrier)",
        "area_name": "법제교육센터(버들어린이공원)",
        "final_rank": 1,
        "final_suitability_score": 0.7385536713622092,
        "positive_drivers": "brand_environment_fit=0.9653579676674365 | brand_specific_advantage=0.9515011547344111 | market_opportunity=0.8545034642032333",
        "caution_flags": "profile_stability_moderate | competition_risk_elevated_but_below_exclusion",
    }

    print(build_explanation(sample_row))
    print("\n" + "=" * 60 + "\n")

    sample_row2 = {
        "brand_name": "더베이크",
        "area_name": "약수역",
        "final_rank": 1,
        "final_suitability_score": 0.710234315534245,
        "positive_drivers": "brand_environment_fit=0.9861431870669746 | market_opportunity=0.9699769053117783 | brand_specific_advantage=0.9653579676674365",
        "caution_flags": "competition_risk_moderate",
    }
    print(build_explanation(sample_row2))