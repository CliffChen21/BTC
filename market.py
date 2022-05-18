from abc import ABC
from copy import deepcopy
from datetime import timedelta, datetime

import numpy as np
import pandas as pd
from config import Config
from const import DEFAULT_ROOT, DERIBIT_DATA, FUTURES, OPTIONS, AVAIL_CCY

from exchange_api.deribit_api import Deribit
from tools.redis_client import r, SaveObj
from tools.time import Time


class DataAtom:

    def __init__(self, raw_data):
        self.raw_data = raw_data
        for k, v in raw_data.items():
            setattr(self, k, v)

    @property
    def to_df(self):
        return pd.DataFrame.from_dict(self.raw_data)

    @property
    def to_list(self):
        rest_data = deepcopy(self.raw_data)
        ticks = rest_data.pop('ticks')
        return [['ticks'] + [k for k in rest_data]] + [[ticks[i]] + [rest_data[k][i] for k in rest_data] for i in
                                                       range(len(ticks))]


class Instruments(ABC):

    def __init__(self, config_file="{}//sample_config.json".format(DEFAULT_ROOT)):
        self.config = Config()
        self.config.loads(config_file)
        self.exchanges = {DERIBIT_DATA: Deribit(self.get_account(DERIBIT_DATA))}
        self.instrument_symbol = {k: self.get_instrument_symbol(k) for k in self.exchanges}

    def get_account(self, platform):
        return [account for account in self.config.ACCOUNTS if account['platform'] == platform][0]

    def get_instrument_symbol(self, exchange):
        if self.market in self.get_account(exchange)['instruments_type']:
            return self.exchanges[exchange].tradeable_symbols(self.ccy, self.get_account(exchange)['instruments_type'][
                self.market])
        else:
            return [None]

    def get_instrument(self, exchange, instrument, tenor, resolution=None, local_time=False):

        if exchange == DERIBIT_DATA:
            end = Time.get_now()
            tenor_f = {'min': lambda tnr: timedelta(minutes=int(tnr[:-3])),
                       'D': lambda tnr: timedelta(days=int(tnr[:-1])),
                       'W': lambda tnr: timedelta(days=7 * int(tnr[:-1])),
                       'M': lambda tnr: timedelta(weeks=7 * int(tnr[:-1])),
                       'Y': lambda tnr: timedelta(weeks=52 * int(tnr[:-1])),
                       }
            start = Time(end.get_deribit_dt - tenor_f[tenor[-1]](tenor), 'utc')
            if instrument.split('-')[1] == 'FUNDING':
                res = \
                self.exchanges[exchange].get_funding_chart_history_data("{}-PERPETUAL".format(instrument.split('-')[0]),
                                                                        start.get_deribit_ts, end.get_deribit_ts)[
                    'result']
                result = {}
                if local_time:
                    result['ticks'] = [Time.get_from_deribit(ttt['timestamp']).get_local_ts for ttt in res]
                else:
                    result['ticks'] = [Time.get_from_deribit(ttt['timestamp']).time for ttt in res]
                result['interest_8h'] = [ttt['interest_8h'] for ttt in res]
            elif instrument.split('-')[1] == 'INDEX':
                res = \
                self.exchanges[exchange].get_funding_chart_history_data("{}-PERPETUAL".format(instrument.split('-')[0]),
                                                                        start.get_deribit_ts, end.get_deribit_ts)[
                    'result']
                result = {}
                if local_time:
                    result['ticks'] = [Time.get_from_deribit(ttt['timestamp']).get_local_ts for ttt in res]
                else:
                    result['ticks'] = [Time.get_from_deribit(ttt['timestamp']).time for ttt in res]
                result['index_price'] = [ttt['index_price'] for ttt in res]
            else:
                result = \
                    self.exchanges[exchange].get_tradingview_chart_data(instrument, start.get_deribit_ts,
                                                                        end.get_deribit_ts,
                                                                        resolution)['result']
                if local_time:
                    result['ticks'] = [Time.get_from_deribit(ttt).get_local_ts for ttt in result['ticks']]
                else:
                    result['ticks'] = [Time.get_from_deribit(ttt).time for ttt in result['ticks']]

            return result

    def get_instruments(self, tenor, resolution=None, local_time=False):
        hdata = {}
        for exchange in self.exchanges:
            hdata[exchange] = {}
            for instrument in self.instrument_symbol[exchange] + ['{}-INDEX'.format(self.ccy)]:
                data_obj = self.get_instrument(exchange, instrument, tenor, resolution, local_time)
                hdata[exchange][instrument] = DataAtom(data_obj)
        return hdata

    @classmethod
    def is_perpetual(cls, instrument, exchange):
        if exchange == DERIBIT_DATA:
            return instrument in ['{}-PERPETUAL'.format(ccy) for ccy in AVAIL_CCY]

    def get_maturity(self, instrument, exchange):
        if exchange == DERIBIT_DATA and not Instruments.is_perpetual(instrument, exchange):
            dd = int(instrument.split('-')[1][:-5])
            mm = {'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4, 'MAY': 5, 'JUN': 6, 'JUL': 7, 'AUG': 8, 'SEP': 9, 'OCT': 10,
                  'NOV': 11, 'DEC': 12}[instrument.split('-')[1][-5:-2]]
            yy = int(instrument.split('-')[1][-2:])
            return datetime(2000 + yy, mm, dd, 16, 0, 0)
        elif Instruments.is_perpetual(instrument, exchange):
            return datetime(4000, 1, 1, 16, 0, 0)


