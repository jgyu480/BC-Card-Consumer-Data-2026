from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

from components.tab3_area_map import build_mini_map


def build_brand_identity_header(brand):
    """브랜드명만 - 카드 없는 텍스트 헤더"""
    if brand is None:
        return html.Div("브랜드를 선택하세요.", className="text-muted")

    return html.Div(
        html.H4(
            brand["brand_name"],
            className="mb-3 portfolio-compatible-brand-title"
        )
    )


def _kpi_tile(label, value):
    """
    핵심 의사결정 정보를 보여주는 타일.
    별도의 border 없이 배경/여백으로 구분.
    """
    return dbc.Col(
        html.Div(
            [
                html.Div(
                    label,
                    className="overview-kpi-label"
                ),
                html.Div(
                    value,
                    className="overview-kpi-value"
                ),
            ],
            className="overview-kpi-tile"
        ),
        width=6,
    )


def _suitability_tone(score):
    """80점 이상 매우 적합 / 65~80점 적합 / 65점 미만 검토 필요"""
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


def _suitability_gauge(score):
    tone = _suitability_tone(score)
    color = _TONE_COLOR[tone]
    label = _TONE_LABEL[tone]

    # 게이지 자체만 Plotly로 렌더링
    fig = go.Figure(
        go.Indicator(
            mode="gauge",
            value=score,
            gauge={
                "axis": {
                    "range": [0, 100],
                    "tickfont": {
                        "size": 10,
                        "color": "#8C8370",
                        "family": "Inter, sans-serif",
                    },
                    "tickwidth": 0,
                    "tickcolor": "rgba(0,0,0,0)",
                },
                "bar": {
                    "color": color,
                    "thickness": 0.18,
                },
                "bgcolor": "#EFE6D6",
                "borderwidth": 0,
            },
            domain={"x": [0.08, 0.92], "y": [0.02, 0.96]},
        )
    )

    fig.update_layout(
        height=170,
        margin=dict(l=10, r=10, t=8, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        autosize=True,
    )

    return html.Div(
        [
            # 적합도 상태
            html.Div(
                label,
                style={
                    "position": "absolute",
                    "top": "84px",
                    "left": "50%",
                    "transform": "translateX(-50%)",
                    "fontFamily": "Inter, sans-serif",
                    "fontSize": "13px",
                    "fontWeight": "600",
                    "color": color,
                    "whiteSpace": "nowrap",
                    "zIndex": "2",
                },
            ),

            # Plotly 게이지
            dcc.Graph(
                figure=fig,
                config={
                    "displayModeBar": False,
                    "responsive": True,
                },
                style={
                    "width": "100%",
                    "height": "170px",
                    "minWidth": "0",
                },
            ),

            # 점수
            html.Div(
                [
                    html.Span(
                        f"{score:.1f}",
                        style={
                            "fontFamily": "Inter, sans-serif",
                            "fontSize": "30px",
                            "fontWeight": "600",
                            "letterSpacing": "-1px",
                            "color": color,
                            "lineHeight": "1",
                        },
                    ),
                    html.Span(
                        "점",
                        style={
                            "fontFamily": "Inter, sans-serif",
                            "fontSize": "16px",
                            "fontWeight": "500",
                            "marginLeft": "2px",
                            "color": color,
                        },
                    ),
                ],
                style={
                    "position": "absolute",
                    "left": "50%",
                    "top": "108px",
                    "transform": "translateX(-50%)",
                    "display": "flex",
                    "alignItems": "baseline",
                    "whiteSpace": "nowrap",
                    "zIndex": "2",
                },
            ),
        ],
        style={
            "position": "relative",
            "width": "100%",
            "height": "170px",
            "minWidth": "0",
            "overflow": "hidden",
        },
    )


def _avg_suitability(recommendations):
    if not recommendations:
        return None

    return sum(
        r["suitability_score"]
        for r in recommendations
    ) / len(recommendations)


def build_dna_summary(brand, desired_store_count=None):
    """
    Brand Overview 탭.

    구조:
    좌측  : 브랜드 DNA
    우측  : 핵심 의사결정 정보 → 추천 근거 → 적합도/지도

    Portfolio 페이지와 동일하게
    '정보를 카드로 장식하기보다 정보 위계를 통해 구분'하는 방향.
    """

    if brand is None:
        return html.P("브랜드를 선택하세요.")

    dna = brand["dna_summary"]
    decision = brand.get("decision_summary", {})
    recommendations = brand.get("recommendations", [])

    top_area = recommendations[0] if recommendations else None

    # =====================================================
    # LEFT : BRAND DNA
    # =====================================================

    type_tag = None

    if brand.get("brand_type"):
        type_tag = html.Span(
            brand["brand_type"],
            className="overview-brand-type"
        )

    left_children = [
        html.H4(
            brand["brand_name"],
            className="overview-brand-name"
        )
    ]

    if type_tag:
        left_children.append(type_tag)

    left_children.append(
        html.P(
            dna["headline"],
            className="overview-brand-headline"
        )
    )

    # 강점
    if dna.get("strengths"):
        left_children.append(
            html.Div(
                [
                    html.Span(
                        s,
                        className="overview-tag overview-tag-good"
                    )
                    for s in dna["strengths"]
                ],
                className="overview-tag-group"
            )
        )

    # 주의점
    if dna.get("cautions"):
        left_children.append(
            html.Div(
                [
                    html.Span(
                        c,
                        className="overview-tag overview-tag-risk"
                    )
                    for c in dna["cautions"]
                ],
                className="overview-tag-group overview-caution-group"
            )
        )

    left_col = dbc.Col(
        html.Div(
            left_children,
            className=(
                "overview-brand-panel "
                "d-flex flex-column "
                "align-items-center "
                "justify-content-center "
                "text-center h-100"
            ),
        ),
        width=4,
    )

    # =====================================================
    # RIGHT : DECISION SUMMARY
    # =====================================================

    matching_portfolios = [
        p
        for p in brand.get("portfolios", [])
        if p["desired_store_count"] == desired_store_count
    ]

    top_portfolio = next(
        (
            p
            for p in matching_portfolios
            if p["portfolio_rank"] == 1
        ),
        None,
    )

    portfolio_label = (
        f"{desired_store_count}개 조합 1순위"
        if desired_store_count
        else "조합 1순위"
    )

    portfolio_value = (
        " · ".join(top_portfolio["area_names"])
        if top_portfolio
        else "-"
    )

    right_children = []

    # -----------------------------------------------------
    # 1. 핵심 의사결정 정보
    # -----------------------------------------------------

    right_children.append(
        dbc.Row(
            [
                _kpi_tile(
                    "최우선 단일 후보",
                    decision.get(
                        "best_single_area",
                        "-"
                    ),
                ),
                _kpi_tile(
                    portfolio_label,
                    portfolio_value,
                ),
            ],
            className="g-3 mb-3",
        )
    )

    # -----------------------------------------------------
    # 2. 한 줄 의사결정 요약
    # -----------------------------------------------------

    if decision.get("headline"):
        right_children.append(
            html.Div(
                decision["headline"],
                className="overview-decision-headline",
            )
        )

    # -----------------------------------------------------
    # 3. 1순위 추천 근거
    # -----------------------------------------------------

    if top_area:

        evidence_children = [
            html.Div(
                [
                    html.Span(
                        "1순위",
                        className="overview-evidence-rank"
                    ),
                    html.Span(
                        f" · {top_area['area_name']} 추천 근거",
                        className="overview-evidence-title"
                    ),
                ],
                className="overview-evidence-header",
            )
        ]

        if top_area.get("positive_factors"):
            evidence_children.append(
                html.Div(
                    [
                        html.Div(
                            [
                                html.Span(
                                    "✓",
                                    className="overview-check"
                                ),
                                html.Span(
                                    factor,
                                    className="overview-evidence-text"
                                ),
                            ],
                            className="overview-evidence-item",
                        )
                        for factor in top_area[
                            "positive_factors"
                        ]
                    ],
                    className="overview-evidence-list",
                )
            )

        consumer_profile = top_area.get(
            "consumer_profile",
            {}
        )

        if consumer_profile:
            evidence_children.append(
                html.Div(
                    [
                        html.Span(
                            "주요 고객     ",
                            className="overview-meta-label"
                        ),
                        html.Span(
                            consumer_profile.get(
                                "primary_segment",
                                "-"
                            ),
                            className="overview-meta-value"
                        ),
                        html.Span(
                            " · ",
                            className="overview-meta-separator"
                        ),
                        html.Span(
                            consumer_profile.get(
                                "demand_context",
                                "-"
                            ),
                            className="overview-meta-value"
                        ),
                    ],
                    className="overview-evidence-meta",
                )
            )

    else:
        evidence_children = [
            html.P(
                "추천 데이터가 없습니다.",
                className="text-muted small mb-0"
            )
        ]

    right_children.append(
        html.Div(
            evidence_children,
            className="overview-evidence-panel",
        )
    )

    # =====================================================
    # 4. GAUGE + MAP
    # =====================================================

    if top_area:

        avg_score = _avg_suitability(
            recommendations
        )

        diff_caption = None

        if avg_score is not None:
            diff = (
                top_area["suitability_score"]
                - avg_score
            )

            sign = "+" if diff >= 0 else ""

            diff_caption = html.Div(
                f"추천 후보 평균 대비 {sign}{diff:.1f}점",
                className="overview-score-caption",
            )

        gauge_card_body = [
            html.Div(
                "단일 후보 적합도",
                className="overview-visual-title",
            ),
            _suitability_gauge(
                top_area["suitability_score"]
            ),
        ]

        if diff_caption:
            gauge_card_body.append(
                diff_caption
            )

        right_children.append(
            dbc.Row(
                [
                    dbc.Col(
                        html.Div(
                            gauge_card_body,
                            className="overview-visual-panel h-100",
                        ),
                        width=6,
                    ),
                    dbc.Col(
                        html.Div(
                            [
                                html.Div(
                                    "지도에서 보기",
                                    className="overview-visual-title",
                                ),
                                build_mini_map(
                                    top_area
                                ),
                            ],
                            className="overview-visual-panel h-100",
                        ),
                        width=6,
                    ),
                ],
                className="g-3 mt-0",
            )
        )

    right_col = dbc.Col(
        right_children,
        width=8,
    )

    return dbc.Row(
        [
            left_col,
            right_col,
        ],
        className="g-3 overview-layout",
    )