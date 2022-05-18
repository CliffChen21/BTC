import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px
from app import app
from const import AVAIL_CCY, BTC
from const import DERIBIT_DATA
from dash.dependencies import Input, Output

from market import Futures
from tools.time import Time

# layout = html.Div([
#     [html.Div([
#         dcc.Graph(figure=px.line(Futures('BTC').get_forward(DERIBIT_DATA), x="Maturity", y="Forward_Rates"))
#     ])]
# ])

layout = html.Div([
    html.Div([
        dcc.Checklist(
            id='ccy2',
            options=[{'label': i, 'value': i} for i in AVAIL_CCY],
            value=[BTC],
            labelStyle={'display': 'inline-block'}
        )
    ]
        , style={'width': '48%', 'display': 'inline-block'}),
    html.Div(id='fund_rate')
])


@app.callback(
    Output('fund_rate', 'children'),
    Input('ccy2', 'value'))
def update_graph(ccy):
    def get_dataframe2(ccy, exchange=DERIBIT_DATA, local_time=True):
        data = Futures(ccy).get_instrument(exchange, '{}-FUNDING'.format(ccy), '1Y')
        if local_time:
            df = pd.DataFrame(
                {'date': [Time(t).get_local_dt for t in data['ticks']], '{}-Funding'.format(ccy): data['interest_8h']})
        else:
            df = pd.DataFrame(
                {'date': [Time(t).get_deribit_dt for t in data['ticks']],
                 '{}-Funding'.format(ccy): data['interest_8h']})
        df['{}-Funding'.format(ccy)] = df['{}-Funding'.format(ccy)] * 3 * 365
        print('{}-Funding'.format(ccy), df['{}-Funding'.format(ccy)].mean())
        return df

    return [
        dcc.Graph(figure=px.line(get_dataframe2(c, DERIBIT_DATA), x="date", y="{}-Funding".format(c)))
        for c in ccy]
