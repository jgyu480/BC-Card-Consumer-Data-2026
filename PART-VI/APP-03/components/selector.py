from dash import html, dcc
import dash_bootstrap_components as dbc


def build_selector(brand_options, compact=False, initial_brand=None, initial_count=None):
    """브랜드 + 희망 출점 수 선택 UI
    compact=False: 랜딩 화면용 (드롭다운 두 개 폭 = 아래 버튼 폭)
    compact=True: 탭바 우측용 (라벨/버튼 없이 슬림하게)
    """
    box_width = 240  # 드롭다운 하나의 고정 폭 (px)

    brand_box = html.Div(
        [
            None if compact else html.Label("브랜드 선택", className="fw-bold mb-2"),
            dcc.Dropdown(
                id="brand-selector",
                options=brand_options,
                value=initial_brand,
                placeholder="브랜드를 선택하세요",
                clearable=False,
            ),
        ],
        style={"width": f"{box_width}px", "flex": f"0 0 {box_width}px"},
    )

    count_box = html.Div(
        [
            None if compact else html.Label("신규 출점 매장 수", className="fw-bold mb-2"),
            dcc.Dropdown(
                id="store-count-selector",
                options=[
                    {"label": "1개", "value": 1},
                    {"label": "2개", "value": 2},
                    {"label": "3개", "value": 3},
                ],
                value=initial_count,
                placeholder="출점 수 선택",
                clearable=False,
            ),
        ],
        style={"width": f"{box_width}px", "flex": f"0 0 {box_width}px"},
    )

    selector_row = html.Div(
        [brand_box, count_box],
        className="selector-row",
        style={"display": "flex", "gap": "16px"},
    )

    if compact:
        return selector_row

    button_row = html.Div(
        dbc.Button(
            "결과 확인",
            id="search-button",
            color="primary",
            className="w-100",
        ),
        style={"marginTop": "16px"},
    )

    wrapper_width = box_width * 2 + 16

    return html.Div(
        [selector_row, button_row],
        style={"width": f"{wrapper_width}px", "margin": "0 auto"},
    )