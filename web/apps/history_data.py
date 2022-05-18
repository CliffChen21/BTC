import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px
from app import app
from const import FUTURES, DERIBIT_DATA
from dash.dependencies import Input, Output

from tools.redis_client import r, LoadObj
from tools.time import Time

# reference : https://plotly.com/python/time-series/


futures_mkt = LoadObj(r.get(FUTURES))
instrument_list = list(futures_mkt[DERIBIT_DATA].keys())

layout = html.Div([
                      html.Button(instrument_list[i], 'btn-{}'.format(i)) for i in range(len(instrument_list))
                  ] + [html.Div(id='history')])


@app.callback(
    Output("history", "children"),
    [Input("btn-{}".format(i), "n_clicks") for i in range(len(instrument_list))])
def display_history(*args):
    futures_mkt = LoadObj(r.get(FUTURES))
    instrument_list = list(futures_mkt[DERIBIT_DATA].keys())

    def get_dataframe(instrument, exchange=DERIBIT_DATA, local_time=True):
        futures_mkt = LoadObj(r.get(FUTURES))
        data = futures_mkt[exchange][instrument]
        if local_time:
            df = pd.DataFrame(
                {'date': [Time(t).get_local_dt for t in data.ticks], instrument: data.close})
        else:
            df = pd.DataFrame(
                {'date': [Time(t).get_deribit_dt for t in data.ticks], instrument: data.close})
        return df

    ctx = dash.callback_context
    rtn_list = []
    for i in range(len(instrument_list)):
        if isinstance(ctx.inputs['btn-{}.n_clicks'.format(i)], int):
            if ctx.inputs['btn-{}.n_clicks'.format(i)] % 2 != 0:
                rtn_list.append(instrument_list[i])
    return [html.Div(children='update time: ' + str(r.get('UPDATE_TIME'))[2:-1])] + [
        dcc.Graph(
            id=instrument,
            figure=px.line(get_dataframe(instrument), x='date', y=instrument)
        ) for instrument in rtn_list
    ]


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')
