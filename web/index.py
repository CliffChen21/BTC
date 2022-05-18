import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app
from apps import history_data, forward_curve, funding_rate

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

home_layout = html.Div([
    dcc.Link('Historical Data', href='/apps/app1'),
    html.Br(),
    dcc.Link('Forward Curve', href='/apps/app2'),
    html.Br(),
    dcc.Link('Funding Rate', href='/apps/app3'),
    html.Br()

])


@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/apps/app1':

        return history_data.layout
    elif pathname == '/apps/app2':
        return forward_curve.layout
    elif pathname == '/apps/app3':
        return funding_rate.layout
    else:
        return home_layout


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')