class Futures(Instruments):

    def __init__(self, ccy):
        self.market = FUTURES
        self.ccy = ccy
        super(Futures, self).__init__()

    def get_forward(self, exchange=DERIBIT_DATA):
        forward_dict = {}
        for instrument in self.get_instrument_symbol(exchange):
            orderbook = self.exchanges[exchange].get_order_book(instrument, 1)
            forward_dict[instrument] = (orderbook['bid'][0][0] + orderbook['ask'][0][0]) / 2
        maturities = []
        rates = []
        first = True
        instruments = sorted(list(forward_dict.keys()), key=lambda k: self.get_maturity(k, exchange))
        for instrument in instruments:
            if not Futures.is_perpetual(instrument, exchange):
                maturity = self.get_maturity(instrument, exchange)
                if first:
                    if exchange == DERIBIT_DATA:
                        rates.append(np.log(forward_dict[instrument] / self.exchanges[exchange].get_index_price(
                            '{}_usd'.format(self.ccy.lower()))) / (
                                                 maturity - datetime.now()).total_seconds() * 365 * 24 * 3600)
                        first = False
                else:
                    if exchange == DERIBIT_DATA:
                        rates.append(
                            np.log(forward_dict[instrument] / forward_dict[last_instrument]) / (
                                    maturity - maturities[-1]).total_seconds() * 365 * 24 * 3600)
                maturities.append(maturity)
                last_instrument = instrument
        return {'Maturity': maturities, '{}-Forward_Rates'.format(self.ccy): rates}

    def get_forward_df(self, exchange=DERIBIT_DATA):
        return pd.DataFrame(self.get_forward(exchange))


class Options(Instruments):

    def __init__(self, ccy):
        self.market = OPTIONS
        self.ccy = ccy
        super(Options, self).__init__()


def Update():
    futures_market = Futures('BTC').get_instruments('1Y', 10)
    r.set(FUTURES, SaveObj(futures_market))
    print(futures_market.keys())
    # options_market = Options('BTC').get_instruments('1Y', 10)
    # r.set(OPTIONS, SaveObj(options_market))
    # print(options_market.keys())
    r.set("UPDATE_TIME", datetime.now().strftime("%m-%d-%Y %H:%M:%S"))


if __name__ == "__main__":
    POS = Futures('BTC')  # .exchanges[DERIBIT_DATA].get_positions("BTC")
    print(POS)
    RES = POS.get_instrument(DERIBIT_DATA, '{}-INDEX'.format("BTC"), '1Y')
    delta = 0
    for ins in POS['result']:
        print(ins['instrument'], ins['sizeBtc'])
        delta = delta + ins['sizeBtc']
    print(delta)
    print("B")
    # while True:
    #     try:
    #         if (Time.get_now().get_local_dt - datetime.strptime(r.get('UPDATE_TIME').decode('utf-8'),
    #                                                   '%m-%d-%Y %H:%M:%S')).total_seconds() > 60:
    #             Update()
    #     except Exception as e:
    #         print("error at {}".format(Time.get_now().get_local_dt.strftime("%H:%M:%S")))
    #         print()
    #         print(e)
