import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
from app import app
from const import AVAIL_CCY, BTC
from const import DERIBIT_DATA
from dash.dependencies import Input, Output

from market import Futures

# layout = html.Div([
#     [html.Div([
#         dcc.Graph(figure=px.line(Futures('BTC').get_forward(DERIBIT_DATA), x="Maturity", y="Forward_Rates"))
#     ])]
# ])

layout = html.Div([
    html.Div([
        dcc.Checklist(
            id='ccy',
            options=[{'label': i, 'value': i} for i in AVAIL_CCY],
            value=[BTC],
            labelStyle={'display': 'inline-block'}
        )
    ]
        , style={'width': '48%', 'display': 'inline-block'}),
    html.Div(id='fwd_crv')
])


@app.callback(
    Output('fwd_crv', 'children'),
    Input('ccy', 'value'))
def update_graph(ccy):
    return [
        dcc.Graph(figure=px.line(Futures(c).get_forward(DERIBIT_DATA), x="Maturity", y="{}-Forward_Rates".format(c)))
        for c in ccy]
