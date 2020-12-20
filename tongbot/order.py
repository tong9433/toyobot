# This Python file uses the following encoding: utf-8
import requests
from PyQt5.QtWidgets import QListWidgetItem
from PyQt5.QtGui import QBrush, QColor

import os
import jwt
import uuid
import hashlib
from urllib.parse import urlencode

import time

class Order:
    def __init__(self, window):
        self.window = window

    def get_order_info(self):
        market = self.window.line_order_coin_name.text()
        url = "https://api.upbit.com/v1/orderbook"
        querystring = {"markets":market}
        res = requests.request("GET", url, params=querystring)
        order_book = res.json()[0]["orderbook_units"]
        self.window.list_sell_order.clear()
        self.window.list_buy_order.clear()

        # 체결 정보
        url = "https://api.upbit.com/v1/trades/ticks"
        querystring = {"market":market,"count":"1"}
        res = requests.request("GET", url, params=querystring)
        cur_info = res.json()[0]
        cur_price = cur_info["trade_price"]
        ask_bid = cur_info["ask_bid"]

        for idx, unit in enumerate(order_book):
            sell_item = QListWidgetItem("{}    {}".format(unit["ask_price"], round(unit["ask_size"], 1)))
            buy_item = QListWidgetItem("{}     {}".format(unit["bid_price"], round(unit["bid_size"], 1)))

            if ask_bid == "BID":
               if unit["ask_price"] == cur_price :
                   sell_item.setBackground(QBrush(QColor("green")))
            elif ask_bid == "ASK":
               if unit["bid_price"] == cur_price :
                   buy_item.setBackground(QBrush(QColor("green")))

            self.window.list_sell_order.addItem(sell_item)
            self.window.list_buy_order.addItem(buy_item)

