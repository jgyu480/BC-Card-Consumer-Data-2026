from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

from components.tab1_overview import (
    _suitability_tone,
    _TONE_COLOR,
)


# =========================================================
# Score chart
# =========================================================

def _score_chart(score):
    """
    상권 적합도 구성요소를 한눈에 보여주는 가로 막대 그래프.
    Portfolio / Overview와 동일한 폰트 및 색상 체계를 사용한다.
    """

    labels = [
        "DNA 적합도",
        "시장 규모",
        "경쟁 매력도",
        "근접 위험도",
    ]

    values = [
        score.get("dna_match_score", 0),
        score.get("market_score", 0),
        score.get("competition_attractiveness_score", 0),
        score.get("proximity_risk_score", 0),
    ]

    colors = [
        "#5B7332",
        "#5B7332",
        "#5B7332",
        "#A13D2B",
    ]

    fig = go.Figure(
        go.Bar(
            y=labels,
            x=values,
            orientation="h",
            marker_color=colors,
            text=[f"{v:.1f}" for v in values],
            textposition="outside",
            textfont={
                "family": "var(--font-body)",
                "size": 11,
            },
            cliponaxis=False,
            hovertemplate="%{y}<br><b>%{x:.1f}점</b><extra></extra>",
        )
    )

    fig.update_layout(
        height=190,
        margin=dict(
            l=0,
            r=35,
            t=5,
            b=5,
        ),
        xaxis=dict(
            range=[0, 105],
            showgrid=False,
            zeroline=False,
            tickfont={
                "family": "var(--font-body)",
                "size": 10,
                "color": "#8C8370",
            },
            fixedrange=True,
        ),
        yaxis=dict(
            autorange="reversed",
            showgrid=False,
            zeroline=False,
            tickfont={
                "family": "var(--font-body)",
                "size": 11,
                "color": "#2E2A22",
            },
            fixedrange=True,
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="var(--font-body)",
            color="#2E2A22",
        ),
        hoverlabel=dict(
            font=dict(
                family="var(--font-body)",
                size=11,
            )
        ),
    )

    return dcc.Graph(
        figure=fig,
        config={
            "displayModeBar": False,
            "responsive": True,
        },
        style={
            "width": "100%",
            "height": "190px",
        },
    )


# =========================================================
# Fact chips
# =========================================================

def _fact_chips(rec):
    """
    상권의 핵심 특징과 고객/수요 정보를
    하나의 pill 영역으로 표시.
    """

    facts = rec.get("facts", {})
    consumer = rec.get("consumer_profile", {})

    chips = []

    # 최근접 점포
    dist = facts.get("min_distance_to_existing_store_m")
    if dist is not None:
        chips.append(
            html.Span(
                f"최근접 점포 {dist:,}m",
                className="fact-chip",
            )
        )

    # 프랜차이즈 밀집도
    share = facts.get("bakery_franchise_share")
    if share is not None:
        chips.append(
            html.Span(
                f"프랜차이즈 밀집도 {share * 100:.0f}%",
                className="fact-chip",
            )
        )

    # 주요 고객
    primary_segment = consumer.get("primary_segment")
    if primary_segment:
        chips.append(
            html.Span(
                primary_segment,
                className="fact-chip",
            )
        )

    # 수요 맥락
    demand_context = consumer.get("demand_context")
    if demand_context:
        chips.append(
            html.Span(
                demand_context,
                className="fact-chip",
            )
        )

    if not chips:
        return html.Div()

    return html.Div(
        [
            html.Div(
                "핵심 특징",
                className="area-detail-subtitle",
            ),
            html.Div(
                chips,
                className="d-flex flex-wrap gap-2",
            ),
        ],
        className="area-detail-facts",
    )


# =========================================================
# Positive / Risk factors
# =========================================================

def _factor_section(rec):
    """
    핵심 강점과 위험 요인을 의사결정자가 빠르게 읽을 수 있도록 정리.
    """

    positives = rec.get("positive_factors", [])
    risks = rec.get("risk_factors", [])

    children = []

    if positives:
        children.append(
            html.Div(
                [
                    html.Div(
                        "핵심 강점",
                        className="area-detail-subtitle",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span(
                                        "✓",
                                        className="area-detail-check",
                                    ),
                                    html.Span(
                                        factor,
                                        className="area-detail-factor-text",
                                    ),
                                ],
                                className="area-detail-factor-row",
                            )
                            for factor in positives
                        ],
                    ),
                ],
                className="area-detail-factor-group",
            )
        )

    if risks:
        children.append(
            html.Div(
                [
                    html.Div(
                        "핵심 위험",
                        className="area-detail-subtitle area-detail-risk-title",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span(
                                        "주의",
                                        className="area-detail-risk-label",
                                    ),
                                    html.Span(
                                        risk,
                                        className="area-detail-risk-text",
                                    ),
                                ],
                                className="area-detail-risk-row",
                            )
                            for risk in risks
                        ],
                    ),
                ],
                className="area-detail-factor-group",
            )
        )

    if not children:
        return None

    return html.Div(
        children,
        className="area-detail-factors",
    )


# =========================================================
# Basic information
# =========================================================

