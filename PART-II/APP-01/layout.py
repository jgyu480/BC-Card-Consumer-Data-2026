from dash import html, dcc
import dash_bootstrap_components as dbc

from utils.data_loader import load_recommendations, get_brand_options
from components.selector import build_selector


SERVICE_DESCRIPTION = (
    "베이커리 브랜드별 기존 점포의 소비환경을 분석해 서울 상권 중 함께 검토할"
    "출점 후보 조합을 제안하는 도구입니다. 예상 매출이나 성공 확률이 아닌, "
    "브랜드 입점 DNA를 기준으로 한 비교 근거를 제공합니다."
)


def build_landing_shell(brand_options):
    return html.Div(
        id="shell-container",
        className="landing-shell",
        children=html.Div(
            className="landing-card",
            children=[
                html.Div("출점 포트폴리오", className="app-wordmark"),
                html.Div(
                    "베이커리 프랜차이즈 신규 출점 추천 서비스",
                    className="landing-headline",
                ),
                html.P(SERVICE_DESCRIPTION, className="landing-description"),
                build_selector(brand_options),
            ],
        ),
    )


def build_layout():
    data = load_recommendations()
    brand_options = get_brand_options(data)

    return html.Div(
        className="page-backdrop",
        children=[
            html.Div(data.get("display_disclaimer", ""), className="page-disclaimer"),

            build_landing_shell(brand_options),

            html.Div(
                id="app-shell-wrap",
                style={"display": "none"},
                children=[
                    html.Div(
                        className="shell-header-row",
                        children=[
                            html.Div(id="tab-folder-wrap"),
                            html.Div(id="selector-outside-wrap"),
                        ],
                    ),

                    dcc.Store(id="selected-area-store", data=None),
                    dcc.Store(id="active-tab-store", data="overview"),

                    # html.Div(id="map-resize-anchor", style={"display": "none"}),

                    html.Div(
                        id="results-wrapper",
                        className="content-card",
                        children=[
                            html.Div(id="tab-panel-overview", style={"display": "block"},
                                      children=html.Div(id="dna-summary-section")),
                            html.Div(id="tab-panel-top3", style={"display": "none"},
                                      children=html.Div(id="portfolio-section")),
                            html.Div(id="tab-panel-areas", style={"display": "none"},
                                      children=[
                                          html.Div(id="map-section", className="mb-4"),
                                          html.Div(id="area-list-section"),
                                      ]),
                        ],
                    ),
                    dbc.Modal(
                        [
                            dbc.ModalHeader(dbc.ModalTitle("조합 상세"), close_button=False),
                            dbc.ModalBody(id="portfolio-detail-modal-body"),
                            dbc.ModalFooter(dbc.Button("닫기", id="portfolio-detail-modal-close", color="secondary", size="sm")),
                        ],
                        id="portfolio-detail-modal",
                        is_open=False,
                        size="lg",
                    ),
                ],
            ),
        ],
    )