from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

from components.tab1_overview import build_brand_identity_header


def build_portfolio_card(portfolio):
    """
    추천 포트폴리오 카드

    디자인 방향:
    - Overview와 동일하게 흰색 surface 중심
    - 카드 border 제거
    - 1순위는 색/타이포그래피로만 강조
    - 장식적인 상단 accent line 사용하지 않음
    """

    rank = portfolio["portfolio_rank"]
    is_primary = rank == 1

    # ---------------------------------------------------------
    # Rank label
    # ---------------------------------------------------------
    rank_label = html.Div(
        f"추천안 {rank:02d}",
        className="portfolio-rank-label",
    )

    rank_description = html.Div(
        "최우선 추천" if is_primary else "대안",
        className="portfolio-rank-desc",
    )

    # ---------------------------------------------------------
    # Score
    # ---------------------------------------------------------
    score = portfolio.get("portfolio_score", 0)

    score_block = html.Div(
        [
            html.Span(
                f"{score:.1f}",
                className="portfolio-score",
            ),
            html.Span(
                "종합 적합도",
                className="portfolio-score-label",
            ),
        ],
        className="portfolio-score-block",
    )

    # ---------------------------------------------------------
    # Area list
    # ---------------------------------------------------------
    area_items = []

    for idx, (area_id, name) in enumerate(
        zip(
            portfolio.get("area_ids", []),
            portfolio.get("area_names", []),
        ),
        start=1,
    ):
        area_items.append(
            html.Div(
                [
                    html.Span(
                        str(idx),
                        className="portfolio-area-index",
                    ),
                    html.Div(
                        name,
                        className="portfolio-area-name",
                    ),
                ],
                className="portfolio-area-item",
            )
        )

    # ---------------------------------------------------------
    # Rationale
    # ---------------------------------------------------------
    rationale_facts = portfolio.get("rationale_facts", [])

    if rationale_facts:
        rationale_text = rationale_facts[0]
    else:
        rationale_text = "선정 상권의 평균 적합도를 기준으로 추천되었습니다."

    rationale_block = html.Div(
        [
            html.Div(
                "핵심 근거",
                className="portfolio-section-label",
            ),
            html.Div(
                rationale_text,
                className="portfolio-rationale",
            ),
        ],
        className="portfolio-rationale-block",
    )

    # ---------------------------------------------------------
    # Risk
    # ---------------------------------------------------------
    overlap_risk = (
        portfolio.get("score_components", {})
        .get("overlap_risk_score")
    )

    risk_items = portfolio.get("risk_factors", [])

    if overlap_risk is not None and overlap_risk > 0:
        risk_block = html.Div(
            [
                html.Span(
                    "주의",
                    className="portfolio-risk-label",
                ),
                html.Span(
                    f"중복위험 {overlap_risk:.1f}",
                    className="portfolio-risk-value",
                ),
            ],
            className="portfolio-risk",
        )

    elif risk_items:
        risk_block = html.Div(
            [
                html.Span(
                    "주의",
                    className="portfolio-risk-label",
                ),
                html.Span(
                    risk_items[0],
                    className="portfolio-risk-value",
                ),
            ],
            className="portfolio-risk",
        )

    else:
        risk_block = html.Div(
            [
                html.Span(
                    "검토",
                    className="portfolio-risk-label-neutral",
                ),
                html.Span(
                    "특이 위험 없음",
                    className="portfolio-risk-value-neutral",
                ),
            ],
            className="portfolio-risk",
        )

    # ---------------------------------------------------------
    # Detail link
    # ---------------------------------------------------------
    detail_link = html.Div(
        [
            html.Span("상세보기"),
            html.Span(
                "→",
                className="portfolio-detail-arrow",
            ),
        ],
        id={
            "type": "portfolio-detail-btn",
            "index": (
                f"{portfolio['desired_store_count']}-"
                f"{portfolio['portfolio_rank']}"
            ),
        },
        n_clicks=0,
        className="portfolio-detail-link",
    )

    # ---------------------------------------------------------
    # Card
    # ---------------------------------------------------------
    card_classes = "portfolio-card"

    if is_primary:
        card_classes += " portfolio-card-primary"

    return html.Div(
        [
            html.Div(
                [
                    rank_label,
                    rank_description,
                ],
                className="portfolio-card-header",
            ),

            score_block,

            html.Div(
                className="portfolio-divider",
            ),

            html.Div(
                "출점 후보",
                className="portfolio-section-label",
            ),

            html.Div(
                area_items,
                className="portfolio-area-list",
            ),

            rationale_block,

            html.Div(
                [
                    risk_block,
                    detail_link,
                ],
                className="portfolio-card-footer",
            ),
        ],
        className=card_classes,
    )


