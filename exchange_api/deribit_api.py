import asyncio
import json
from datetime import datetime

import requests
from aiohttp import ClientSession


class Deribit:

    def __init__(self, Tokens):
        # drbt = # account information
        self.key = Tokens['account']
        self.secret = Tokens['secret_key']
        self.session = requests.Session()
        self.url = Tokens['host']
        self.token = self.get_token()
        self.update = datetime.now().timestamp()

    def request(self, action):
        if datetime.now().timestamp() - self.update > 800:
            self.token = self.get_token()
        if action.startswith('/api/v2/private'):
            response = self.session.get(self.url + action, headers={
                "Content-Type": 'application/json',
                "Authorization": "Bearer " + self.token
            })
            return response.json()

        else:
            print(self.url + action)
            response = self.session.get(self.url + action)
            return response.json()

    async def async_engine(self, url):
        # print('request: ' + str(time.time()))
        async with ClientSession() as session:
            async with session.get(url, headers={
                "Content-Type": 'application/json',
                "Authorization": "Bearer " + self.token}) as response:
                response = await response.read()
        return json.loads(response)

    def place_order(self, urls: list):
        self.token = self.get_token()
        # print(urls)
        orders = []
        for url in urls:
            order = asyncio.ensure_future(self.async_engine(url))
            orders.append(order)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.wait(orders))
        return [order.result() for order in orders]

    async def _place_order(self, urls: list, loop):
        self.token = self.get_token()
        # print(urls)
        orders = []
        for url in urls:
            order = asyncio.ensure_future(self.async_engine(url))
            orders.append(order)
        await asyncio.wait(orders, return_when=asyncio.ALL_COMPLETED, loop=loop)
        return [order.result() for order in orders]

    def get_positions(self, ccy='BTC', kind=None):
        """

        :param ccy: 'BTC' or 'ETH'
        :param kind: 'future' or 'option'
        :return:
        """
        if kind:
            return self.request("/api/v2/private/positions?currency={}&kind={}".format(ccy, kind))

        return self.request("/api/v2/private/positions?currency={}".format(ccy))

    def get_margin(self, ccy='BTC'):
        return self.request('/api/v2/private/get_account_summary?currency={}'.format(ccy))

    def get_order_info(self, order_id):
        return self.request('/api/v2/private/get_order_state?order_id={}'.format(order_id))

    def get_open_orders(self, ccy='BTC'):
        """

        :param ccy: BTC or ETH
        :return:
        """
        self.ccy = ccy
        result = self.request('/api/v2/private/get_open_orders_by_currency?currency={}'.format(self.ccy))
        return [res['order_id'] for res in result['result']]

    def tradeable_symbols(self, ccy='BTC', kind=None):
        """

        :param ccy: 'BTC' or 'ETH'
        :param type: 'future' or 'option'
        :return:
        """
        if kind:
            data = self.request('/api/v2/public/get_instruments?currency={}&kind={}'.format(ccy, kind))
            return sorted([x['instrument_name'] for x in data['result']])
        else:
            data = self.request('/api/v2/public/get_instruments?currency={}'.format(ccy))
            return sorted([x['instrument_name'] for x in data['result']])

    def get_order_book(self, instrument_name='BTC-PERPETUAL', depth=5):
        """

        :param instrument_name: 'BTC-PERPETUAL' or 'ETH-PERPETUAL'
        :param depth: 'future' or 'option'
        :return:
        """
        book = self.request('/api/v2/public/get_order_book?depth={}&instrument_name={}'.format(depth, instrument_name))[
            'result']
        return {'instrument_name': instrument_name, 'bid': book['bids'], 'ask': book['asks'],
                'timestamp': book['timestamp']}

    def get_tradingview_chart_data(self, instrumemt_name, start_timestamp, end_timestamp, resolution):
        result = self.request(
            '/api/v2/public/get_tradingview_chart_data?end_timestamp={}&instrument_name={}&resolution={}&start_timestamp={}'.format(
                end_timestamp, instrumemt_name, resolution, start_timestamp))
        return result

    def get_funding_chart_history_data(self, instrumemt_name, start_timestamp, end_timestamp):
        result = self.request(
            '/api/v2/public/get_funding_rate_history?end_timestamp={}&instrument_name={}&start_timestamp={}'.format(
                end_timestamp, instrumemt_name, start_timestamp))
        return result

    def get_funding_chart_data(self, instrumemt_name, length):
        result = self.request(
            '/api/v2/public/get_funding_chart_data?instrument_name={}&length={}'.format(instrumemt_name, length))
        return result

    def get_index_price(self, index):
        return self.request("/api/v2/public/get_index_price?index_name={}".format(index))['result']['index_price']

    def get_token(self):
        response = self.session.get(
            self.url + "/api/v2/public/auth?client_id={}&client_secret={}&grant_type=client_credentials".format(
                self.key, self.secret),
            headers={'Content-Type': 'application/json'})
        return response.json()['result']['access_token']

    def buy_limit(self, symbol, price, quantity, label=""):
        result = self.place_order(
            urls=[self.url + '/api/v2/private/buy?amount={}&instrument_name={}&price={}&label={}&type=limit'.format(
                str(quantity), symbol, str(price), label)]
        )
        return ["Deribit Buy {} {}@{} ID:{}".format(res['result']['order']['amount'],
                                                    res['result']['order']['instrument_name'],
                                                    res['result']['order']['price'],
                                                    res['result']['order']['order_id']) if 'result' in res else res
                for
                res in result]

    def sell_limit(self, symbol, price, quantity, label=""):
        result = self.place_order(
            urls=[
                self.url + '/api/v2/private/sell?amount={}&instrument_name={}&price={}&label={}&type=limit'.format(
                    str(quantity), symbol, str(price), label)]
        )
        return ["Deribit Sell {} {}@{} ID:{}".format(res['result']['order']['amount'],
                                                     res['result']['order']['instrument_name'],
                                                     res['result']['order']['price'],
                                                     res['result']['order']['order_id']) if 'result' in res else res
                for
                res in result]

    def sell_market(self, symbol, quantity, label=""):
        result = self.place_order(
            urls=[
                self.url + '/api/v2/private/sell?amount={}&instrument_name={}&label={}&type=market'.format(
                    str(quantity), symbol, label)]
        )
        # print(result)
        return ["Deribit Sell {} {}@{} ID:{}".format(res['result']['order']['amount'],
                                                     res['result']['order']['instrument_name'],
                                                     res['result']['order']['price'],
                                                     res['result']['order']['order_id']) if 'result' in res else res
                for
                res in result]

    def buy_market(self, symbol, quantity, label=""):
        result = self.place_order(
            urls=[
                self.url + '/api/v2/private/buy?amount={}&instrument_name={}&label={}&type=market'.format(
                    str(quantity), symbol, label)]
        )
        # print(result)
        return ["Deribit Sell {} {}@{} ID:{}".format(res['result']['order']['amount'],
                                                     res['result']['order']['instrument_name'],
                                                     res['result']['order']['price'],
                                                     res['result']['order']['order_id']) if 'result' in res else res
                for
                res in result]

    def buy_market_stop(self, symbol, quantity, stop_price, label=""):
        result = self.place_order(
            urls=[
                self.url + '/api/v2/private/buy?amount={}&instrument_name={}&label={}&type=stop_market&stop_price = {}'.format(
                    str(quantity), symbol, label, stop_price)]
        )
        # print(result)
        return ["Deribit Sell {} {}@{} ID:{}".format(res['result']['order']['amount'],
                                                     res['result']['order']['instrument_name'],
                                                     res['result']['order']['price'],
                                                     res['result']['order']['order_id']) if 'result' in res else res
                for
                res in result]

    def sell_market_stop(self, symbol, quantity, stop_price, label=""):
        result = self.place_order(
            urls=[
                self.url + '/api/v2/private/sell?amount={}&instrument_name={}&label={}&type=stop_market&stop_price = {}'.format(
                    str(quantity), symbol, label, stop_price)]
        )
        # print(result)
        return ["Deribit Sell {} {}@{} ID:{}".format(res['result']['order']['amount'],
                                                     res['result']['order']['instrument_name'],
                                                     res['result']['order']['price'],
                                                     res['result']['order']['order_id']) if 'result' in res else res
                for
                res in result]

    def buy_limit_batch(self, orders_info: list):

        urls = []
        # print(type(orders_info))
        for order in orders_info:
            urls.append(
                self.url + '/api/v2/private/buy?amount={}&instrument_name={}&price={}&label={}&type=limit'.format(
                    order['quantity'], order['symbol'], order['price'], order['label']
                ))
        result = self.place_order(urls=urls)
        # print(result)
        return ["Deribit Buy {} {}@{} ID:{}".format(res['result']['order']['amount'],
                                                    res['result']['order']['instrument_name'],
                                                    res['result']['order']['price'],
                                                    res['result']['order']['order_id']) if 'result' in res else res
                for
                res in result]

    def sell_limit_batch(self, orders_info: list):

        urls = []
        for order in orders_info:
            urls.append(
                self.url + '/api/v2/private/sell?amount={}&instrument_name={}&price={}&label={}&type=limit'.format(
                    order['quantity'], order['symbol'], order['price'], order['label']
                ))
        result = self.place_order(urls=urls)
        return ["Deribit Sell {} {}@{} ID:{}".format(res['result']['order']['amount'],
                                                     res['result']['order']['instrument_name'],
                                                     res['result']['order']['price'],
                                                     res['result']['order']['order_id']) if 'result' in res else res
                for
                res in result]

    async def _buy_limit_batch(self, orders_info: list, loop):

        urls = []
        # print(type(orders_info))
        for order in orders_info:
            urls.append(
                self.url + '/api/v2/private/buy?amount={}&instrument_name={}&price={}&label={}&type=limit'.format(
                    order['quantity'], order['symbol'], order['price'], order['label']
                ))
        result = await self._place_order(urls=urls, loop=loop)
        # (result)
        return ["Deribit Buy {} {}@{} ID:{}".format(res['result']['order']['amount'],
                                                    res['result']['order']['instrument_name'],
                                                    res['result']['order']['price'],
                                                    res['result']['order']['order_id']) if 'result' in res else res
                for
                res in result]

    async def _sell_limit_batch(self, orders_info: list, loop):
        urls = []
        for order in orders_info:
            urls.append(
                self.url + '/api/v2/private/sell?amount={}&instrument_name={}&price={}&label={}&type=limit'.format(
                    order['quantity'], order['symbol'], order['price'], order['label']
                ))
        result = await self._place_order(urls=urls, loop=loop)
        # print(result)
        return ["Deribit Sell {} {}@{} ID:{}".format(res['result']['order']['amount'],
                                                     res['result']['order']['instrument_name'],
                                                     res['result']['order']['price'], res['result']['order'][
                                                         'order_id']) if 'result' in res == 'open' else res for res
                in
                result]

    def cancel_all_order(self):
        return self.request('/api/v2/private/cancel_all?')

    def modify_order(self, orderID, price, amount):
        return self.request('/api/v2/private/edit?&amount={}&order_id={}&price={}'.format(amount, orderID, price))

    def _cancel(self, urls: list):
        self.token = self.get_token()
        orders = []
        for url in urls:
            order = asyncio.ensure_future(self.async_engine(url))
            orders.append(order)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.wait(orders))
        return [order.result() for order in orders]

    async def _cancelAync(self, urls: list, loop):
        self.token = self.get_token()
        # print(urls)
        orders = []
        for url in urls:
            order = asyncio.ensure_future(self.async_engine(url))
            orders.append(order)
        await asyncio.wait(orders, return_when=asyncio.ALL_COMPLETED, loop=loop)
        return [order.result() for order in orders]

    async def _cancel_batch_order(self, orders: list, loop):
        # print(orders)
        urls = []
        for order_id in orders:
            urls.append(self.url + "/api/v2/private/cancel?order_id={}".format(order_id))
        result = await self._cancelAync(urls, loop=loop)
        return ["Deribit Order {} cancelled".format(res['result']['order_id']) if res['result'][
                                                                                      'order_state'] == 'cancelled' else
                res['result'] for res in result]

    def cancel_order(self, order_id):
        result = self._cancel([self.url + "/api/v2/private/cancel?order_id={}".format(order_id)])
        return ["Deribit Order {} cancelled".format(res['result']['order_id']) if res['result'][
                                                                                      'order_state'] == 'cancelled' else
                res['result'] for res in result]

    def cancel_batch_order(self, orders: list):
        urls = []
        for order_id in orders:
            urls.append(self.url + "/api/v2/private/cancel?order_id={}".format(order_id))
        result = self._cancel(urls)
        return ["Deribit Order {} cancelled".format(res['result']['order_id']) if res['result'][
                                                                                      'order_state'] == 'cancelled' else
                res['result'] for res in result]

    def get_orders(self, count):
        return self.request('/api/v2/private/get_order_history_by_currency?count={}&currency=BTC'.format(count))
