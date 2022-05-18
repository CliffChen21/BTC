import sys

from config import Config

from huobi_api import HuobiFutureRestAPI

sys.argv.append("E:/Dropbox/source/projects/Bitcoin_Trading/configuration.json")
MyConfig = Config()
MyConfig.loads(sys.argv[1])

api = HuobiFutureRestAPI(MyConfig.accounts[0]['host'], MyConfig.accounts[0]['access_key'],
                         MyConfig.accounts[0]['secret_key'])  # host, access_key, secret_key
print(api.get_contract_info(symbol="BTC", contract_type="quarter"))
