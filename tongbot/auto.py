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
from order_upbit import OrderUpbit
from chat_selling import Sellchat
from cralwer import Cralwer
from logger import Logger

from pyupbit import Upbit
import pyupbit

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
        self.update_target_price()
        self.chat_bot = chatAPI(window)
        self.order_upbit = OrderUpbit(window)

    def init(self):
        self.cur_krw_coin_list = []
        self.start_krw_coin_list = []
        self.cur_anounce_coin_list = []
        self.target_market= "KRW-BTC"
        self.window.line_edit_cur_market_name.setText(self.target_market)
        self.test = False
        self.sell_time_limit = int(self.window.line_edit_sell_time.text())
        self.start_target_price = 1
        self.cur_target_price = 1
        self.sell_status = [True]

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
                self.check_mode()
            if status == "buy" or status == "sell":
                self.update_target_price()
            if status == "buy":
                self.buy_mode()
            if status == "sell":
                self.sell_mode()

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

        now = datetime.datetime.now().timestamp()
        time = datetime.datetime.fromtimestamp(int(now)).strftime('%Y-%m-%d %H:%M:%S')
        if int(time.split(":")[-1]) % 5 == 0:
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

    def check_mode(self):
        if self.check_create_new_coin():
            new_coin_market = self.search_new_coin(self)
            log = self.logger.print_log("새 원화 상장 코인 : {}".format(new_coin_market))
            self.chat_bot.send_to_me_telegram_message(log)
            self.auto_bot["new_krw_coin"] = "BTC-"+new_coin_market.split("-")[1]
            self.target_market = self.auto_bot["new_krw_coin"]
            self.window.line_edit_cur_market_name.setText(self.target_market)
            self.auto_bot["status"] = "buy"
            self.autobot_status_changed()

    def update_target_price(self):
        market = self.target_market
        self.cur_target_price = pyupbit.get_current_price(self.target_market)
        self.logger.print_log("[{}] 현재가 {}".format(
            self.auto_bot["new_krw_coin"], str(self.cur_target_price)))

    def buy_mode(self):
        if self.window.check_box_buy.isChecked():
            self.start_target_price = self.order_upbit.buy_btc(self.target_market)
            self.auto_bot["buy"] = True
        self.auto_bot["status"] = "sell"
        self.autobot_status_changed()

    def sell_mode(self):
        sell = Sellchat(self.window, self)
        sell.selling_msg()
        self.sell_time_limit -= 1
        self.logger.print_log("{}초 뒤에 시장가 매도 진행됩니다.".format(self.sell_time_limit))
        if self.sell_status[0] == False:
            if self.sell_status[1] == None:
                self.logger.print_log("자동매도 거부")
                self.auto_bot["status"] = "end"
                self.autobot_status_changed()
        else:
            # 목표 percent 도달 시 시장가 매도(default: 50%)
            if self.window.check_box_sell.isChecked():
                sell_percent = float(self.line_edit_sell_percent.text())
                if float(100 * (self.cur_target_price - self.start_target_price) / self.start_target_price) > sell_percent :
                    self.order_upbit.sell_btc(self.target_market)
                    self.auto_bot["status"] = "end"
                    self.autobot_status_changed()

            # 하락시 시장가 매도 (default: -10%)
            if float(100 * (self.cur_target_price - self.start_target_price) / self.start_target_price) < -10.0 :
                self.order_upbit.sell_btc(self.target_market)
                self.auto_bot["status"] = "end"
                self.autobot_status_changed()

            # 타임초과 시 시장가 매도 (default: 90초)
            if self.sell_time_limit < 0:
                self.order_upbit.sell_btc(self.target_market)
                self.auto_bot["status"] = "end"
                self.autobot_status_changed()

    def test_btn_clicked(self):
        self.test =True
        # test 1 : krw 코인 증가
        #self.cur_krw_coin_list.append(
        #    {'market': 'KRW-ONIT', 'korean_name': '온버프', 'english_name': 'onbuf'}
        #)

        # tes 2 : 공지사항 등록
        self.cur_anounce_coin_list.append("KRW-SAND")

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
        now = datetime.datetime.now().timestamp()
        time = datetime.datetime.fromtimestamp(int(now)).strftime('%Y-%m-%d %H:%M:%S')
        if int(time.split(":")[-1]) % 5 == 0:
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
