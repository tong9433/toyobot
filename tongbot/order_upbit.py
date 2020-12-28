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

    def buy_btc(self, market_name):
        server_url = 'https://api.upbit.com/v1/orders'
        upbit = Upbit(self.access_key, self.secret_key)
        my_account_btc = upbit.get_balance(ticker="KRW-BTC")
        buy_money = my_account_btc * 0.99 # 내가 가진 btc
        respon = upbit.buy_market_order(market_name, buy_money)
        cur_price = pyupbit.get_current_price(market_name)

        self.logger.print_log(
            "[{} 체결완료] : 금액: {}".format(market_name, cur_price))
        return cur_price


    #def sell_btc(market_name, rising_percent, sell_percent):
    ##    '구매 가격 * (1+rising_percent) > 현재가격' 의 경우
    ##    현재 보유 market_name 지분에서 sell_percent로 판매

    ######지정가 매도도 가능하고, while로 돌면서 계속 추이를 볼수 있다.
    #    server_url = 'https://api.upbit.com/v1/orders'
    #    upbit = Upbit(self.access_key, self.secret_key)
    #    my_account_btc = upbit.get_balance(ticker=market_name)
    #    while True:
    #        time.sleep(0.5)
    #        cur_price = pyupbit.get_current_price(market_name)
    #        if buy_price * (1+rising_percent) < cur_price:
    #            upbit.sell_market_order(market_name, my_account_btc*sell_percent)
    #    print("체결이 완료됐습니다")

    ## 지정가 매도의 경우.
    def sell_btc(self, market_name, rising_percent, sell_percent, buy_price):
    #    '구매 가격 * (1+rising_percent) > 현재가격' 의 경우
    #    현재 보유 market_name 지분에서 sell_percent로 판매
        server_url = 'https://api.upbit.com/v1/orders'
        upbit = Upbit(self.access_key, self.secret_key)
        my_account_btc = upbit.get_balance(ticker=market_name)
        print(upbit.sell_limit_order(market_name, float(buy_price) * (1+rising_percent) , my_account_btc*sell_percent))
        print("지정가 매도 시작했습니다.")





