"""
색상 톤 / 숫자 포맷 공용 헬퍼.

다른 components 파일(tab1_overview, tab3_area_map, tab3_area_table,
tab2_portfolio_modal 등)이 전부 이 파일에서만 가져다 쓴다.

이 파일이 다른 components 파일을 import하면 안 된다 — 그러면 순환 import가
생긴다.
"""


def _suitability_tone(score):
    """80점 이상 매우 적합 / 65~80점 적합 / 65점 미만 검토 필요.
    (레거시 — 브랜드마다 점수 분포가 달라 대부분 '적합'에만 몰리는 문제가 있어서
    개별 상권 표시에는 _recommendation_tone을 대신 쓴다. recommendation_label이
    없는 예외 상황의 폴백으로만 남겨둠.)"""
    if score >= 80:
        return "success"
    elif score >= 65:
        return "warning"
    return "danger"


_TONE_COLOR = {
    "success": "#5B7332",
    "warning": "#C9992B",
    "danger": "#A13D2B",
}

_TONE_LABEL = {
    "success": "매우 적합",
    "warning": "적합",
    "danger": "검토 필요",
}


_LABEL_TONE = {
    "최우선 검토": "success",
    "우선 검토": "warning",
    "비교 후보": "danger",
}


def _recommendation_tone(recommendation_label):
    return _LABEL_TONE.get(recommendation_label, "warning")


def _portfolio_tone(portfolio):
    """포트폴리오는 recommendation_label이 없어서 is_top_recommendation으로 톤을 정함.
    최우선 추천(1위 또는 동점 2위)이면 success, 나머지(대안)는 warning.
    danger를 안 쓰는 이유: 2~3위 대안이 '위험'한 게 아니라 그냥 차순위일 뿐이라서."""
    return "success" if portfolio.get("is_top_recommendation") else "warning"


def format_distance(meters):
    """거리를 사람이 읽기 좋은 형태로 축약. 1km 이상이면 km(소수 1자리),
    미만이면 10m 단위로 반올림해서 표시 (소수점 다 붙는 버그 방지)."""
    if meters is None:
        return "-"
    if meters >= 1000:
        return f"약 {meters / 1000:.1f}km"
    rounded = round(meters / 10) * 10
    return f"약 {rounded:,.0f}m"