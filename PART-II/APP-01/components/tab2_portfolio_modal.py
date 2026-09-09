from dash import html
import dash_leaflet as dl

from components.tab1_overview import _suitability_tone, _TONE_COLOR


def build_combo_map(area_ids, recommendations):
    """조합에 포함된 상권들을 한 지도에 함께 표시"""

    matched = [
        r for r in recommendations
        if r["area_id"] in area_ids
    ]

    if not matched:
        return html.P(
            "표시할 상권이 없습니다.",
            className="text-muted small"
        )

    markers = [
        dl.CircleMarker(
            center=[
                r["centroid_latitude"],
                r["centroid_longitude"]
            ],
            radius=10,
            color="#0F6E56",
            fillColor="#0F6E56",
            fillOpacity=0.8,
            weight=2,
            children=[
                dl.Tooltip(r["area_name"])
            ],
        )
        for r in matched
    ]

    avg_lat = sum(
        r["centroid_latitude"] for r in matched
    ) / len(matched)

    avg_lng = sum(
        r["centroid_longitude"] for r in matched
    ) / len(matched)

    return dl.Map(
        center=[avg_lat, avg_lng],
        zoom=12,
        style={
            "height": "260px",
            "width": "100%",
            "borderRadius": "8px",
            "overflow": "hidden",
        },
        children=[
            dl.TileLayer(),
            *markers,
        ],
    )


def _build_score_header(portfolio):
    """
    모달 최상단 핵심 의사결정 정보.
    Overview / Portfolio와 동일한 타이포그래피 사용.
    """

    tone = _suitability_tone(
        portfolio["portfolio_score"]
    )

    score_color = _TONE_COLOR[tone]

    return html.Div(
        [
            html.Div(
                [
                    html.Span(
                        f"{portfolio['portfolio_rank']}순위",
                        className="portfolio-detail-rank"
                    ),
                    html.Span(
                        "종합적합도",
                        className="portfolio-detail-score-label"
                    ),
                ],
                className="portfolio-detail-score-meta",
            ),

            html.Div(
                [
                    html.Span(
                        f"{portfolio['portfolio_score']:.1f}",
                        className="portfolio-detail-score",
                        style={"color": score_color},
                    ),
                    html.Span(
                        "점",
                        className="portfolio-detail-score-unit",
                    ),
                ],
                className="portfolio-detail-score-wrap",
            ),
        ],
        className="portfolio-detail-header",
    )


def _build_area_summary(area_ids, recommendations):
    """
    조합을 구성하는 상권별 핵심 정보를 간결하게 보여준다.
    """

    matched = {
        r["area_id"]: r
        for r in recommendations
        if r["area_id"] in area_ids
    }

    rows = []

    for index, area_id in enumerate(area_ids, start=1):

        rec = matched.get(area_id)

        if not rec:
            continue

        share = rec.get(
            "facts", {}
        ).get(
            "bakery_franchise_share"
        )

        if share is not None:
            share_text = (
                f"프랜차이즈 밀집도 {share * 100:.0f}%"
            )
        else:
            share_text = None

        secondary_info = [
            f"적합도 {rec['suitability_score']:.1f}점"
        ]

        if share_text:
            secondary_info.append(share_text)

        rows.append(
            html.Div(
                [
                    html.Div(
                        str(index),
                        className="portfolio-detail-area-index"
                    ),

                    html.Div(
                        [
                            html.Div(
                                rec["area_name"],
                                className="portfolio-detail-area-name"
                            ),

                            html.Div(
                                " · ".join(secondary_info),
                                className="portfolio-detail-area-meta"
                            ),
                        ],
                        className="portfolio-detail-area-info",
                    ),
                ],
                className="portfolio-detail-area-row",
            )
        )

    return html.Div(rows)


