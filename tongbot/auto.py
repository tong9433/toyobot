# This Python file uses the following encoding: utf-8

import requests
from bs4 import BeautifulSoup
from PyQt5.QtWidgets import QTableWidgetItem, QListWidgetItem

import threading

from PyQt5.QtCore import Qt
from PyQt5.QtCore import QThread
from PyQt5.QtCore import QWaitCondition
from PyQt5.QtCore import QMutex
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import pyqtSlot

import datetime
from chatAPI import chatAPI
from cralwer import Cralwer
from logger import Logger

class Thread(QThread):
    signal_update = pyqtSignal()

    def __init__(self, window):
        QThread.__init__(self)
        self.cond = QWaitCondition()
        self.mutex = QMutex()
        self.cnt = 0
        self._status = True
        self.window = window
        self.logger = Logger(window)

    def __del__(self):
        self.wait()

    def run(self):
        while True:
            self.mutex.lock()
            if not self._status:
                self.cond.wait(self.mutex)
            # self.logger.print_log("working auto bot")
            self.msleep(1000)  # ※주의 QThread에서 제공하는 sleep을 사용
            self.signal_update.emit()
            self.mutex.unlock()

    def toggle_status(self):
        self._status = not self._status
        if self._status:
            self.cond.wakeAll()

    @property
    def status(self):
        return self._status

class Auto:
    def __init__(self, window):
        self.window = window
        self.test = False
        self.init()
        self.logger = Logger(window)
        self.auto_thread =Thread(window)
        self.auto_thread.start()
        self.init_auto_bot()
        self.connect_signal()
        self.update_table_widget_market_info()
        self.chat_bot = chatAPI()

    def init(self):
        self.cur_krw_coin_list = []
        self.start_krw_coin_list = []
        self.cur_anounce_coin_list = []
        self.target_market= "KRW-BTC"
        self.window.line_edit_cur_market_name.setText(self.target_market)
        self.test = False

    def connect_signal(self):
        self.auto_thread.signal_update.connect(self.update)

    def update(self):
        try:
            status = self.auto_bot["status"]
            # self.window.update_account_btn_clicked()
            # self.window.order.get_order_info()
            if status == "stop" or status == "start":
                self.load_api_krw_coin()
            if status == "start":
                self.load_upbit_annoucement()
                self.check_cnt_krw_coin()
            if status == "buy":
                self.update_table_widget_market_info()

        except Exception as e:
            self.logger.print_log(str(e))

    def search_new_coin(self, txt):
        start_krw_list = []
        for coin in self.start_krw_coin_list:
            start_krw_list.append(coin["market"])

        for coin in self.cur_krw_coin_list:
            if not coin["market"] in start_krw_list:
                return coin["market"]

        for announce_coin in self.cur_anounce_coin_list:
            if not announce_coin in start_krw_list:
                return announce_coin

    def load_upbit_annoucement(self):
        # 테스트 시에만 사용하는 코드
        if self.test == True:
            return
        self.window.list_widget_announce.clear()
        url = "https://api-manager.upbit.com/api/v1/notices?page=1&per_page=20&thread_name=general"
        res = requests.request("GET", url)
        upbit_announcement = res.json()["data"]["list"]

        for idx, unit in enumerate(upbit_announcement):
            parsed_list = unit["title"].split(" ")
            self.window.list_widget_announce.addItem(QListWidgetItem(unit["title"]))
            if parsed_list[0] == "[거래]" and parsed_list[1] == "원화":
                self.cur_anounce_coin_list.append("KRW-{}".format(parsed_list[-1][0:-1]))
        self.logger.print_log("공지사항 리스트를 갱신합니다.")

    def check_create_new_coin(self):
        signal = ""
        self.auto_bot["cnt_cur_krw_coin"] = len(self.cur_krw_coin_list)
        if self.auto_bot["cnt_cur_krw_coin"] > self.auto_bot["cnt_start_krw_coin"]:
            signal = " [개수증가] "
            log = self.logger.print_log("{}: 원화상장 시그널이 포착되었습니다. 구매단계로 전환합니다.".format(signal))
            self.chat_bot.send_to_me_telegram_message(log)
            return True
        cur_krw_market_list = []
        for coin in self.cur_krw_coin_list:
            cur_krw_market_list.append(coin["market"])

        for anounce_coin in self.cur_anounce_coin_list:
            if not anounce_coin in cur_krw_market_list:
                signal = " [공지] "
                log = self.logger.print_log("{}: 원화상장 시그널이 포착되었습니다. 구매단계로 전환합니다.".format(signal))
                self.chat_bot.send_to_me_telegram_message(log)
                return True

        return False

    def check_cnt_krw_coin(self):
        if self.check_create_new_coin():
            self.auto_bot["status"] = "buy"
            # Todo
            #1. 해당 코인이 뭔지 찾기 "buy"
            new_coin_market = self.search_new_coin(self)
            log = self.logger.print_log("새 원화 상장 코인 : {}".format(new_coin_market))
            self.chat_bot.send_to_me_telegram_message(log)
            self.auto_bot["new_krw_coin"] = "BTC-"+new_coin_market.split("-")[1]
            self.target_market = self.auto_bot["new_krw_coin"]
            self.window.line_edit_cur_market_name.setText(self.target_market)

            #2. 해당 코인 구매 여부 확인 "buy"
            #3. 구매 "buy"
            #4. 카카오톡 알림 "sell
            #5. 매도 "sell"
            #6. stop "stop"

