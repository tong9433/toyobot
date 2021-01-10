# This Python file uses the following encoding: utf-8
import requests
from PyQt5.QtWidgets import QTableWidgetItem, QListWidgetItem
import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
import datetime

import pyupbit
from pyupbit import Upbit


class Disclosure:
    def __init__(self, window, parent):
        self.window = window
        self.parent = parent
        self.latest_disclosure = ""
        self.telegram_token = window.telegram_token
        self.telegram_id = window.telegram_id
        self.bot = telepot.Bot(self.telegram_token)
        self.access_key = window.access_key
        self.secret_key = window.secret_key
        self.upbit = Upbit(self.access_key, self.secret_key)
        self.target_coin = "KRW-BTC"

    def catch_new_disclosure(self, title, target_coin):
        coin_list = []
        for coin in self.parent.cur_krw_coin_list:
            coin_list.append(coin["market"])
        if target_coin in coin_list:
            keywords = title.split(" ")
            keyword = "없음"
            for word in keywords:
                if word in ["소각", "계약", "파트너십"]:
                    keyword = word
            self.target_coin = target_coin
            self.buying_msg(title, target_coin, keyword)

    def load_discolure(self):
        url = "https://project-team.upbit.com/api/v1/disclosure?region=kr&per_page=20"
        res = requests.request("GET", url)
        upbit_disclosure = res.json()["data"]["posts"]
        self.window.list_widget_disclosure.clear()
        for idx, unit in enumerate(upbit_disclosure):
            title = unit["text"]
            target_coin = "KRW-"+unit["assets"]
            if idx == 0:
                if self.latest_disclosure == "":
                    self.latest_disclosure = title
                    self.target_coin = target_coin
                else:
                    if self.latest_disclosure != title:
                        self.target_coin = target_coin
                        self.catch_new_disclosure(title, target_coin)
                        self.latest_disclosure = title
            self.window.list_widget_disclosure.addItem(QListWidgetItem(title))
        now = datetime.datetime.now().timestamp()
        time = datetime.datetime.fromtimestamp(int(now)).strftime('%Y-%m-%d %H:%M:%S')
        if int(time.split(":")[-1]) % 5 == 0:
            self.parent.logger.print_log("공시 리스트를 갱신합니다.")

    def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        self.bot.sendMessage(self.telegram_id, '완료')

    def on_callback_query(self, msg):
        query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
        if query_data == 'yes':
            my_account_KRW = self.upbit.get_balance(ticker="KRW")
            buy_money = my_account_KRW * 0.05
            respon = self.upbit.buy_market_order(self.target_coin, buy_money)
            self.bot.sendMessage(self.telegram_id, '자동 매수 완료')

    def buying_msg(self, title, target_coin, keyword):
        url = "https://api.upbit.com/v1/candles/days"
        querystring = {"market":target_coin,"count":"1"}
        response = requests.request("GET", url, params=querystring)
        info = response.json()[0]
        price_start = info["opening_price"]
        price_cur = info["trade_price"]
        percent = round(((price_cur - price_start) * 100) / price_start, 2)
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='자동매수', callback_data='yes',  callback_query=self.on_callback_query)]
        ])

        self.bot.sendMessage(
            self.telegram_id, '[공시알림] \n title : {}\n 코인명: {}\n keyword: {}\n 시작가: {}원\n 현재가: {}원\n 금일 퍼센트: {}%'.format(
                title, target_coin, keyword, str(price_start), str(price_cur), str(percent)), reply_markup=keyboard)
        MessageLoop(self.bot, {'chat': self.on_chat_message, 'callback_query': self.on_callback_query}).run_as_thread()