def build_single_store_chart(portfolios, brand_recommendations):
    """
    희망 출점 수 1개일 때:
    recommendations에서 해당 상권의 실제 세부 점수를 매핑하여 비교
    """

    x_metrics = [
        "최종 적합도",
        "DNA 유사도",
        "시장 규모",
        "경쟁 매력도",
    ]

    fig = go.Figure()

    rank_colors = {
        1: "#5B7332",
        2: "#8A9A5B",
        3: "#C9B18F",
    }

    rec_map = {
        r["area_id"]: r
        for r in brand_recommendations
    }

    for p in portfolios:
        rank = p["portfolio_rank"]
        area_ids = p.get("area_ids", [])

        rec_data = (
            rec_map.get(area_ids[0], {})
            if area_ids
            else {}
        )

        score_comp = rec_data.get(
            "score_components",
            {},
        )

        suitability = rec_data.get(
            "suitability_score",
            p.get("portfolio_score", 0),
        )

        dna = score_comp.get(
            "dna_match_score",
            0,
        )

        market = score_comp.get(
            "market_score",
            0,
        )

        competition = score_comp.get(
            "competition_attractiveness_score",
            0,
        )

        scores = [
            suitability,
            dna,
            market,
            competition,
        ]

        fig.add_trace(
            go.Bar(
                name=f"{rank}순위",
                x=x_metrics,
                y=scores,
                marker_color=rank_colors.get(
                    rank,
                    "#78716C",
                ),
                text=[
                    f"{v:.1f}" if v > 0 else "-"
                    for v in scores
                ],
                textposition="auto",
            )
        )

    fig.update_layout(
        barmode="group",
        bargap=0.25,
        bargroupgap=0.12,
        height=300,
        margin=dict(
            l=20,
            r=20,
            t=20,
            b=30,
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="Inter, sans-serif",
            color="#2E2A22",
            size=12,
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
        yaxis=dict(
            range=[0, 100],
            showgrid=True,
            gridcolor="rgba(0,0,0,0.05)",
        ),
        xaxis=dict(
            showgrid=False,
        ),
    )

    return dcc.Graph(
        figure=fig,
        config={
            "displayModeBar": False,
        },
    )


def build_metric_comparison_chart(portfolios):
    """
    2~3개 출점 시:
    포트폴리오의 종합 점수 + 긍정 지표 비교
    """

    field_keys = [
        "average_area_score",
        "geographic_diversification_score",
        "consumer_diversification_score",
    ]

    x_metrics = [
        "종합 점수",
        "평균 상권 적합도",
        "지역 분산도",
        "소비자 분산도",
    ]

    fig = go.Figure()

    rank_colors = {
        1: "#5B7332",
        2: "#8A9A5B",
        3: "#C9B18F",
    }

    for p in portfolios:
        rank = p["portfolio_rank"]
        score_comp = p.get(
            "score_components",
            {},
        )

        overall = p.get(
            "portfolio_score"
        ) or 0

        scores = [
            overall
        ] + [
            score_comp.get(field) or 0
            for field in field_keys
        ]
        
        fig.add_trace(
            go.Bar(
                name=f"{rank}순위",
                x=x_metrics,
                y=scores,
                marker_color=rank_colors.get(
                    rank,
                    "#78716C",
                ),
                text=[
                    f"{v:.1f}" if v > 0 else "-"
                    for v in scores
                ],
                textposition="auto",
                hovertemplate="<b>%{fullData.name}</b><br>%{x}<br><b>%{y:.1f}점</b><extra></extra>",
            )
        )

    fig.update_layout(
        barmode="group",
        bargap=0.25,
        bargroupgap=0.12,
        height=300,
        margin=dict(
            l=20,
            r=20,
            t=20,
            b=30,
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="Inter, sans-serif",
            color="#2E2A22",
            size=12,
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
        yaxis=dict(
            range=[0, 100],
            showgrid=True,
            gridcolor="rgba(0,0,0,0.05)",
        ),
        xaxis=dict(
            showgrid=False,
        ),
        hoverlabel=dict(
            font=dict(
                family="Inter, sans-serif",
                size=11,
            )
        ),
    )

    return dcc.Graph(
        figure=fig,
        config={
            "displayModeBar": False,
        },
    )


def build_portfolio_section(
    brand,
    desired_store_count,
):
    """추천 포트폴리오 섹션 최종 구성"""

    header = build_brand_identity_header(
        brand
    )

    if brand is None:
        return html.Div(
            [
                header,
                html.P(
                    "브랜드를 선택해주세요."
                ),
            ]
        )

    portfolios = brand.get(
        "portfolios",
        [],
    )

    filtered = [
        p
        for p in portfolios
        if p["desired_store_count"]
        == desired_store_count
    ]

    filtered = sorted(
        filtered,
        key=lambda p: p["portfolio_rank"],
    )[:3]

    if not filtered:
        return html.Div(
            [
                header,
                html.P(
                    "해당 출점 수의 추천 조합이 없습니다."
                ),
            ]
        )

    # ---------------------------------------------------------
    # Page intro
    # ---------------------------------------------------------
    intro = html.Div(
        [
            html.Div(
                "추천 포트폴리오",
                className="portfolio-page-title",
            ),
            html.Div(
                "출점 수에 따른 추천 조합을 비교합니다. "
                "1순위 안을 우선 검토하고, 대안을 함께 비교할 수 있습니다.",
                className="portfolio-page-description",
            ),
        ],
        className="portfolio-page-intro",
    )

    # ---------------------------------------------------------
    # Portfolio cards
    # ---------------------------------------------------------
    card_columns = []

    for p in filtered:
        card_columns.append(
            dbc.Col(
                build_portfolio_card(p),
                width=12 // len(filtered),
                className="portfolio-card-col",
            )
        )

    children = [
        header,
        html.Div(
            [
                intro,
                dbc.Row(
                    card_columns,
                    className="portfolio-card-row",
                ),
            ],
            className="portfolio-section",
        ),
    ]

    # ---------------------------------------------------------
    # Comparison chart
    # ---------------------------------------------------------
    if desired_store_count >= 2:

        children.append(
            dbc.Card(
                dbc.CardBody(
                    [
                        html.Div(
                            [
                                html.Div(
                                    "포트폴리오 비교",
                                    className="comparison-title",
                                ),
                                html.Div(
                                    "상권 적합도와 지역·소비자 분산 수준을 기준으로 추천안 간 차이를 비교합니다.",
                                    className="comparison-description",
                                ),
                            ],
                            className="comparison-header",
                        ),

                        html.Div(
                            build_metric_comparison_chart(
                                filtered
                            ),
                            className="comparison-chart-wrap",
                        ),
                    ]
                ),
                className="portfolio-comparison-card",
            )
        )

    # ---------------------------------------------------------
    # Single store chart
    # ---------------------------------------------------------
    else:

        all_recs = brand.get(
            "recommendations",
            [],
        )

        children.append(
            dbc.Card(
                dbc.CardBody(
                    [
                        html.Div(
                            [
                                html.Div(
                                    "단일 상권 핵심 지표 비교",
                                    className="comparison-title",
                                ),
                                html.Div(
                                    "단일 후보 상권들의 적합도와 핵심 환경 지표를 비교합니다.",
                                    className="comparison-description",
                                ),
                            ],
                            className="comparison-header",
                        ),

                        html.Div(
                            build_single_store_chart(
                                filtered,
                                all_recs,
                            ),
                            className="comparison-chart-wrap",
                        ),
                    ]
                ),
                className="portfolio-comparison-card",
            )
        )

    # ---------------------------------------------------------
    # Next checks
    # ---------------------------------------------------------
    shared_checks = filtered[0].get(
        "next_checks",
        [],
    )

    if shared_checks:

        children.append(
            html.Div(
                [
                    html.Div(
                        "공통 추가 검토사항",
                        className="next-checks-title",
                    ),

                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span(
                                        "•",
                                        className="next-checks-bullet",
                                    ),
                                    html.Span(
                                        check,
                                        className="next-checks-text",
                                    ),
                                ],
                                className="next-check-item",
                            )
                            for check in shared_checks
                        ],
                        className="next-checks-list",
                    ),
                ],
                className="portfolio-next-checks",
            )
        )

    return html.Div(children)