#            self.auto_bot["buy"] = True
        self.autobot_status_changed()

    def test_btn_clicked(self):
        self.test =True
        # test 1 : krw 코인 증가
        #self.cur_krw_coin_list.append(
        #    {'market': 'KRW-ONIT', 'korean_name': '온버프', 'english_name': 'onbuf'}
        #)

        # tes 2 : 공지사항 등록
        self.cur_anounce_coin_list.append("KRW-ONIT")

    def update_table_widget_market_info(self):
        try:
            market = self.target_market
            url = "https://api.upbit.com/v1/candles/minutes/1"
            querystring = {"market":market,"count":"1"}
            res = requests.request("GET", url, params=querystring)
            print(res.text)
            coin_minitue_candle = res.json()[0]
            info_trade_price = coin_minitue_candle["trade_price"]
            info_high_price = coin_minitue_candle["high_price"]
            info_low_price = coin_minitue_candle["low_price"]
            info_candle_acc_trade_price = round(coin_minitue_candle["candle_acc_trade_price"], 1)
            self.window.label_info_0.setText(str(info_trade_price))
            self.window.label_info_1.setText(str(info_low_price))
            self.window.label_info_2.setText(str(info_high_price))
            self.window.label_info_3.setText(str(info_candle_acc_trade_price))
            # 현재가 정보
            url = "https://api.upbit.com/v1/ticker"
            querystring = {"markets": market}
            res = requests.request("GET", url, params=querystring)

            coin_cur_info = res.json()[0]
            info_change = coin_cur_info["change"]
            info_signed_change_price = coin_cur_info["signed_change_price"]
            info_signed_change_rate = round(coin_cur_info["signed_change_rate"] * 100,3)
            info_trade_volume = coin_cur_info["trade_volume"]
            info_prev_closing_price = coin_cur_info["prev_closing_price"]
            self.window.label_info_4.setText(str(info_change))
            self.window.label_info_5.setText(str(info_signed_change_price))
            self.window.label_info_6.setText(str(info_signed_change_rate)+" %")
            self.window.label_info_7.setText(str(info_trade_volume))
            self.window.label_info_8.setText(str(info_prev_closing_price))
            if self.auto_bot["status"] == "buy":
                self.logger.print_log("[{}] 현재가: {} 변화율: {}".format(
                self.auto_bot["new_krw_coin"], str(coin_minitue_candle["trade_price"]), str(info_signed_change_rate)+" %"))


            # 최근 체결 내역
#            url = "https://api.upbit.com/v1/trades/ticks"
#            querystring = {
#                "market":market,
#                "count":"100"
#            }
#            res = requests.request("GET", url, params=querystring)
#            list_trade = res.json()
#            sum = 0
#            for a in list_trade:
#                sum += a["trade_volume"]
#            print(time)
#            print(list_trade[0])
#            print(list_trade[1])
#            print(list_trade[2])
#            print(list_trade[3])
#            print(list_trade[4])
#            self.logger.print_log(res.json)

        except Exception as e :
            self.logger.print_log("제대로 된 코인 마켓명을 적으세요")
            self.logger.print_log(e)

    def init_auto_bot(self):
        self.auto_bot = {
            "status": "stop",
            "buy":False,
            "cnt_start_krw_coin": 0,
            "cnt_cur_krw_coin": 0,
            "new_krw_coin": ""
        }

    def load_api_krw_coin(self):
        # 테스트 시에만 사용하는 코드
        if self.test == True:
            return

        self.cur_krw_coin_list = []
        url = "https://api.upbit.com/v1/market/all"
        querystring = {"isDetails":"false"}
        response = requests.request("GET", url, params=querystring)
        all = response.json()
        cnt_krw_coin = 0
        for coin in all:
            market = coin["market"]
            korean_name = coin["korean_name"]
            english_name = coin["english_name"]
            if coin["market"].split("-")[0] != "KRW":
                continue
            self.cur_krw_coin_list.append(coin)
            cnt_krw_coin = cnt_krw_coin + 1
        self.window.table_widget_api.setColumnCount(3)
        self.window.table_widget_api.setRowCount(cnt_krw_coin)
        for idx, coin in enumerate(self.cur_krw_coin_list) :
            self.window.table_widget_api.setItem(idx, 0, QTableWidgetItem(coin["market"]))
            self.window.table_widget_api.setItem(idx, 1, QTableWidgetItem(coin["korean_name"]))
            self.window.table_widget_api.setItem(idx, 2, QTableWidgetItem(coin["english_name"]))
        self.window.table_widget_api.resizeColumnsToContents()
        self.window.table_widget_api.resizeRowsToContents()
        self.window.label_cnt_api.setText(str(cnt_krw_coin) + "개")
        self.logger.print_log("원화 상장 리스트를 갱신합니다.")

    def autobot_status_changed(self):
        self.window.label_status.setText(self.auto_bot["status"])
        self.window.label_start_cnt.setText(str(self.auto_bot["cnt_start_krw_coin"]))
        self.window.label_cur_cnt.setText(str(self.auto_bot["cnt_cur_krw_coin"]))
        self.window.label_flag_buy.setText(str(self.auto_bot["buy"]))
        self.window.label_new_coin.setText(str(self.auto_bot["new_krw_coin"]))

    def start_btn_clicked(self):
        self.start_krw_coin_list = self.cur_krw_coin_list
        self.auto_bot["status"] = "start"
        self.auto_bot["cnt_start_krw_coin"] = len(self.start_krw_coin_list)
        self.window.btn_start.setEnabled(False)
        self.window.btn_stop.setEnabled(True)
        self.autobot_status_changed()

    def stop_btn_clicked(self):
        self.init()
        self.auto_bot["status"] = "stop"
        self.window.btn_start.setEnabled(True)
        self.window.btn_stop.setEnabled(False)
        self.init_auto_bot()
        self.autobot_status_changed()



