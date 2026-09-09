import dash
from dash import Input, Output, State, ALL, MATCH, html, ctx

from utils.data_loader import (
    load_recommendations,
    get_brand_by_id,
    get_brand_options,
)

from components.tabbar import build_tab_folder, TABS
from components.selector import build_selector
from components.tab1_overview import build_dna_summary
from components.tab2_portfolio import build_portfolio_section
from components.tab2_portfolio_modal import build_portfolio_detail_content
from components.tab3_area_table import build_area_list
from components.tab3_area_map import build_map_view


# =========================================================
# Overview
# =========================================================

@dash.callback(
    Output("dna-summary-section", "children"),
    Input("brand-selector", "value"),
    Input("store-count-selector", "value"),
)
def update_dna_summary(brand_id, desired_store_count):

    data = load_recommendations()
    brand = get_brand_by_id(data, brand_id)

    return build_dna_summary(
        brand,
        desired_store_count,
    )


# =========================================================
# Portfolio
# =========================================================

@dash.callback(
    Output("portfolio-section", "children"),
    Input("brand-selector", "value"),
    Input("store-count-selector", "value"),
)
def update_portfolio_section(brand_id, desired_store_count):

    data = load_recommendations()
    brand = get_brand_by_id(data, brand_id)

    return build_portfolio_section(
        brand,
        desired_store_count,
    )


# =========================================================
# Selected area
# =========================================================

@dash.callback(
    Output("selected-area-store", "data"),
    Input(
        {"type": "area-marker", "index": ALL},
        "n_clicks",
    ),
    Input(
        {"type": "overview-map-jump", "index": ALL},
        "n_clicks",
    ),
    Input(
        {"type": "portfolio-area-jump", "index": ALL},
        "n_clicks",
    ),
    Input("brand-selector", "value"),
    prevent_initial_call=True,
)
def update_selected_area(
    marker_clicks,
    jump_clicks,
    portfolio_jump_clicks,
    brand_id,
):

    triggered_id = ctx.triggered_id

    # 브랜드가 바뀌면 선택 상권 초기화
    if triggered_id == "brand-selector":
        return None

    # 마커 / Overview 지도 / Portfolio에서 상권을 선택한 경우
    if isinstance(triggered_id, dict):
        return triggered_id["index"]

    return dash.no_update


# =========================================================
# Area list + map
# =========================================================

@dash.callback(
    Output("area-list-section", "children"),
    Output("map-section", "children"),
    Input("brand-selector", "value"),
    Input("selected-area-store", "data"),
    Input("active-tab-store", "data"),
)
def update_area_list_and_map(
    brand_id,
    selected_area_id,
    active_tab,
):

    data = load_recommendations()
    brand = get_brand_by_id(data, brand_id)

    if not brand:
        empty = html.P(
            "데이터를 찾을 수 없습니다.",
            className="text-muted",
        )
        return empty, empty

    recommendations = brand["recommendations"]

    # -----------------------------------------
    # 상권 목록
    # -----------------------------------------

    area_list = build_area_list(
        recommendations,
        selected_area_id,
    )

    # -----------------------------------------
    # 지도
    #
    # 중요:
    # 상권 상세 탭이 활성화된 경우에만
    # Leaflet 지도를 생성한다.
    #
    # 처음 페이지 로드 시 display:none 상태인
    # 부모 안에서 Leaflet이 초기화되는 문제를 방지.
    # -----------------------------------------

    if active_tab == "areas":

        area_map = build_map_view(
            recommendations,
            selected_area_id,
        )

    else:

        area_map = html.Div()

    return area_list, area_map


# =========================================================
# Search
# =========================================================

@dash.callback(
    Output("shell-container", "style"),
    Output("app-shell-wrap", "style"),
    Output("tab-folder-wrap", "children"),
    Output("selector-outside-wrap", "children"),
    Input("search-button", "n_clicks"),
    State("brand-selector", "value"),
    State("store-count-selector", "value"),
    prevent_initial_call=True,
)
def handle_search_click(
    n_clicks,
    brand_id,
    desired_store_count,
):

    if not brand_id or desired_store_count is None:
        return (
            dash.no_update,
            dash.no_update,
            dash.no_update,
            dash.no_update,
        )

    data = load_recommendations()
    brand_options = get_brand_options(data)

    folder = build_tab_folder()

    selector = build_selector(
        brand_options,
        compact=True,
        initial_brand=brand_id,
        initial_count=desired_store_count,
    )

    return (
        {"display": "none"},
        {"display": "block"},
        folder,
        selector,
    )


# =========================================================
# Tab switching
# =========================================================

