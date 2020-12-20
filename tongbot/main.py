# This Python file uses the following encoding: utf-8
import sys
import os

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem
from PyQt5.QtCore import QFile

form_class = uic.loadUiType("form.ui")[0]

import os
import jwt
import uuid
import hashlib
from urllib.parse import urlencode

import requests
from auto import Auto
from order import Order

class Main(QMainWindow, form_class):
    def __init__(self):
        super(Main, self).__init__()
        self.setupUi(self)
        self.order = Order(self)
        self.auto_bot = Auto(self)
        self.connect_signal()

    def init(self):
        url = "https://api.upbit.com/v1/market/all"
        querystring = {"isDetails":"false"}
        res = requests.request("GET", url, params=querystring)
        self.coin_dict = res.json()

    def connect_signal(self):
        self.btn_start.clicked.connect(self.auto_bot.start_btn_clicked)
        self.btn_stop.clicked.connect(self.auto_bot.stop_btn_clicked)
        self.btn_account_update.clicked.connect(self.update_account_btn_clicked)
        self.btn_set_key.clicked.connect(self.set_key_btn_clicked)
        self.btn_test.clicked.connect(self.auto_bot.test_btn_clicked)

    def update_account_btn_clicked(self):
        self.set_key_btn_clicked()
        self.init_acount()

    def set_key_btn_clicked(self):
        self.access_key = self.line_edit_access_key.text()
        self.secret_key = self.line_edit_secret_key.text()


    def init_acount(self):
        server_url = 'https://api.upbit.com'

        payload = {
            'access_key': self.access_key,
            'nonce': str(uuid.uuid4()),
        }

        jwt_token = jwt.encode(payload, self.secret_key).decode('utf-8')
        authorize_token = 'Bearer {}'.format(jwt_token)
        headers = {"Authorization": authorize_token}

        res = requests.get(server_url + "/v1/accounts", headers=headers)

        a = res.json()

        self.table_account.setRowCount(len(a) + 1)
        self.table_account.setColumnCount(9)

        account_sum_price = 0;
        for i, coin in enumerate(a):
            coin_name = coin["currency"]
            balence = float(coin["balance"])
            locked = float(coin["locked"])
            avg_buy_price = float(coin["avg_buy_price"])
            cnt_sum = balence + locked
            if coin_name in ['HORUS', 'ADD', 'MEETONE', 'CHL', 'BLACK']:
                continue
            self.table_account.setItem(i, 0, QTableWidgetItem(coin_name))
            self.table_account.setItem(i, 1, QTableWidgetItem(format(balence, ",")))
            self.table_account.setItem(i, 2, QTableWidgetItem(format(locked, ",")))
            self.table_account.setItem(i, 3, QTableWidgetItem(format(avg_buy_price, ",")))
            self.table_account.setItem(i, 4, QTableWidgetItem(coin["unit_currency"]))
            if coin_name == "KRW":
                self.table_account.setItem(i, 6, QTableWidgetItem(format(int(cnt_sum), ",") + " 원"))
                account_sum_price += int(cnt_sum)
            else:
                cur_price = float(self.check_coin_candle(coin_name)["trade_price"])
                profit_price = int((cur_price - avg_buy_price) * cnt_sum)
                profit_ratio = round((cur_price / avg_buy_price - 1.0), 8) * 100
                sum_price = int(int(cur_price) * cnt_sum)
                self.table_account.setItem(i, 5, QTableWidgetItem(format(int(cur_price), ",")+" 원"))
                self.table_account.setItem(i, 6, QTableWidgetItem(format(sum_price, ",")+" 원"))
                self.table_account.setItem(i, 7, QTableWidgetItem(format(profit_ratio, ",")+" %"))
                self.table_account.setItem(i, 8, QTableWidgetItem(format(profit_price, ",")+" 원"))
                account_sum_price += sum_price

        self.table_account.setItem(len(a), 0, QTableWidgetItem("총 평가 금액"))
        self.table_account.setItem(len(a), 1, QTableWidgetItem(str(format(account_sum_price, ",")) + "원"))
        self.table_account.resizeColumnsToContents()
        self.table_account.resizeRowsToContents()


    def check_coin_candle(self, coin_name):
        url = "https://api.upbit.com/v1/candles/minutes/1"
        querystring = {"market":"KRW-" + coin_name,"count":"1"}
        res = requests.request("GET", url, params=querystring)

        return res.json()[0]



if __name__ == "__main__":
    app = QApplication([])
    widget = Main()
    widget.show()
    sys.exit(app.exec_())