def _basic_information(rec):
    """
    보조적인 의사결정 정보.
    주요 고객/수요 정보는 핵심 특징 pill에서 표시하고,
    여기서는 데이터 신뢰도만 표시한다.
    """

    data_quality = rec.get("data_quality", {})

    confidence_label = data_quality.get("confidence_label")
    coverage_score = data_quality.get("coverage_score")

    if not confidence_label:
        return None

    confidence_text = confidence_label

    if coverage_score is not None:
        confidence_text += f" · coverage {coverage_score:.0f}"

    return html.Div(
        [
            html.Div(
                "데이터 신뢰도",
                className="area-detail-info-label",
            ),
            html.Div(
                confidence_text,
                className="area-detail-info-value",
            ),
        ],
        className="area-detail-info",
    )


# =========================================================
# Next checks
# =========================================================

def _next_checks(rec):
    """
    실제 출점 전 검토사항.
    """

    checks = rec.get("next_checks", [])

    if not checks:
        return None

    return html.Div(
        [
            html.Div(
                "실제 출점 전 추가 검토",
                className="area-detail-subtitle",
            ),

            html.Ul(
                [
                    html.Li(
                        check,
                        className="area-detail-check-item",
                    )
                    for check in checks
                ],
                className="area-detail-check-list",
            ),
        ],
        className="area-detail-next-checks",
    )


# =========================================================
# Area detail
# =========================================================

def _build_area_detail(rec):
    """
    행을 클릭했을 때 펼쳐지는 상권 상세 영역.

    정보 우선순위:
    1. 평가 구성요소
    2. 핵심 특징 / 고객 / 수요
    3. 강점 / 위험
    4. 고객 / 데이터 신뢰도
    5. 실제 출점 전 검토사항
    """

    score = rec.get("score_components", {})

    factor_section = _factor_section(rec)
    basic_information = _basic_information(rec)
    next_checks = _next_checks(rec)

    children = [
        html.Div(
            [
                html.Div(
                    "핵심 평가",
                    className="area-detail-title",
                ),
                _score_chart(score),
            ],
            className="area-detail-score-section",
        ),

        _fact_chips(rec),
    ]

    if factor_section:
        children.append(factor_section)

    if basic_information:
        children.append(basic_information)

    if next_checks:
        children.append(next_checks)

    return html.Div(
        children,
        className="area-detail-content",
    )


# =========================================================
# Table row
# =========================================================

def _build_area_row_group(rec, selected=False):

    area_id = rec["area_id"]
    rank = rec["rank"]

    suitability_score = rec["suitability_score"]
    tone = _suitability_tone(suitability_score)
    score_color = _TONE_COLOR[tone]

    top_positive = rec.get(
        "positive_factors",
        ["-"],
    )[0]

    top_risk = rec.get(
        "risk_factors",
        ["특이 위험 없음"],
    )[0]

    confidence_label = rec.get(
        "data_quality",
        {},
    ).get(
        "confidence_label",
        "-",
    )

    # -----------------------------------------------------
    # Summary row
    # -----------------------------------------------------

    summary_row = html.Tr(
        [
            # 순위
            html.Td(
                html.Span(
                    str(rank),
                    className="area-table-rank",
                    style={
                        "color": (
                            "var(--color-ink-muted)"
                        ),
                    },
                )
            ),

            # 상권
            html.Td(
                html.Div(
                    rec["area_name"],
                    className="area-table-name",
                )
            ),

            # 적합도
            html.Td(
                html.Span(
                    f"{suitability_score:.1f}",
                    className="area-table-score",
                    style={
                        "color": score_color,
                    },
                )
            ),

            # 핵심 강점
            html.Td(
                html.Div(
                    top_positive,
                    className="area-table-positive",
                )
            ),

            # 핵심 위험
            html.Td(
                html.Div(
                    top_risk,
                    className="area-table-risk",
                )
            ),

            # 신뢰도
            html.Td(
                html.Div(
                    confidence_label,
                    className="area-table-confidence",
                )
            ),
        ],
        id={
            "type": "area-row-toggle",
            "index": area_id,
        },
        n_clicks=0,
        className=(
            "area-table-row area-table-row-selected"
            if selected
            else "area-table-row"
        ),
        style={
            "cursor": "pointer",
        },
    )

    # -----------------------------------------------------
    # Detail row
    # -----------------------------------------------------

    detail_content = _build_area_detail(rec)

    detail_row = html.Tr(
        html.Td(
            dbc.Collapse(
                detail_content,
                id={
                    "type": "area-row-collapse",
                    "index": area_id,
                },
                is_open=selected,
            ),
            colSpan=6,
            style={
                "padding": 0,
                "border": "none",
            },
        )
    )

    return [
        summary_row,
        detail_row,
    ]


# =========================================================
# Main area list
# =========================================================

def build_area_list(
    recommendations,
    selected_area_id=None,
):
    """
    추천 상권 목록.

    - 상단: 의사결정용 요약 표
    - 행 클릭: 해당 상권의 상세 평가 펼침
    """

    if not recommendations:
        return html.P(
            "추천 상권이 없습니다.",
            className="text-muted",
        )

    rows = []

    for rec in recommendations:
        rows += _build_area_row_group(
            rec,
            selected=(
                rec["area_id"] == selected_area_id
            ),
        )

    table = dbc.Table(
        [
            html.Thead(
                html.Tr(
                    [
                        html.Th("순위"),
                        html.Th("상권"),
                        html.Th("적합도"),
                        html.Th("핵심 강점"),
                        html.Th("핵심 위험"),
                        html.Th("신뢰도"),
                    ],
                    className="area-table-head",
                )
            ),
            html.Tbody(rows),
        ],
        bordered=False,
        hover=False,
        responsive=True,
        className="area-table",
    )

    return html.Div(
        table,
        className="area-list-container",
    )