from dash import html
import dash_bootstrap_components as dbc

TABS = [
    {"key": "overview", "label": "Brand Overview"},
    {"key": "top3", "label": "추천 포트폴리오"},
    {"key": "areas", "label": "상권 상세"},
]


def build_tab_nav():
    return dbc.Nav(
        [
            dbc.NavLink(
                tab["label"],
                id={"type": "nav-tab", "index": tab["key"]},
                active=(tab["key"] == "overview"),
                n_clicks=0,
                className="tab-link",
            )
            for tab in TABS
        ],
        pills=True,
        className="tab-nav",
    )


def build_tab_folder():
    """탭 개수만큼만 폭을 차지하는 폴더 손잡이 부분"""
    return html.Div(build_tab_nav(), className="tab-folder")