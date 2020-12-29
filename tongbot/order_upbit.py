import os
import jwt
import uuid
import hashlib
import time
from urllib.parse import urlencode

import requests
import pyupbit
from pyupbit import Upbit
from logger import Logger

from pyupbit import Upbit


class OrderUpbit:
    def __init__(self, window):
        self.logger = Logger(window)
        self.access_key = window.access_key
        self.secret_key = window.secret_key
        self.upbit = Upbit(self.access_key, self.secret_key)

    def buy_btc(self, market_name):
        server_url = 'https://api.upbit.com/v1/orders'
        my_account_btc = self.upbit.get_balance(ticker="KRW-BTC")
#        buy_money = my_account_btc * 0.99 # 내가 가진 btc
        buy_money = 0.001 # 내가 가진 btc
#        respon = upbit.buy_market_order(market_name, buy_money)
        cur_price = pyupbit.get_current_price(market_name)

        self.logger.print_log(
            "[{} 체결완료] : 금액: {}".format(market_name, cur_price))
        return cur_price

    def sell_btc(self, market_name):
        server_url = 'https://api.upbit.com/v1/orders'
        my_account_btc = self.upbit.get_balance(ticker=market_name)
#        self.upbit.sell_market_order(market_name, my_account_btc)