def _build_reason_section(portfolio):
    """
    조합 선정 근거.
    데이터가 있을 때만 표시.
    """

    rationale = portfolio.get(
        "rationale_facts",
        []
    )

    if not rationale:
        return None

    return html.Div(
        [
            html.Div(
                "선정 근거",
                className="portfolio-detail-section-title"
            ),

            html.Div(
                [
                    html.Div(
                        [
                            html.Span(
                                "✓",
                                className="portfolio-detail-check"
                            ),
                            html.Span(
                                fact,
                                className="portfolio-detail-reason-text"
                            ),
                        ],
                        className="portfolio-detail-reason-row"
                    )
                    for fact in rationale
                ],
                className="portfolio-detail-reason-list"
            ),
        ],
        className="portfolio-detail-section"
    )


def _build_risk_section(portfolio):
    """
    위험 요인.
    다른 정보보다 시각적 우선순위를 낮추되,
    의사결정에 필요한 경고는 명확하게 표시.
    """

    risks = portfolio.get(
        "risk_factors",
        []
    )

    if not risks:
        return None

    return html.Div(
        [
            html.Div(
                "위험 요인",
                className="portfolio-detail-section-title portfolio-detail-risk-title"
            ),

            html.Div(
                [
                    html.Div(
                        [
                            html.Span(
                                "주의",
                                className="portfolio-detail-risk-label"
                            ),
                            html.Span(
                                risk,
                                className="portfolio-detail-risk-text"
                            ),
                        ],
                        className="portfolio-detail-risk-row"
                    )
                    for risk in risks
                ],
            ),
        ],
        className="portfolio-detail-section portfolio-detail-risk-section"
    )


def _build_competitor_placeholder():
    """
    향후 경쟁사 입점현황 데이터를 추가할 영역.

    실제 데이터가 연결되기 전에는 화면에 노출하지 않는다.
    """

    return None


def build_portfolio_detail_content(brand, portfolio):
    """
    조합 상세 모달 콘텐츠.

    정보 우선순위:
    1. 순위 / 종합 적합도
    2. 추천 상권 위치
    3. 상권별 구성
    4. 선정 근거
    5. 위험 요인
    6. 향후 경쟁사 입점현황 확장
    """

    recommendations = brand.get(
        "recommendations",
        []
    )

    area_ids = portfolio.get(
        "area_ids",
        []
    )

    # -----------------------------------------------------
    # 1. Header
    # -----------------------------------------------------

    header = _build_score_header(portfolio)

    # -----------------------------------------------------
    # 2. Map
    # -----------------------------------------------------

    combo_map = build_combo_map(
        area_ids,
        recommendations
    )

    map_section = html.Div(
        [
            html.Div(
                "추천 상권 위치",
                className="portfolio-detail-section-title"
            ),

            html.Div(
                combo_map,
                className="portfolio-detail-map"
            ),
        ],
        className="portfolio-detail-section"
    )

    # -----------------------------------------------------
    # 3. Area summary
    # -----------------------------------------------------

    area_summary = html.Div(
        [
            html.Div(
                "상권별 요약",
                className="portfolio-detail-section-title"
            ),

            _build_area_summary(
                area_ids,
                recommendations
            ),
        ],
        className="portfolio-detail-section"
    )

    # -----------------------------------------------------
    # 4. Selection rationale
    # -----------------------------------------------------

    reason_section = _build_reason_section(
        portfolio
    )

    # -----------------------------------------------------
    # 5. Risk
    # -----------------------------------------------------

    risk_section = _build_risk_section(
        portfolio
    )

    # -----------------------------------------------------
    # 6. Future competitor information
    # -----------------------------------------------------

    # 향후 경쟁사 입점현황 데이터가 연결되면
    # 이 위치에 경쟁사 분포 / 입점 밀도 / 주요 경쟁 브랜드
    # 등의 정보를 추가할 예정.
    competitor_section = _build_competitor_placeholder()

    # -----------------------------------------------------
    # Assemble
    # -----------------------------------------------------

    children = [
        header,
        map_section,
        area_summary,
    ]

    if reason_section:
        children.append(reason_section)

    if risk_section:
        children.append(risk_section)

    if competitor_section:
        children.append(competitor_section)

    return html.Div(
        children,
        className="portfolio-detail-content"
    )