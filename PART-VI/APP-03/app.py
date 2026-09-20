import dash
import dash_bootstrap_components as dbc

from layout import build_layout
import callbacks  # noqa: F401  # 콜백 등록을 위해 import만 해도 됨 (dash.callback 데코레이터 방식)

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP],
    suppress_callback_exceptions=True,
)
server = app.server  # Render 배포 시 gunicorn이 이 변수를 찾아서 씀

app.layout = build_layout()

if __name__ == "__main__":
    app.run(debug=False, port=8050)
