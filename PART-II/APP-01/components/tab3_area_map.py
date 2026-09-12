import dash_leaflet as dl
import dash_bootstrap_components as dbc
from dash import html


def _map_tooltip(rec):
    """
    지도 마커 hover 시 의사결정에 필요한 핵심 정보를 표시.
    """

    facts = rec.get("facts", {})
    score = rec.get("score_components", {})
    quality = rec.get("data_quality", {})

    distance = facts.get("min_distance_to_existing_store_m")
    franchise_share = facts.get("bakery_franchise_share")

    distance_text = (
        f"{distance:,}m"
        if distance is not None
        else "-"
    )

    franchise_text = (
        f"{franchise_share * 100:.0f}%"
        if franchise_share is not None
        else "-"
    )

    return html.Div(
        [
            html.Div(
                f"{rec['rank']}순위 · {rec['area_name']}",
                style={
                    "fontWeight": "700",
                    "fontSize": "13px",
                    "marginBottom": "6px",
                },
            ),

            html.Div(
                [
                    html.Span("종합 적합도 ", className="text-muted"),
                    html.Strong(f"{rec['suitability_score']:.1f}점"),
                ],
                style={"marginBottom": "4px"},
            ),

            html.Div(
                [
                    html.Span("DNA 적합도 ", className="text-muted"),
                    html.Span(
                        f"{score.get('dna_match_score', 0):.1f}"
                    ),
                ],
            ),

            html.Div(
                [
                    html.Span("시장 규모 ", className="text-muted"),
                    html.Span(
                        f"{score.get('market_score', 0):.1f}"
                    ),
                ],
            ),

            html.Div(
                [
                    html.Span("경쟁 매력도 ", className="text-muted"),
                    html.Span(
                        f"{score.get('competition_attractiveness_score', 0):.1f}"
                    ),
                ],
            ),

            html.Div(
                [
                    html.Span("근접 위험도 ", className="text-muted"),
                    html.Span(
                        f"{score.get('proximity_risk_score', 0):.1f}"
                    ),
                ],
            ),

            html.Hr(
                style={
                    "margin": "6px 0",
                    "borderColor": "#E8E2D8",
                }
            ),

            html.Div(
                [
                    html.Span("최근접 점포 ", className="text-muted"),
                    html.Span(distance_text),
                ],
            ),

            html.Div(
                [
                    html.Span("프랜차이즈 밀집도 ", className="text-muted"),
                    html.Span(franchise_text),
                ],
            ),

            html.Div(
                [
                    html.Span("데이터 신뢰도 ", className="text-muted"),
                    html.Span(
                        quality.get("confidence_label", "-")
                    ),
                ],
                style={"marginTop": "3px"},
            ),
        ],
        style={
            "fontFamily": "var(--font-body)",
            "fontSize": "11px",
            "lineHeight": "1.5",
            "minWidth": "180px",
        },
    )


def build_map_view(recommendations, selected_area_id=None):
    """상권 위치 지도. area_id를 공유 id로 써서 표와 연동한다."""

    if not recommendations:
        return html.P(
            "표시할 상권이 없습니다.",
            className="text-muted"
        )

    markers = []

    for rec in recommendations:

        is_selected = rec["area_id"] == selected_area_id

        markers.append(
            dl.CircleMarker(
                id={
                    "type": "area-marker",
                    "index": rec["area_id"]
                },

                center=[
                    rec["centroid_latitude"],
                    rec["centroid_longitude"]
                ],

                radius=13 if is_selected else 9,

                color=(
                    "#0F6E56"
                    if is_selected
                    else "#5B7332"
                ),

                fillColor=(
                    "#0F6E56"
                    if is_selected
                    else "#5B7332"
                ),

                fillOpacity=0.82,

                weight=2 if is_selected else 1,

                children=[
                    dl.Tooltip(
                        _map_tooltip(rec),
                        direction="top",
                        sticky=True,
                    )
                ],
            )
        )

    avg_lat = sum(
        r["centroid_latitude"]
        for r in recommendations
    ) / len(recommendations)

    avg_lng = sum(
        r["centroid_longitude"]
        for r in recommendations
    ) / len(recommendations)

    map_component = dl.Map(
        id="area-map",

        center=[
            avg_lat,
            avg_lng
        ],

        zoom=11,

        style={
            "height": "480px",
            "width": "100%",
            "borderRadius": "12px",
            "overflow": "hidden",
        },

        children=[
            dl.TileLayer(),
            *markers,
        ],
    )

    return dbc.Card(
        dbc.CardBody(
            map_component,
            className="p-2",
        ),
        className="shadow-sm border-0",
    )


def build_mini_map(top_area):
    """Overview 탭용 작은 지도."""

    marker = dl.CircleMarker(
        center=[
            top_area["centroid_latitude"],
            top_area["centroid_longitude"]
        ],
        radius=10,
        color="#0F6E56",
        fillColor="#0F6E56",
        fillOpacity=0.8,
        weight=2,
    )

    mini_map = dl.Map(
        id=f"mini-map-{top_area['area_id']}",
        center=[
            top_area["centroid_latitude"],
            top_area["centroid_longitude"]
        ],

        zoom=13,

        style={
            "height": "220px",
            "width": "100%",
            "borderRadius": "8px",
            "overflow": "hidden",
        },

        children=[
            dl.TileLayer(),
            marker,
        ],
    )

    return html.Div(
        id={
            "type": "overview-map-jump",
            "index": top_area["area_id"]
        },

        n_clicks=0,

        style={
            "cursor": "pointer"
        },

        children=mini_map,
    )

