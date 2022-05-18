from sqlalchemy import create_engine, Table, Column, MetaData


class Config:
    # enter your server IP address/domain name
    HOST = "192.168.0.242"  # or "domain.com"
    # HOST = "localhost"
    # database name, if you want just to connect to MySQL server, leave it empty
    DATABASE = "deribit_db"
    # this is the user you create
    USER = ""
    # user password
    PASSWORD = ""


# sqlEngine =create_engine('mysql+pymysql://{}:{}@{}/{}'.format(USER,PASSWORD,HOST,DATABASE))
# dbConnection = sqlEngine.connect()


class SQLEngine:

    def __init__(self):
        self.db_engine = create_engine(
            'mysql+pymysql://{}:{}@{}/{}'.format(Config.USER, Config.PASSWORD, Config.HOST, Config.DATABASE))

    def connection(self):
        return self.db_engine.connect()

    def get_table(self, table_name):
        metadata = MetaData(bind=self.db_engine, reflect=True)
        return metadata.tables[table_name]

    def create_table(self, table_name=None, columns_info=None):
        metadata = MetaData()
        [Column(key, item, primary_key=False) if key != columns_info['primary_key'] else Column(key, item,
                                                                                                primary_key=True) for
         key, item in columns_info['columns'].items()]
        table = Table(*[table_name, metadata] + [Column(key, item) for key, item in columns_info['columns'].items()])
        metadata.create_all(self.db_engine)
        return table

    def insert(self, data=None, table=None):
        self.connection().execute(table.insert(), data)
        self.connection().close()

    def execute(self, sql=None):
        with self.connection() as con:
            rs = con.execute(sql)
        return rs
