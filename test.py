#!/usr/bin/python3
import json
import time
import unittest

from sqlalchemy import Integer, String

from exchange_api.deribit_api import Deribit
from tools.database_writer import DataBaseWriter
from tools.mysql_api import SQLEngine


class Test(unittest.TestCase):

    def setUp(self) -> None:
        with open("Tokens.json", 'r') as f:
            self.Tokens = json.load(f)
        self.depth = 5

    def test_mysql_api(self):
        columns_info = {'columns': {'id': Integer, 'name': String(255)},
                        'primary_key': 'id'}
        db = SQLEngine()
        table = db.create_table('test', columns_info)
        data = [
            {'id': 1, 'name': 'jack@yahoo.com'},
            {'id': 1, 'name': 'jack@msn.com'},
            {'id': 2, 'name': 'www@www.org'},
            {'id': 2, 'name': 'wendy@aol.com'},
        ]
        db.insert(data, table)
        sql = 'SELECT * FROM test'
        rs = db.execute(sql)
        for row in rs:
            print(row)
        db.get_table("test")
        db.execute("DROP TABLE IF EXISTS test")

    def test_deribit_api(self):
        client = Deribit(self.Tokens)
        instrument_name = "BTC-PERPETUAL"
        result = client.get_order_book(instrument_name, self.depth)
        print(result)

    def test_database_writer(self):
        table_name = "test_deribit_perpetual"
        db_writer = DataBaseWriter(Tokens=self.Tokens, table_name=table_name)
        db_writer.create_table()
        db_writer.start_record()
        time.sleep(5)
        db = SQLEngine()
        db.execute("DROP TABLE IF EXISTS {}".format(table_name))


if __name__ == '__main__':
    unittest.main()
