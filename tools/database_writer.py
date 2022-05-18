import asyncio

from sqlalchemy import String

from exchange_api.deribit_api import Deribit
from tools.mysql_api import SQLEngine


class DataBaseWriter:
    def __init__(self, instrument_name="BTC-PERPETUAL", Tokens=None, table_name="deribit_btc_perpetual_tick"):
        self.MAX_COUNT_IN_MINUTES = 5 * 60
        self.data = []
        self.depth = 5
        self.client = Deribit(Tokens)
        self.db = SQLEngine()
        self.table_name = table_name
        self.instrument_name = instrument_name
        self.columns_info = {
            'columns': {**{'id': String(255)}, **{'bid_{}'.format(i + 1): String(255) for i in range(self.depth)},
                        **{'bid__vol_{}'.format(i + 1): String(255) for i in range(self.depth)},
                        **{'ask_{}'.format(i + 1): String(255) for i in range(self.depth)},
                        **{'ask__vol_{}'.format(i + 1): String(255) for i in range(self.depth)}}, 'primary_key': 'id'}

    def create_table(self):
        self.db.execute("DROP TABLE IF EXISTS {}".format(self.table_name))
        return self.db.create_table(self.table_name, self.columns_info)

    async def store_ticks_to_sqldb(self, count=0):
        # When more exchange involved, just change self.__data_from_deribit()
        if count == 0:
            self.data = []
        if count == self.MAX_COUNT_IN_MINUTES:
            self.db.insert(self.data, self.db.get_table(self.table_name))
        else:
            data_slice = await self.__data_from_deribit()
            self.data.append(data_slice)
            await self.store_ticks_to_sqldb(count + 1)

    def start_record(self):
        loop = asyncio.new_event_loop()
        loop.run_until_complete(self.store_ticks_to_sqldb(0))

    async def __get_order_book_from_deribit(self):
        rs = self.client.get_order_book(self.instrument_name, self.depth)
        return rs

    async def __data_from_deribit(self):
        order_book = await self.__get_order_book_from_deribit()
        data_slice = [order_book['timestamp'],
                      *[str(order_book['bid'][i][0]) for i in range(self.depth)],
                      *[str(order_book['bid'][i][1]) for i in range(self.depth)],
                      *[str(order_book['ask'][i][0]) for i in range(self.depth)],
                      *[str(order_book['ask'][i][1]) for i in range(self.depth)]]
        keys = list(self.columns_info['columns'].keys())
        return {keys[i]: data_slice[i] for i in range(len(keys))}