@dash.callback(
    Output("active-tab-store", "data"),
    Input(
        {"type": "nav-tab", "index": ALL},
        "n_clicks",
    ),
    Input(
        {"type": "overview-map-jump", "index": ALL},
        "n_clicks",
    ),
    Input(
        {"type": "portfolio-area-jump", "index": ALL},
        "n_clicks",
    ),
    prevent_initial_call=True,
)
def switch_tab(
    nav_clicks,
    jump_clicks,
    portfolio_jump_clicks,
):

    triggered = ctx.triggered

    if not triggered or not ctx.triggered_id:
        return dash.no_update

    triggered_id = ctx.triggered_id

    val = ctx.triggered[0].get("value")

    if not val:
        return dash.no_update

    # -----------------------------------------
    # 탭 버튼
    # -----------------------------------------

    if isinstance(triggered_id, dict):

        tab_type = triggered_id.get("type")

        if tab_type == "nav-tab":
            return triggered_id["index"]

        # Overview / Portfolio에서 상권 상세로 이동
        if tab_type in (
            "overview-map-jump",
            "portfolio-area-jump",
        ):
            return "areas"

    return dash.no_update


# =========================================================
# Active tab highlight
# =========================================================

@dash.callback(
    Output(
        {"type": "nav-tab", "index": ALL},
        "active",
    ),
    Input("active-tab-store", "data"),
)
def highlight_active_tab(active_tab):

    return [
        tab["key"] == active_tab
        for tab in TABS
    ]


# =========================================================
# Show active panel
# =========================================================

@dash.callback(
    Output("tab-panel-overview", "style"),
    Output("tab-panel-top3", "style"),
    Output("tab-panel-areas", "style"),
    Input("active-tab-store", "data"),
)
def show_active_panel(active_tab):

    def style_for(key):

        return (
            {"display": "block"}
            if active_tab == key
            else {"display": "none"}
        )

    return (
        style_for("overview"),
        style_for("top3"),
        style_for("areas"),
    )


# =========================================================
# Area row collapse
# =========================================================

@dash.callback(
    Output(
        {"type": "area-row-collapse", "index": MATCH},
        "is_open",
    ),
    Input(
        {"type": "area-row-toggle", "index": MATCH},
        "n_clicks",
    ),
    State(
        {"type": "area-row-collapse", "index": MATCH},
        "is_open",
    ),
    prevent_initial_call=True,
)
def toggle_area_row(
    n_clicks,
    is_open,
):

    return not is_open


# =========================================================
# Portfolio detail modal
# =========================================================

@dash.callback(
    Output(
        "portfolio-detail-modal",
        "is_open",
    ),
    Output(
        "portfolio-detail-modal-body",
        "children",
    ),
    Input(
        {"type": "portfolio-detail-btn", "index": ALL},
        "n_clicks",
    ),
    Input(
        "portfolio-detail-modal-close",
        "n_clicks",
    ),
    State(
        "brand-selector",
        "value",
    ),
    prevent_initial_call=True,
)
def toggle_portfolio_detail_modal(
    detail_clicks,
    close_clicks,
    brand_id,
):

    triggered_id = ctx.triggered_id

    triggered_value = (
        ctx.triggered[0]["value"]
        if ctx.triggered
        else None
    )

    # -----------------------------------------
    # 모달 닫기
    # -----------------------------------------

    if triggered_id == "portfolio-detail-modal-close":
        return False, dash.no_update

    if not triggered_value:
        return (
            dash.no_update,
            dash.no_update,
        )

    # -----------------------------------------
    # Portfolio 상세 열기
    # -----------------------------------------

    if (
        isinstance(triggered_id, dict)
        and triggered_id.get("type")
        == "portfolio-detail-btn"
    ):

        store_count_str, rank_str = (
            triggered_id["index"].split("-")
        )

        desired_store_count = int(
            store_count_str
        )

        rank = int(rank_str)

        data = load_recommendations()

        brand = get_brand_by_id(
            data,
            brand_id,
        )

        if not brand:
            return (
                dash.no_update,
                dash.no_update,
            )

        portfolio = next(
            (
                p
                for p in brand.get(
                    "portfolios",
                    [],
                )
                if (
                    p["desired_store_count"]
                    == desired_store_count
                    and
                    p["portfolio_rank"]
                    == rank
                )
            ),
            None,
        )

        if portfolio is None:
            return (
                dash.no_update,
                dash.no_update,
            )

        return (
            True,
            build_portfolio_detail_content(
                brand,
                portfolio,
            ),
        )

    return (
        dash.no_update,
        dash.no_update,
    )