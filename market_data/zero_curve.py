from tools.deribit_api import Deribit


class ZeroCurve:

    def __init__(self, Tokens, ccy="BTC"):
        self.drb_api = Deribit(Tokens)
        self.symbs = self.drb_api.tradeable_symbols(ccy=ccy, kind="future")
        self.ccy = ccy

    @classmethod
    def get_price_from_orderbook(cls, orderbook):
        return (orderbook['bid'][0][0] + orderbook['ask'][0][0]) / 2

    def get_market_price(self):
        mkt_price = dict()
        for symb in self.symbs:
            price = ZeroCurve.get_price_from_orderbook(self.drb_api.get_order_book(symb))
            mkt_price[symb] = price
        mkt_price[self.ccy] = self.drb_api.get_index_price("{}_usd".format(self.ccy.lower()))['result']['index_price']

        return mkt_price

    def cal_market_zc_rate(self):
        raise NotImplementedError


if __name__ == '__main__':
    Tokens = {}
    print(ZeroCurve(Tokens).get_market_price())
