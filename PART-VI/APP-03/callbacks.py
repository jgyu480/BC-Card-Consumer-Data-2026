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
from components.tab3_area_table import build_area_list, build_area_detail_modal_content
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
# Selected area + Tab switching 
# =========================================================

@dash.callback(
    Output("selected-area-store", "data"),
    Output("active-tab-store", "data"),
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
    Input(
        {"type": "nav-tab", "index": ALL},
        "n_clicks",
    ),
    Input("brand-selector", "value"),
    prevent_initial_call=True,
)
def update_selected_area_and_tab(
    marker_clicks,
    jump_clicks,
    portfolio_jump_clicks,
    nav_clicks,
    brand_id,
):

    triggered_id = ctx.triggered_id
    # 실제 클릭 횟수(n_clicks). 컴포넌트가 화면에 "새로 나타나기만" 해도
    # 이 콜백이 걸리는 Dash 패턴매칭 특성 때문에, isinstance(dict) 체크만
    # 하면 Overview 탭에 들어가기만 해도 "지도에서 보기" 위젯(1위 상권 id를
    # 달고 있음)이 클릭도 안 했는데 선택된 것처럼 처리되는 버그가 있었음.
    # n_clicks가 실제로 1 이상(참값)인지 반드시 같이 확인해서 방지.
    triggered_value = ctx.triggered[0]["value"] if ctx.triggered else None

    # 브랜드가 바뀌면 선택 상권만 초기화 (탭은 그대로 둠)
    if triggered_id == "brand-selector":
        return None, dash.no_update

    if not (isinstance(triggered_id, dict) and triggered_value):
        return dash.no_update, dash.no_update

    tab_type = triggered_id.get("type")

    # 탭 버튼 직접 클릭 — 선택 상권은 안 건드림
    if tab_type == "nav-tab":
        return dash.no_update, triggered_id["index"]

    # 마커 / Overview 지도 / Portfolio에서 상권을 실제로 클릭한 경우:
    # 선택 상권 갱신 + "상권 상세" 탭 이동을 동시에
    if tab_type in (
        "area-marker",
        "overview-map-jump",
        "portfolio-area-jump",
    ):
        return triggered_id["index"], "areas"

    return dash.no_update, dash.no_update

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
            brand,
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

# =========================================================
# Area detail modal (포트폴리오 카드에서 상권 클릭 시)
# =========================================================

@dash.callback(
    Output(
        "area-detail-modal",
        "is_open",
    ),
    Output(
        "area-detail-modal-body",
        "children",
    ),
    Input(
        {"type": "portfolio-area-detail-btn", "index": ALL},
        "n_clicks",
    ),
    Input(
        "area-detail-modal-close",
        "n_clicks",
    ),
    State(
        "brand-selector",
        "value",
    ),
    prevent_initial_call=True,
)
def toggle_area_detail_modal(
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

    if triggered_id == "area-detail-modal-close":
        return False, dash.no_update

    if not triggered_value:
        return (
            dash.no_update,
            dash.no_update,
        )

    # -----------------------------------------
    # 상권 상세 열기
    # -----------------------------------------

    if (
        isinstance(triggered_id, dict)
        and triggered_id.get("type")
        == "portfolio-area-detail-btn"
    ):

        area_id = triggered_id["index"]

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

        rec = next(
            (
                r
                for r in brand.get(
                    "recommendations",
                    [],
                )
                if r["area_id"] == area_id
            ),
            None,
        )

        if rec is None:
            return (
                dash.no_update,
                dash.no_update,
            )

        return (
            True,
            build_area_detail_modal_content(
                rec
            ),
        )

    return (
        dash.no_update,
        dash.no_update,
    )


# =========================================================
# 선택된 상권으로 스크롤 이동
# =========================================================

@dash.callback(
    Output("url", "hash"),
    Input("selected-area-store", "data"),
    Input("active-tab-store", "data"),
    prevent_initial_call=True,
)
def scroll_to_selected_area(selected_area_id, active_tab):

    if not selected_area_id or active_tab != "areas":
        return dash.no_update

    return f"#area-anchor-{selected_area_id}"



# =========================================================
# 상권 상세 탭에서는 출점 수 셀렉터 비활성화
#
# "상권 상세" 탭은 desired_store_count(1/2/3개)에 영향을 안 받고
# 항상 4~20위 전체를 보여주는데, 셀렉터가 활성화돼 있으면 "이걸 바꾸면
# 뭔가 달라지겠지"라고 오해하기 쉬움. 이 탭에서만 흐리게 비활성화 처리.
# =========================================================

@dash.callback(
    Output("store-count-selector", "disabled"),
    Output("store-count-overlay", "style"),
    Input("active-tab-store", "data"),
)
def disable_store_count_on_areas_tab(active_tab):
    is_areas = active_tab == "areas"
    overlay_style = {"display": "flex"} if is_areas else {"display": "none"}
    return is_areas, overlay_style